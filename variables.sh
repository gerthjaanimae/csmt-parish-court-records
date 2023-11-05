#!/bin/bash
export script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/scripts
#Moses directory
export moses=/gpfs/space/home/gerthj/moses
#Directory for manually annotated parish court records
export records_annotated=$script_dir/../manually-annotated-crowdsourcing/
#The directory containing translation models, the files for train, dev and test sets
export train_files=/gpfs/space/home/gerthj/csmt-parish-court-records/experiments
#The directory containing silver standard files
export silver_standard=$script_dir/../silver-standard
