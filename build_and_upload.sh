#!/bin/bash

for module in hashi_vault
do
  cd $module
  python -m build
  twine upload dist/*
  cd ..
done