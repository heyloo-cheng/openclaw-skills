#!/bin/bash
# 闲鱼监控 - 状态查询

WORKSPACE=~/.openclaw/workspace
SCRIPTS_DIR=$WORKSPACE/scripts

cd $SCRIPTS_DIR
bash manage-dropship.sh status
