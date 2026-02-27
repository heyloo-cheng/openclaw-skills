---
name: deploy-reviewer
description: Reviews CI/CD configs, Dockerfiles, and deployment manifests for risks and best practices. Use when reviewing infrastructure or deployment changes.
---

# Deploy Reviewer

Evaluates deployment-related changes for risk, security, and best practices.

## When NOT to Use This Skill

- For application code review (use code-review-router)
- For initial project setup (no baseline to compare)

## Step 0: Detect Deployment Files

```bash
git --no-pager diff --name-only HEAD 2>/dev/null | grep -iE "(docker|compose|k8s|kubernetes|helm|terraform|\.github/workflows|Jenkinsfile|\.gitlab-ci|deploy|infra|\.env)" || echo "NO_DEPLOY_FILES"
```

**If no deployment files changed:** "No deployment-related changes detected."

## Step 1: Classify Change Type

| Category | Files | Risk Base |
|----------|-------|-----------|
| Container | `Dockerfile*`, `docker-compose*`, `.dockerignore` | Medium |
| CI/CD | `.github/workflows/*`, `Jenkinsfile`, `.gitlab-ci.yml` | Medium |
| Orchestration | `k8s/`, `helm/`, `*.yaml` (k8s manifests) | High |
| Infrastructure | `terraform/`, `*.tf`, `pulumi/`, `cdk/` | Critical |
| Secrets/Env | `.env*`, `*secret*`, `*credential*` | Critical |
| Deploy scripts | `deploy.sh`, `scripts/deploy*` | High |

## Step 2: Risk Scoring

Initialize `risk_score = 0`:

| Condition | Points |
|-----------|--------|
| Secrets/env files changed | +5 |
| Infrastructure (Terraform/CDK) changed | +4 |
| Production config modified | +4 |
| K8s resource limits changed | +3 |
| Docker base image changed | +3 |
| CI/CD pipeline modified | +2 |
| Port/network config changed | +2 |
| Health check modified | +2 |
| Replica count changed | +1 |

| Score | Risk Level |
|-------|------------|
| ≥ 8 | Critical — manual review required |
| 5-7 | High — careful automated review |
| 2-4 | Medium — standard review |
| 0-1 | Low — quick check |

## Step 3: Execute Review

### Low/Medium Risk
```bash
opencode run "Review these deployment config changes for: 1) Security issues (exposed secrets, privileged containers), 2) Resource misconfigs, 3) Best practices. Be specific."
```

### High/Critical Risk
```bash
git --no-pager diff HEAD -- <deploy-files> | claude -p "Review these deployment changes for: 1) Security vulnerabilities, 2) Breaking changes, 3) Resource limits, 4) Rollback safety, 5) Secret exposure. Flag anything that could cause downtime."
```

## Step 4: Checklist Output

```
## Deploy Review

**Risk Level:** [Low/Medium/High/Critical]
**Files:** [list]

**Security:** [PASS/WARN/FAIL]
- [ ] No secrets in plain text
- [ ] No privileged containers
- [ ] Base images pinned to digest

**Reliability:** [PASS/WARN/FAIL]
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Rollback strategy exists

**Issues found:** [list or "None"]
```
