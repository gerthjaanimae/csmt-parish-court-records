#!/bin/bash
script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/scripts
moses=/home/gerth/moses
records_annotated=$script_dir/../manually-annotated-crowdsourcing/
#the The directory containing the files for train, dev and test sets
train_files=`echo $script_dir | sed 's#/scripts#/experiments#'`
silver_standard=$script_dir/../silver-standard
