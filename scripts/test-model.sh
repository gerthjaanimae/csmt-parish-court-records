#!/bin/bash
#Set the variables
moses=/home/gerth/moses
script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
experiments=$script_dir/../experiments

$moses/moses/bin/moses -f $experiments/$1/mert-1/moses.ini -i $1-test.txt > hypothesis-$1.txt
python $script_dir/test-translation.py $1-test.normalized hypothesis-$1.txt
