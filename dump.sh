#!/bin/bash

mkdir -p data
wget -O data/tags.json.gz    https://vndb.org/api/tags.json.gz
wget -O data/traits.json.gz  https://vndb.org/api/traits.json.gz
wget -O data/votes2.gz       https://vndb.org/api/votes2.gz
