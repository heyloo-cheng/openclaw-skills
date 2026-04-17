#!/bin/bash
# 闲鱼监控 - 停止命令

WORKSPACE=~/.openclaw/workspace
SCRIPTS_DIR=$WORKSPACE/scripts

cd $SCRIPTS_DIR
bash manage-dropship.sh stop
