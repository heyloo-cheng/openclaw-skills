#!/bin/bash
# 闲鱼监控 - 查看日志

WORKSPACE=~/.openclaw/workspace
SCRIPTS_DIR=$WORKSPACE/scripts

cd $SCRIPTS_DIR
bash manage-dropship.sh logs
