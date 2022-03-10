#!/bin/bash
set -e
#Set the variables
moses=/home/gerth/moses
script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
#experiments=`echo $script_dir | sed 's#/scripts#/experiments#'`
experiments=$script_dir/../experiments
#clean up the model from previous trainings if it exists
if [ -d "$experiments/$1" ]; then rm -Rf $experiments/$1; fi
#Train the translation model
echo $experiments


$moses/moses/scripts/training/train-model.perl --corpus $1-train --f txt --e normalized --external-bin-dir=$moses/training-tools --lm 0:5:$experiments/lm.arpa --root-dir $experiments/$1 --reordering msd-bidirectional-fe --mgiza
#echo Translation model trained successfully.
echo Tuning the weights of the trained model.
$moses/moses/scripts/training/mert-moses.pl $1-dev.txt $1-dev.normalized $moses/moses/bin/moses $experiments/$1/model/moses.ini  --working-dir  $experiments/$1/mert-1 --threads 4 --decoder-flags "--threads 4"
