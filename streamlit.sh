#!/usr/bin/env bash

export HOME=$PWD/src
export TMP=$PWD/tmp
export LOGS=$PWD/logs
export DOCS=$PWD/docs
export PYTHONPATH=$PWD/src

mkdir -p $HOME
mkdir -p $TMP
mkdir -p $LOGS
mkdir -p $DOCS

cd src/frontend/
streamlit run Home.py --server.port=8501 --server.address=0.0.0.0 --server.enableCORS false