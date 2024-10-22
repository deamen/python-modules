#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <module_name>"
  exit 1
fi

module=$1

cd $module || { echo "Module $module not found"; exit 1; }
python -m build
twine upload dist/*
cd ..