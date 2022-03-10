import sys
normalized=sys.argv[1]
translated=sys.argv[2]
lines_normalized=[]
lines_translated=[]
with open(normalized) as fin:
	for line in fin:
		line=line.strip().replace(" ", "")
		lines_normalized.append(line)
with open(translated) as fin:
	for line in fin:
		line=line.strip().replace(" ", "")
		lines_translated.append(line)
correct_translations=0
for i, line in enumerate(lines_normalized):
	if line==lines_translated[i]:
		print ("#+++#", line)
		correct_translations+=1
	else:
		print ("#---#", line, lines_translated[i])
print ("Correct translations ", correct_translations, len(lines_normalized))
print ("Accuracy: ", correct_translations * 100 / len(lines_normalized))