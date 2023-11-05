#!/usr/bin/python
import sys
import collections
infile=sys.argv[1]
lines=[]
with open(infile) as fin:
	for line in fin:
		lines.append(line.strip())
iterations=[]
total=0
for index, line in enumerate(lines):
	if line.startswith("###"):
		if len(iterations) > 0:
			print ("Average accuracy for the iteration: ", total/len(iterations[-1]))
		print(line)
		iterations.append({})
		total=0
		continue
	print (line)
	if line.startswith("Accuracy"):
		location=lines[index-2]
		accuracy=line.replace("Accuracy:  ", "")
		accuracy=float(accuracy)
		total+=accuracy
		iterations[-1][location]=accuracy
	if index==len(lines)-1:
		print ("Average accuracy for the iteration: ", total/len(iterations[-1]))
whole_corpus=0
print ("###Average accuracies for a county across the iterations")
totals_per_location=collections.defaultdict(float)
for i in iterations:
    for location in i:
        #print (location, i[location])
        totals_per_location[location]+=i[location]
for location in totals_per_location:
    average = totals_per_location[location]/len(iterations)
    print(location, average)
    whole_corpus+=average
print ("The average accuracy for the whole corpus is ", whole_corpus/len(totals_per_location))

