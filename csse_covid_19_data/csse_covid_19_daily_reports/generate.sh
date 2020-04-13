#!/bin/bash -ex

python analyze.py > ../us_deaths.csv
python doplot-non-cumulative.py ../us_deaths.csv ../2017_us_deaths.csv
python doplot-cumulative.py ../us_deaths.csv ../2017_us_deaths.csv
