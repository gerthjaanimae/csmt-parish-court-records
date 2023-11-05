from estnltk import Text
import csv
from bs4 import BeautifulSoup
import os
import sys
import re
from estnltk.taggers.standard.text_segmentation.whitespace_tokens_tagger import WhiteSpaceTokensTagger
from estnltk.taggers.standard.text_segmentation.pretokenized_text_compound_tokens_tagger import PretokenizedTextCompoundTokensTagger
from estnltk.taggers.standard.text_segmentation.word_tagger import WordTagger
from estnltk import Layer
from estnltk.taggers.standard.morph_analysis.morf_common import _postprocess_root
def read_from_csv(path):
    with open(path, encoding="utf-8") as fin:
        records=[]
        reader=csv.DictReader(fin, delimiter='|', quotechar='"')
        for row in reader:
            #Cleanup the texts from html-tags
            soup=BeautifulSoup(row['text'], "html.parser")
            content=soup.get_text()
            meta={
                'location':row['maakond'].lower(),
                'year' : row['year'],
                'id' : row['id']}
            records.append((content, meta))
    return records

def read_from_csv(path, dialects_file):
    if dialects_file !="":
        with open(dialects_file, encoding="utf-8") as fin:
            dialects=[]
            reader=csv.DictReader(fin, delimiter=';')
            for row in reader:
                dialects.append(row)
    with open(path, encoding="utf-8") as fin:
        records=[]
        reader=csv.DictReader(fin, delimiter='|', quotechar='"')
        for row in reader:
            #Cleanup the texts from html-tags
            soup=BeautifulSoup(row['text'], "html.parser")
            content=soup.get_text()
            if dialects_file != "":
                #Lookup the dialect
                dialect=""
                for d in dialects:
                    if d['maakond_kuni1917']== row['maakond'] and d['kihelkond']==row['kihelkond']:
                        dialect=d['murre']
                if dialect=="":
                    #print (d['kihelkond'], row['kihelkond'])
                    dialect=row['kihelkond']
                    #sys.stderr("Error: Could not find the dialect information.")
            meta={
                'location':row['maakond'].lower(),
                'year' : row['year'],
                'id' : row['id']}
            if dialects_file != "":
                meta['dialect']=dialect

            records.append((content, meta))
    return records


def read_from_xml(path):
    records=[]
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            (head, tail) = os.path.split(root)
            if len(files) > 0:
                for file in files:
                    if not file.endswith(".xml"):
                        continue
                    with open(os.path.join(root, file), encoding="utf-8") as fin:
                        content=fin.read()
                    soup=BeautifulSoup(content, "lxml")
                    #print (file)
                    try:
                        content=soup.find("sisu").getText()
                    except:
                        continue
                    location=soup.find("vald").getText().lower()
                    #Sometimes the date is not written
                    try:
                        date=soup.find("aeg").getText()
                        year=date.split(".")[-1]
                    except AttributeError:
                        year="n.a."
                    #Let's get the id from the filename and remove the extension
                    record_id=file.split(".")[0]
                    meta={'year' : year,
                        'location' : location,
                        'id':record_id}
                    records.append((content, meta))
    return records

