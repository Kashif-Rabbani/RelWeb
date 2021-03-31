#!/bin/bash

if [ ! -d "outputs" ]; then
    wget http://qweb.cs.aau.dk/factify/files/outputs.zip
	unzip outputs.zip -d outputs
fi

if [ ! -f "relevance_scores.csv" ]; then
    wget http://qweb.cs.aau.dk/factify/files/relevance_scores.csv
fi

if [ ! -f "eval.py" ]; then
    wget http://qweb.cs.aau.dk/factify/files/eval.py
fi

python3 eval.py