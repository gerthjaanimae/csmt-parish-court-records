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
python $script_dir/prepare-corpus-moses-ngrams.py $records_annotated .
cat *-train.normalized > for-lm.txt
#add the artificially created silver standard to the language model
for x in $silver_standard/*.txt
do sed 's/^[^\t]*\t//g' $x | sed 's/w/v/g' | sed 's/W/V/g' > tmp1
tail -n +2 tmp1 | sed 's/^/#/g' > tmp2
paste tmp1 tmp2 | sed 's/\s#/#/g' > tmp3
grep '#' tmp3 | sed 's/\(.\)/\1 /g' | sed 's/ # /#/g' >> for-lm.txt
done
$moses/moses/bin/lmplz -o 5 -S 50% < for-lm.txt > lm.arpa
for j in *-train.txt
do location=`echo $j | sed "s/-train.txt//"`
train_test_location $location
if [ $? -ne 0 ]; then
echo ###Restarting iteration $i > accuracy-tmp.txt
continue [$i]
fi
done
done
cd $script_dir
python calculate-translation-averages.py $script_dir/accuracy-tmp.txt

