#!/bin/bash
branch=$1
git stash
git pull
git checkout $branch
git pull
