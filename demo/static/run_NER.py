import os, json
import parse_json
import re
import codecs

class_path = "'../../stanford-corenlp-full-2016-10-31/*'" 
def generate_NER(location):
	outputDirectory = "data/" + location + "/"
	os.system("java -mx1g -cp " + class_path + " edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators 'tokenize,ssplit,pos,lemma,ner' -outputFormat json -outputDirectory " + outputDirectory + " -outputExtension _NER_output.json -replaceExtension True -textFile " + outputDirectory + "/" + location + ".txt")
	with open(outputDirectory + location + '_NER_output.json', 'r') as tagged:
		return json.load(tagged)

# the dependency parsing part
'''
os.system("java -cp " + class_path + " edu.stanford.nlp.parser.nndep.DependencyParser -model edu/stanford/nlp/models/parser/nndep/english_SD.gz -textFile " + input_file + " -outFile data/parsed.txt")
locations = parse_json.get_locations(input_file + ".json")
data = codecs.open('data/parsed.txt', 'r', "utf-8")
for line in data.read().splitlines():
	matchObj = re.match(r'([a-z]+\:?[a-z]+?)\(([a-zA-Z]+)\-(\d+)\, ([a-zA-Z]+)\-(\d+)\)', line)
	if matchObj != None:
		if "nmod" in matchObj.group(1) or "appos" in matchObj.group(1) or "compound" in matchObj.group(1) or "nsubj" in matchObj.group(1):
			if matchObj.group(2) in locations or matchObj.group(4) in locations:
				print line
'''