def read_from_tsv(path):
    texts=[]
    tokens_tagger = WhiteSpaceTokensTagger()
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            (head, tail) = os.path.split(root)
            if len(files) > 0:
                for file in files:
                    if not file.endswith(".tsv"):
                        continue
                    with open(os.path.join(root, file), "rU", encoding="utf-8") as fin:    
                        reader=csv.reader(fin, delimiter="\t")
                        rows=[]
                        #Add the row lengths into separate list. The most frequent one should be the correct length.
                        row_lengths=[]
                        for row in reader:
                            row_lengths.append(len(row))
                            rows.append(row)
                        max_length=max(set(row_lengths), key = row_lengths.count)
                        words=[]
                        #Lines containing a word and its analysis
                        word=[]
                        #Morphological analysis of the whole text.
                        morph_analysis=[]
                        raw_text=""
                        multiword_expressions = []
                        #Symbols that are forbidden at the beginning of a line
                        forbidden_starts=["#", "¤", "£", "@"]
                        for index, row in enumerate(rows):
                            #print (file, index)
                            #Check if the row is not empty
                            if row==[]:
                                continue
                            row[0]=row[0].strip()
                            row[1]=row[1].strip(" ")
                            #Validate the manually tagged file
                            #check if any of these forbidden symbols are in the first column
                            if len(row[0]) > 0:
                                if row[0][0] in forbidden_starts:
                                    sys.stderr.write("Something is wrong with the following file: "+file+" In the following line: "+str(index+1)+"\n"+"\t".join(row)+"The symbol is: "+row[0][0]+"\n")
                                    sys.exit(1)
                            #Check if the row has correct number of elements
                            #If there are less than max_length then it is probably an adverb, abbreviation etc.
                            #But if there are more, then there's something wrond and the user has to be notified.
                            if len(row) > max_length:
                                #If the elements after the 6th one contain nothing, then we can continue.
                                for x in row[max_length:]:
                                    x=x.strip()
                                    if x !="":
                                        sys.stderr.write("Something is wrong with the following file: "+file+" In the following line: "+str(index+1)+"\n"+"\t".join(row)+str(len(row))+"\n")
                                        #print (row)
                                        sys.exit(1)
                            #If the first element of a row is empty then it is an alternative analysis of a word.
                            if row[0]=="" and word:
                                word.append(row)
                            else:
                                if len(word) != 0:
                                    words.append(word)
                                #After appending the word into the words list let's initialize a new word.
                                word=[row]
                        #As the loop terminates before adding the last word into the list, let's do it now
                        words.append(word)
                        for word in words:
                            #Iterate over the analyses and check for manual fixes.
                            #Remove all other analyses if they exist.
                            type_of_fix=""
                            for analysis in word:
                                #As it may be sometimes necessary to look at the whole line, join the elements of a row back together.
                                line="\t".join(analysis)
                                if "¤" in line:
                                    word[0][1:]=[None, None, None, None, None]
                                    word=[word[0]]
                                    
                                    type_of_fix="No_correct_analysis_available"
                                    break
                                elif analysis[1].startswith("@"):
                                    word[0][1:]=analysis[1:]
                                    word=[word[0]]
                                    word[0][1]=word[0][1].strip("@")
                                    type_of_fix="correct_analysis_provided"
                                    break
                                elif analysis[1].startswith("£"):
                                    word[0][1:]=analysis[1:]
                                    word=[word[0]]
                                    word[0][1]=word[0][1].strip("£")
                                    type_of_fix="correct_analysis_not_provided"
                                    break
                                elif re.match("#[A-Üa-ü0-9]", analysis[1]):
                                    word[0][1:]=analysis[1:]
                                    word=[word[0]]
                                    word[0][1]=word[0][1].strip("#")
                                    type_of_fix="correct_analysis_manually_added"
                                    break
                            analyses=[]
                            for a in word:
                                analysis={}
                                if max_length==7:
                                    analysis['normalized_text']=a[1]
                                    del a[1]
                                else:
                                    analysis['normalized_text']=a[0]
                                analysis['root']=a[1]
                                #If it is an abbreviation some fields may be missing.
                                #Sometimes there are also missing tabs in the end of a line, so the last element has to be checked.
                                if a[-1]=="Y" or a[-1]=='D' or a[-1]=='K':
                                    analysis['partofspeech']=a[-1]
                                    analysis['ending']=""
                                    analysis['form']=""
                                    analysis['clitic']=""
                                else:
                                    analysis['ending']=a[2]
                                    analysis['clitic']=a[3]
                                    analysis['partofspeech']=a[4]
                                    analysis['form']=a[5] if len(a) ==6 else ""
                                if analysis['root']!=None:
                                    analysis['root'], analysis['root_tokens'], analysis['lemma'] = _postprocess_root( analysis['root'], analysis['partofspeech'])
                                else:
                                    analysis['root_tokens']=None
                                    analysis['lemma'] =None
                                analysis['type_of_fix']=type_of_fix
                                analyses.append(analysis)
                            #if len(analyses) > 1:
                            #    print (analyses)
                            word_tuple=(word[0][0], analyses)
                            morph_analysis.append(word_tuple)
                            #Let's reconstruct the raw text
                            #A list of punctuations where there's going to be no whitespace between the word and punctuations
                            #punct_no_whitespace=["," "."]
                            if analysis['lemma'] =="\.":
                                raw_text+=word[0][0]
                            else:
                                raw_text+=" " + word[0][0]
                            if ' ' in word[0][0]:
                                multiword_expressions.append(word[0][0])
                        text = Text(raw_text)
                        #print (text.text)
                        tokens_layer=tokens_tagger.make_layer(text)
                        multiword_expressions = [mw.split() for mw in multiword_expressions]
                        compound_tokens_tagger = PretokenizedTextCompoundTokensTagger( multiword_units = multiword_expressions )
                        compound_tokens_layer=compound_tokens_tagger.make_layer(text, layers={'tokens':tokens_layer})
                        word_tagger=WordTagger()
                        words_layer=word_tagger.make_layer(text, layers={'compound_tokens':compound_tokens_layer, 'tokens':tokens_layer})
                        #text.tag_layer(['sentences'])
                        layer_morph=Layer(name='manual_morph',
                            text_object=text,
                            attributes=['root', 'lemma', 'root_tokens', 'ending', 'clitic', 'partofspeech', 'form', 'normalized_text'],
                            ambiguous=True)
                        layer_fix=Layer(name='type_of_fix',
                            text_object=text,
                            attributes=['type_of_fix'],
                            parent='manual_morph')
                        #print (file, len(words_layer), len(morph_analysis))
                        for ind, word in enumerate(words_layer):
                            layer_fix.add_annotation((word.start, word.end), type_of_fix=analysis['type_of_fix'])
                            assert word.text == morph_analysis[ind][0], '(!) Mismatching words {!r} vs {!r} in file {!r}'.format(word.text, morph_analysis[ind][0], file)
                            #print ("***", file, morph_analysis[ind][0], words_layer[ind].text)
                            for analysis in morph_analysis[ind][1]:
                                layer_morph.add_annotation((word.start, word.end), **analysis)
                        text.add_layer(layer_morph)
                        text.add_layer(layer_fix)
                        text.meta['id']=file.split(".")[0]
                        text.meta['location']=root.split(os.sep)[-1].lower()
                        texts.append(text)
    return texts



def read_corpus(path, dialects=""):
    sys.stderr.write("Reading corpus.\n")
    if os.path.isdir(path):
        records=read_from_xml(path)
    elif os.path.isfile(path):
        if path.endswith("csv"):
            records=read_from_csv(path, dialects)
    #In order to display the progress, initialise the counter
    count=0
    #In order not to bombard the stderr, let's initialise the displayed progress value and if it differs from the progress, we will update and display it.
    percent_displayed=""
    progress=""
    for i in records:
        #text=i[0].replace("\n\n", "\n")
        text=i[0]
        #text=text.replace(chr(10), "")
        #text = os.linesep.join([s for s in text.splitlines() if s])
        text=Text(text)
        text.meta=i[1]
        count+=1
        percent=int(count*100/len(records))
        if percent != percent_displayed:
            percent_displayed=percent
            progress="Working with records "+str(percent_displayed).rjust(3)+"%"
            sys.stderr.write("\r"+progress)
            sys.stderr.flush()

        yield text
    sys.stderr.write("\n")