#!/bin/sh

ENDPOINT=`cat /etc/10xeng.yaml | grep "endpoint" | awk {'print $2;'}`

export MICROCLOUD=$ENDPOINT

cd /opt/gateone
./gateone.py
