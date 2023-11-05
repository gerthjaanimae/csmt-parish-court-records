#~/bin/bash
set -e
source variables.sh
process_location () {
#echo @@@ processing location $1
$script_dir/train-models.sh $1
$script_dir/test-model.sh $1 > results-$1.txt
mkdir -p $script_dir/../translated-silver/$1
$script_dir/translate.sh $script_dir/../records-xml/$1 $script_dir/../translated-silver/$1 ~/moses/vallakohtud/experiments/$1/mert-1/moses.ini
}

#Create or initialize the training, dev and test set
python $script_dir/prepare-corpus-moses-silver.py $records_annotated $train_files $silver_standard
#Train the language model
cd $train_files
cat *-train.txt > for-lm.txt
$moses/moses/bin/lmplz -o 5 -S 50% < for-lm.txt > lm.arpa
for j in *-train.txt
do location=`echo $j | sed "s/-train.txt//"`
process_location $location
done


echo @@@ Results of the morphological analysis
python $script_dir/annotate_corpus.py $script_dir/../translated-silver $script_dir/../analyses-translated
