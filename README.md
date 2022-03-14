# csmt-parish-court-records
This repository contains scripts for normalizing parish court records from the 19th century using character level statistical machine translation.
The texts originate from the crowdsourcing project of The National
Archives of Estonia, and the manual annotations have been created in
the project "Possibilities of automatic analysis of historical texts
by the example of 19th-century Estonian communal court minutes". The
project "Possibilities of automatic analysis of historical texts by
the example of 19th-century Estonian communal court minutes" is funded
by the national programme "Estonian Language and Culture in the
Digital Age 2019-2027".

# Prerequisits
In order to use the scripts in this repository, the following requirements have to be met.
* Moses has to be downloaded and compiled.
It can be obtained from https://www.statmt.org/moses/ 
* The Python library called ESTNLTK has to be installed.
It can be downloaded from https://github.com/estnltk/estnltk
* The scripts use Bash, so they do not work under Windows natively.

# Overview of the structure of the repository.
## Scripts
Contains the scripts for performing the experiments.
## manually-annotated-crowdsourcing
Contains the manually annotated parish court records which are required for training the machine translation.

## records-xml
Contains all of the parish court records in xml-format.

## silver-standard
Contains the files required for the silver standard experiments.

## experiments
The directory for the training files and models that will be created when running the scripts.

# Instructions
In order to check the accuracies of the baseline, silver standard, large lm and n-grams translations, run the check-accuracy-baseline.sh, check-accuracy-silver.sh etc scripts.
In order to normalize the whole corpus, run translate-corpus-baseline.sh, translate-corpus-silver.sh etc.
The scripts produce a lot of output, so you may want to direct it into a file.

More detailed instructions coming soon!   
