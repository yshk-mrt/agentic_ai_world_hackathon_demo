#!/bin/bash

source .venv/bin/activate

LOG_FILE="agents_log.txt"

> $LOG_FILE

python src/trump_agent.py >> $LOG_FILE 2>&1 &
HARIS_PID=$!

python src/harris_agent.py >> $LOG_FILE 2>&1 &
TRUMP_PID=$!

sleep 10

python src/moderation_agent.py >> $LOG_FILE 2>&1 &
MODERATION_PID=$!

tail -f $LOG_FILE &
TAIL_PID=$!

trap 'kill $HARIS_PID $TRUMP_PID $MODERATION_PID $TAIL_PID; exit' INT

while true; do
    sleep 1
done