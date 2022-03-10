#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
#Performs the morphological analysis of municipal court records,
#Ranks the records according the amount of unknown word forms.
#The progress of the script is output to stderr
#Author: Gerth Jaanimäe
from __future__ import unicode_literals, print_function, absolute_import
import sys
from estnltk.text import Text
from collections import defaultdict
import csv
import os, os.path
import corpus_readers
from morph_pipeline import *
from estnltk.taggers.morph_analysis.morf_common import _is_empty_annotation
from estnltk.taggers import CompoundTokenTagger
# If the missing punctuation analysis should be added to the tsv output
add_punctuation_analyses = True
add_sentence_boundaries=False
#If the punctuation analyses should be subtracted from the statistics
subtract_punctuation_analyses = True
#Finds how many percents C constitutes from A and formats the results as string
def get_percentage_of_all_str( c, a ):
	return '{} / {} ({:.2f}%)'.format(c, a, (c*100.0)/a)


infile=sys.argv[1]
#	 (analysed, unamb, unk_title, unk_punct, punct, total)
#Setup the configuration for the morphological analysis

morph_conf={'vm_analyzer' : VabamorfAnalyzer(guess=False, propername=False),
	'newline_sentence_tokenizer' : SentenceTokenizer( base_sentence_tokenizer=LineTokenizer() ),
	'tokens_tagger' : TokensTagger(),
	'compound_tokens_tagger' : CompoundTokenTagger(),
	'prenormalizer' : word_prenormalizer(),
	'add_punctuation_analyses' : add_punctuation_analyses}
analysed=defaultdict(int)
unamb=defaultdict(int)
total=defaultdict(int)
unk_title=defaultdict(int)
unk_punct=defaultdict(int)
punct=defaultdict(int)
texts=corpus_readers.read_corpus(infile)
content={}
for text in texts:
	location=text.meta['location']
	id=text.meta['id']
	year=text.meta['year']
	text=apply_pipeline(text, morph_conf)
	record="\t".join([id, location, year])
	content[record]=text.text
	# Collect the statistics
	for word in text.morph_analysis:
		is_punct = len(word.text) > 0 and not any([c.isalnum() for c in word.text])
		if not _is_empty_annotation( word.annotations[0] ):
			analysed[record] += 1
			if len(word.annotations) == 1:
				unamb[record] += 1
		if _is_empty_annotation( word.annotations[0] ):
			# save the type of unknown word
			
			if len(word.text) > 0:
				if word.text[0].isupper():
					unk_title[record] += 1
				if is_punct:
					unk_punct[record] += 1
		else:
			# Save the type of regular word
			if is_punct:
				punct[record] += 1
		total[record] += 1
#Agregate the statistics
results={}
for record in total:
	if total[record] > 15:
		# Corrections
		if subtract_punctuation_analyses:
			if add_punctuation_analyses:
				# The punctuation won't be analysed if guessing is disabled
				total[record] -= punct[record]
				analysed[record] -= punct[record]
				unamb[record] -= punct[record]
				punct[record] = 0
			else:
				# If guessing is disabled, the punctuation won't be analysed.
				total[record] -= unk_punct[record]
				unk_punct[record] = 0
		percent_analysed = (analysed[record] * 100.0) / total[record]
		results_tuple = (analysed[record], unamb[record], unk_title[record], unk_punct[record], total[record], percent_analysed)
		results[record]=results_tuple



# Sort the results according to percentages
# Output the results
aggregated = [0, 0, 0, 0, 0, 0]
for key in sorted(results, key = lambda x : results[x][-1], reverse=True):
	(analysed, unamb, unk_title, unk_punct, total, percent_analysed) = results[key]
	print("\t".join(['***', key, str(analysed), str(total), str(percent_analysed)]))
	print('	1. morf analüüsiga: '+get_percentage_of_all_str( analysed, total ))
	"""
	if analysed > 0:
		print('			 sh ühesed: '+get_percentage_of_all_str( unamb, analysed ))
	print('	2. morf analüüsita: '+get_percentage_of_all_str( (total-analysed), total ))
	if (total-analysed) > 0:
		print('  sh suure algustähega: '+get_percentage_of_all_str( unk_title,(total-analysed) ))
		if not subtract_punctuation_analyses:
			print('	  sh punktuatsioon: '+get_percentage_of_all_str( unk_punct,(total-analysed) ))
	"""
	#print()
	print(content[key].strip())
	