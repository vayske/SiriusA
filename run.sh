#!/bin/bash
sirius_dir=$(dirname $0)

mkdir -p logs

cd $sirius_dir/sirius
message=
while true; do
    python3 sirius.py $message
    rc=$?
    if [ $rc -eq 0 ]; then
        exit $rc
    elif [ $rc -ge 2 ]; then
        branch=$(git branch --show-current)
        message="$rc $branch"
        continue
    fi
done
