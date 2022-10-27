#!/bin/bash
#Set the variables
moses=/home/gerth/moses
script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
experiments=$script_dir/../experiments

$moses/moses/bin/moses -f $experiments/$1/mert-1/moses.ini -i $1-test.txt > hypothesis-$1.txt
#as we are translating bigrams, but evaluating the single words let's remove the second part of a bigram
sed -i 's/#.*//' $1-test.normalized
sed -i 's/#.*//' hypothesis-$1.txt
python $script_dir/test-translation.py $1-test.normalized hypothesis-$1.txt
