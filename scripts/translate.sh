#!/bin/bash
set -e
#The script for normalizing the texts from the single dialectal area
#The command line argument is the area
script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
#source $script_dir/variables.sh

for i in $1/*.xml
do 
new=`echo $i | sed "s:\$1:\$2:g"`
#echo $new
#Strip the xml tags
#Each word to a separate line
# spaces between the letters
tr '\n' '@' < $i |\
sed 's#@# @ #g' |\
sed -n 's:.*<sisu>\(.*\)</sisu>.*:\1:p' |\
sed 's# #\n#g' | sed -e 's#\(.\)#\1 #g' > tmp1
$moses/moses/bin/moses -v 0 -f $3 -i tmp1 > tmp2
#Convert the translated text back to its xml form
translated=`sed 's# ##g' < tmp2 | tr '\n' ' '`
#echo $translated
awk '/<sisu>/{p=1;print;print "&&&"}/<\/sisu>/{p=0}!p' $i |\
sed "s#&&&#$translated#g" | tr '@' '\n' |\
sed 's# \([,|.]\)#\1#g' > $new
done
