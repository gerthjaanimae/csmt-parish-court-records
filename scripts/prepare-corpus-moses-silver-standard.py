# -*- coding: utf-8 -*-

#A script for preparing the corpus in order to use with Moses machine translation
#Author: Gerth Jaanimäe
import sys
if len(sys.argv) < 1:
    sys.stderr.write("Error: You must specify the directory of the manually tagged files.")
    sys.exit(1)
def corpus_to_file(corpus, outputfile):
    with open(outputfile+".txt", "w")as fout0:
        with open(outputfile+".normalized", "w")as fout1:
            for word in corpus:
                #print(word)
                if len(word) < 2:
                    continue
                fout0.write(word[0]+"\n")
                fout1.write(word[1]+"\n")
import corpus_readers
from estnltk import Layer, Text
import random
random.seed(1111)
import os
dialects_file=os.path.join(os.path.dirname(sys.argv[0]), "..", "ra_piirkonnad_murded.csv")
texts=corpus_readers.read_from_tsv(sys.argv[1])
outputdir=sys.argv[2]
silver_standard=sys.argv[3]
words_per_location={}
#print (texts[0])
for text in texts:
    if 'dialect' not in text.meta:
        text.meta['dialect']=text.meta['location']
    if text.meta['dialect'] not in words_per_location:
        words_per_location[text.meta['dialect']]=[]
    for word in text['manual_morph']:
        #print (word.annotations)
        if word.annotations[0]['partofspeech']=='Z' or word.annotations[0]==None or word.annotations[0]['normalized_text']=="":
            continue
        word_tuple=(" ".join(word.text), " ".join(str(word.annotations[0]['normalized_text'])))
        #print (word_tuple)
        
        words_per_location[text.meta['dialect']].append(word_tuple)

for location in words_per_location:
    #Let's extract the test portion first, then add the artificially created silver standard if it exists
    random.shuffle(words_per_location[location])
    test_amount=int(len(words_per_location[location])*20/100)
    test=words_per_location[location][:test_amount]
    if os.path.exists(os.path.join(silver_standard, location+".txt")):
        with open (os.path.join(silver_standard, location+".txt")) as fin:
            for line in fin:
                line=line.strip()
                word=line.split("\t")
                if len(word) < 2:
                    continue
                word[0]=" ".join(word[0])
                word[1]=" ".join(word[1])
                word_tuple=tuple(word)
                words_per_location[location].append(word_tuple)
    train_dev=words_per_location[location][test_amount:]
    random.shuffle(train_dev)
    train_amount=int(len(train_dev)*90/100)
    train=train_dev[:train_amount]
    dev=train_dev[train_amount:]
    corpus_to_file(train, os.path.join(outputdir, location+"-train"))
    corpus_to_file(dev, os.path.join(outputdir, location+"-dev"))
    corpus_to_file(test, os.path.join(outputdir, location+"-test"))