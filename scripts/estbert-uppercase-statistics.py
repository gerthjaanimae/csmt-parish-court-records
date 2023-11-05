import os
from simpletransformers.ner import NERModel, NERArgs
import corpus_readers
import sys

from estnltk.taggers import SentenceTokenizer
from estnltk.taggers.standard.morph_analysis.proxy import MorphAnalyzedToken
def PredictDialect(dialect, lower_sentence_beginnings=False):
    #print (lower_sentence_beginnings)
    dialects_file=sys.argv[2]
    texts=corpus_readers.read_corpus(sys.argv[1], dialects_file)
    model_dir=os.path.join("estbert-outputs", dialect.lower(), "best-model")
    model_dir=model_dir.replace(" ", "_")
    model_args = NERArgs()
    model_args.train_batch_size = 16
    model_args.num_train_epochs=50
    model_args.evaluate_during_training = True,
    model_args.overwrite_output_dir=True
    model_args.labels_list=['needsNormF', 'needsNormT']
    model_args.silent=True
    
    model=NERModel('bert', model_dir, use_cuda=False, args=model_args)
    words_total=0
    estbertNeedsNormT=0
    estbertNeedsNormF=0
    vabamorfNeedsNormT=0
    vabamorfNeedsNormF=0
    
    upperNeedsNormF=0
    upperNeedsNormT=0
    lowerNeedsNormF=0
    lowerNeedsNormT=0
    
    texts_dialect=[]
    for text in texts:
        if text.meta['dialect']==dialect:
            if lower_sentence_beginnings:
                text.tag_layer(['words'])
                SentenceTokenizer().tag(text)
                x=""
                for sentence in text['sentences']:
                    sentence=" ".join(sentence.text)
                    sentence=sentence[0].lower()+sentence[1:]
                    
                    x+=sentence
                texts_dialect.append(x)
            else:
                texts_dialect.append(text.text)
            #break
    #print(dialect, len(texts_dialect))
    predictions, raw_outputs=model.predict(texts_dialect)
    with open ("../"+dialect+"_predictions.txt", "w") as fout:
        #print (len(predictions))
        for i in predictions:
            for word in i:
                for key in word:
                    fout.write(key+"\t"+word[key]+"\n")
                    if key[0].isupper() and word[key]=='needsNormT':
                        upperNeedsNormT+=1
                        words_total+=1
                    if key[0].isupper() and word[key]=='needsNormF':
                        upperNeedsNormF+=1
                        words_total+=1
                    if key[0].islower() and word[key]=='needsNormT':
                        lowerNeedsNormT+=1
                        words_total+=1
                    if key[0].islower() and word[key]=='needsNormF':
                        lowerNeedsNormF+=1
                        words_total+=1
                    if (key[0].isupper() or key[0].islower()) and MorphAnalyzedToken(key).is_word:
                        vabamorfNeedsNormF+=1
                    elif (key[0].isupper() or key[0].islower()) and  not MorphAnalyzedToken(key).is_word:
                        vabamorfNeedsNormT+=1
    estbertNeedsNormT+=upperNeedsNormT
    estbertNeedsNormT+=lowerNeedsNormT
    estbertNeedsNormF+=upperNeedsNormF
    estbertNeedsNormF+=lowerNeedsNormF
                    
    line="\t".join([dialect, str(words_total), str(vabamorfNeedsNormT), str(vabamorfNeedsNormF), str(estbertNeedsNormT), str(estbertNeedsNormF), str(upperNeedsNormT), str(upperNeedsNormF), str(lowerNeedsNormT), str(lowerNeedsNormF)])
    return line

if __name__ == '__main__':
    dialects=["idamurre", "kirderanniku murre", "läänemurre", "Mulgi murre", "saarte murre", "Tartu murre", "Võru murre", "keskmurre"]
    lines=[]
    lines.append("\t".join(['dialect', 'words_total', 'vabamorfNeedsNormT', 'vabamorfNeedsNormF', 'estbertNeedsNormT', 'estbertNeedsNormF', 'upperNeedsNormT', 'upperNeedsNormF', 'lowerNeedsNormT', 'lowerNeedsNormF']))
    lines.append("The first words of a sentence are not lowercased.")
    for dialect in dialects:
        lines.append(PredictDialect(dialect))
    lines.append("The first words of a sentence are lowercased.")
    for dialect in dialects:
        lines.append(PredictDialect(dialect, lower_sentence_beginnings=True))
    
    
    for line in lines:
        print (line)
