#Converts texts from contemporary writing system to old writing system
from estnltk import text
from estnltk.vabamorf.morf import syllabify_word
import corpus_readers
import os
import sys
dialects_file='/home/gerth/VinuxShare/processing-old-estonian/ra_piirkonnad_murded.csv'
texts=corpus_readers.read_corpus(sys.argv[1], dialects_file)
if not os.path.exists(sys.argv[2]):
    os.mkdir(sys.argv[2])

words_location={}

def convert_word(word):
    vowels='aeiouõäöü'
    consonants='bcdfghjklmnpqrstvwxz'
    
    syllables=syllabify_word(word)
    for i, syllable in enumerate(syllables):
        if syllable['accent']==1 and syllable['quantity']==1:
            if syllables[i+1]['syllable'][0] in consonants:
                syllable['syllable']+=syllables[i+1]['syllable'][0]
        if syllable['accent']==1 and syllable['quantity']>=2:
            for j, letter in enumerate(syllable['syllable']):
                #print (letter, syllables['syllable'][j+1])
                if j < len(syllable['syllable'])-1 and letter in vowels and letter==syllable['syllable'][j+1]:
                    syllable['syllable']=syllable['syllable'][0 : j : ] + syllable['syllable'][j + 1 : :]
    
    new_word=""
    for syllable in syllables:
        new_word+=syllable['syllable']
    return new_word


def convert_text(text):
    new_text=""
    #print (text)
 #Sometimes the dialect info is not available
    if 'dialect' not in text.meta:
        text.meta['dialect']=text.meta['location']
    if text.meta['dialect'] not in words_location:
        words_location[text.meta['dialect']]=[]
    text.tag_layer(['words'])
    
    for word in text.words:
        new_word=convert_word(word.text)
        new_text+=new_word+" "
        is_punct = len(word.text) > 0 and not any([c.isalnum() for c in word.text])
        if not is_punct:
            words_location[text.meta['dialect']].append((new_word, word.text))
    return new_text
ids=[]
with open(sys.argv[3]) as fin:
    for line in fin:
        ids.append(line.strip())

for text in texts:
    if text.meta['id'] not in ids:
        continue
    new=convert_text(text)
    print ("###")
    print (text.text)
    print (new)

for location in words_location:
    with open(os.path.join(sys.argv[2], location+".txt"), "w") as fout:
        for word in words_location[location]:
            #print (word)
            fout.write(word[0]+"\t"+word[1]+"\n")
