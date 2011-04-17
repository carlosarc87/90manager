#!/bin/sh
echo "Limpiando .pyc del proyecto"
pwd
find . -type f -name "*.pyc" -delete
