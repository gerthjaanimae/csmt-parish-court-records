#!/bin/bash
set -e
#import the variables
source variables.sh

#The function for processing a single dialectal area
train_test_location () {
cd $train_files
echo $1 >> $script_dir/accuracy-tmp.txt
$script_dir/train-models.sh $1
mkdir -p test-translation-results/$i
$script_dir/test-model.sh $1 > test-translation-results/$i/$1.txt
 tail -2 test-translation-results/$i/$1.txt >> $script_dir/accuracy-tmp.txt
}
#Initialize the file for holding the accuracies temporarily
#Later on it will be processed and the averages will be calculated
> $script_dir/accuracy-tmp.txt
mkdir -p test-translation-results
mkdir -p $train_files

cd $train_files
for i in {1..10}
do echo "### Iteration number $i" >> $script_dir/accuracy-tmp.txt
python $script_dir/prepare-corpus-moses-silver-standard.py $records_annotated . $silver_standard
cat *-train.txt > for-lm.txt
$moses/moses/bin/lmplz -o 5 -S 50% < for-lm.txt > lm.arpa
for j in *-train.txt
do location=`echo $j | sed "s/-train.txt//"`
train_test_location $location
if [ $? -ne 0 ]; then
echo ###Restarting iteration $i
continue [$i]
fi
done
done

