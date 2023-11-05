import logging
import os
import pandas as pd
from simpletransformers.ner import NERModel, NERArgs
from estnltk import text
import sys
from estnltk.taggers import SentenceTokenizer
from estnltk.taggers.standard.morph_analysis.proxy import MorphAnalyzedToken
from estnltk import Layer
import corpus_readers
from estnltk.taggers.standard.text_segmentation.pretokenized_text_compound_tokens_tagger import PretokenizedTextCompoundTokensTagger
from estnltk.taggers.standard.text_segmentation.whitespace_tokens_tagger import WhiteSpaceTokensTagger
import statistics
#import zipfile
import pathlib
import shutil
import random
logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)
#print ("Preparing data for training and later predictions.")
#Setup for cleaning up the output from noisy training
save_stdout = sys.stdout
#Directory for manually annotated files
texts_tmp=corpus_readers.read_from_tsv(sys.argv[1])
#As the texts need to be in order, let's sort them first.
texts2=[]
for text in texts_tmp:
    texts2.append(text)
texts=sorted(texts2, key=lambda text: text.text)

num_iterations=5
results={}
#Read in the data first
#Create a dictionary for holding together the sentences from a dialectal area
sentences_loc={}
for text in texts:
    if 'dialect' not in text.meta:
        text.meta['dialect']=text.meta['location']
    if text.meta['dialect'] not in sentences_loc:
        sentences_loc[text.meta['dialect']]=[]
    text.tag_layer(['words'])
    text.pop_layer('words')
    words_layer=text['manual_morph']
    words_layer.name="words"
    text.add_layer(words_layer)
    SentenceTokenizer().tag(text)
    
    for sentence in text['sentences']:
        sentences_loc[text.meta['dialect']].append(sentence)
random.seed(111)
#Sort the sentences first
for location in sentences_loc:
    sentences_loc[location].sort()
#Shuffle the sentences first
for location in sentences_loc:
    random.shuffle(sentences_loc[location])
for n in range(num_iterations):
    print ("Run number ", n+1)
    data={}
    for location in sentences_loc:
        data[location]=[]
        for index, sentence in enumerate(sentences_loc[location]):
            #print (sentence)
            #print (sentence.spans)
            for span in sentence.spans:
                #Let's check if the old spelling is the same as the normalized form.
                if span.text.lower() == str(span.annotations[0]['normalized_text']).lower():
                    labels="needsNormF"
                else:
                    labels="needsNormT"
                data[location].append([index, span.text, labels])
    
    for location in data:
        print (location)
        sys.stdout = open('trash', 'w')
        if location not in results:
            results[location]={}
        test_start=int(n*0.2*len(data[location]))
        test_end=int(((n*0.2)+0.2)*len(data[location]))
        train_data = pd.DataFrame(
            data[location][:test_start]+data[location][test_end:], columns=["sentence_id", "words", "labels"]
        )
        eval_data=pd.DataFrame(
            data[location][test_start:test_end], columns=["sentence_id", "words", "labels"]
        )
        model_args = NERArgs()
        model_args.train_batch_size = 16
        model_args.num_train_epochs=50
        model_args.save_eval_checkpoints=False
        model_args.save_model_every_epoch=False
        model_args.evaluate_during_training = True,
        model_args.overwrite_output_dir=True
        model_args.output_dir=os.path.join("estbert-outputs", location)
        model_args.best_model_dir=os.path.join(model_args.output_dir, "best-model")
        model_args.labels_list=['needsNormF', 'needsNormT']
        model_args.silent=True
        model_args.verbose=False
        model = NERModel(
        
            "bert", "tartuNLP/EstBERT", args=model_args, use_cuda=False
        )

        # Train the model
        model.train_model(train_data, eval_data=eval_data)

        # Evaluate the model
        result, model_outputs, preds_list = model.eval_model(eval_data)
        sys.stdout = save_stdout
        #Collect the statistics and diagnostics
        #Lines for outputting into the files for diagnostics
        diag_lines=[]
        if not os.path.exists(os.path.join("..", "diagnostics-estbert", str(n+1))):
            os.makedirs(os.path.join("..", "diagnostics-estbert", str(n+1)))
        diag_filepath=os.path.join("..", "diagnostics-estbert", str(n+1), location+".txt")
        vabamorf_correct=0
        estbert_correct=0
        sentences=[]
        sentence=[]
        s_id=eval_data.iloc[0]['sentence_id']
        for i in eval_data.iloc:
            sentence_id=i['sentence_id']
            if s_id != sentence_id:
                sentences.append(sentence)
                sentence=[]
                s_id=sentence_id
            word=i['words']
            label=i['labels']
            sentence.append((word, label))
        #Also add the last sentence
        sentences.append(sentence)
        #print (sentences)
        #as preds_list is a 2.dimensional list, containing sentences and then words, we have to make a double loop
        #print (len(preds_list), len(sentences))
        for ind1, i in enumerate(preds_list):
            #print (len(preds_list[ind1]), len(sentences[ind1]))
            for ind2, j in enumerate(i):
                word=sentences[ind1][ind2][0]
                label=sentences[ind1][ind2][1]
                #Check if a word is indeed a word
                #if (word[0].isupper() or word[0].islower()):
                if word[0]:
                    if MorphAnalyzedToken(word).is_word:
                        morph="needsNormF"
                    else:
                        #Check if a word is punctuation
                        if len(word) > 0 and not any([c.isalnum() for c in word]):
                            continue
                        morph="needsNormT"
                    diag_lines.append("\t".join([word, label, morph, j]))
                    if j==label:
                        estbert_correct+=1
                    if morph==label:
                        vabamorf_correct+=1
                #   ˇprint (eval_data.iloc[k])
        result['total'] = len(diag_lines)
        result['vabamorf']= vabamorf_correct
        result['vabamorf_percentage']=round((vabamorf_correct/result['total']), 2)
        result['estbert']= estbert_correct
        result['estbert_percentage']=round((estbert_correct/result['total']), 2)
        print (result)
        #print(len_preds, len(eval))
        with open(diag_filepath, "w") as fout:
            fout.write("word\tcorrect label\tvabamorf\testbert\n")
            for line in diag_lines:
                fout.write(line+"\n")
        for key in result:
            if key not in results[location]:
                results[location][key]=[]
            results[location][key].append(result[key])
        #break
#Calculate the averages
averages={}
for location in results:
    averages[location]={}
    for key in results[location]:
        averages[location][key]=statistics.mean(results[location][key])
print ("Averages of the results")
for location in averages:
    print (location)
    print (averages[location])
"""
        # Make predictions with the model
        print ("Predictions on a single text.")
        for text in texts:
            loc=text.meta['location'].replace("\s", "_")
            #print (text.meta['location'])
            if loc==location and len(text.text) > 500:
                test_text=text.text
                break
        predictions, raw_outputs = model.predict([test_text])
        print (predictions)
        #print (raw_outputs)
"""
