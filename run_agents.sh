#!/bin/bash

source .venv/bin/activate

LOG_FILE="agents_log.txt"

> $LOG_FILE

python src/trump_agent.py >> $LOG_FILE 2>&1 &
HARIS_PID=$!

sleep 5

python src/haris_agent.py >> $LOG_FILE 2>&1 &
TRUMP_PID=$!

tail -f $LOG_FILE &
TAIL_PID=$!

trap 'kill $HARIS_PID $TRUMP_PID $TAIL_PID; exit' INT

while true; do
    sleep 1
done