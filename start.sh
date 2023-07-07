#!/bin/bash
app="pyturf.app"
docker build -t ${app} .
docker run -d -p 8765:80 \
  --name=${app} \
  -v $PWD:/app ${app}