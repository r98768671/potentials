#!/bin/bash
cd pyiron-resources
git add -A
git commit -m  "$1" 
git push
