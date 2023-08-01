#!/bin/bash

# Use this script:
# ./download.sh drugbank_username drugbank_password

# Allow to provide drugbank login via args or env variables
DRUGBANK_USERNAME="${1:-$DRUGBANK_USERNAME}"
DRUGBANK_PASSWORD="${2:-$DRUGBANK_PASSWORD}"

DRUGBANK_VERSION="${DRUGBANK_VERSION:=5-1-8}"

mkdir -p data
cd data

if [ ! -f "data/drugbank.xml" ]; then
    echo "data/drugbank.xml does not exist, downloading version $DRUGBANK_VERSION"
    curl -Lfs -o drugbank.zip -u $DRUGBANK_USERNAME:$DRUGBANK_PASSWORD https://go.drugbank.com/releases/$DRUGBANK_VERSION/downloads/all-full-database
    unzip -o drugbank.zip
fi

if [ ! -f "data/mondo.json" ]; then
    echo "data/mondo.json does not exist, downloading"
    curl -Ls -o mondo.json https://github.com/monarch-initiative/mondo/releases/latest/download/mondo.json
    curl -Lfs -o drugbank.zip -u $DRUGBANK_USERNAME:$DRUGBANK_PASSWORD https://go.drugbank.com/releases/$DRUGBANK_VERSION/downloads/all-full-database
    unzip -o drugbank.zip
fi