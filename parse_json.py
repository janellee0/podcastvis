import json
import pprint
import pycountry
from geopy import geocoders
from collections import defaultdict
from operator import itemgetter
import argparse

gn = geocoders.Nominatim()
pp = pprint.PrettyPrinter(indent=4)

def main_location(words):
	countries = list(pycountry.countries)
	country_names = [x.name for x in countries]
	locations = []
	for word in words:
		if "NER_token" in word and word["tfidf_score"] > 0:
			if word["NER_token"]["ner"] == "LOCATION":
				locations.append(word)
	locations = list(map(lambda x:x["word"], locations))
	freqs = [(word, locations.count(word)) for word in locations]
	sorted_locs = [x[0] for x in sorted(list(set(freqs)),key=itemgetter(1),reverse=True)]
	country = None
	city = None
	for loc in sorted_locs:
		if country == None:
			country = next((i for i in countries if i.name == loc), None)
	if country != None:
		#print sorted_locs[0] + " " + country.name
		return sorted_locs[0] + " " + country.name
	else:
		return sorted_locs[0]

def assemble_loc(words):
	complete = ""
	for i,word in enumerate(words):
		if "NER_token" in word:
			if word["NER_token"]["ner"] == "LOCATION":
				complete += word["word"]
				if i < len(words)-1:
					complete += " "
	return complete


def assemble_propernoun(words, num_before):
	complete = ""
	before = ""
	for i in range(num_before-1, -1, -1):
		prev = words[i]
		if "NER_token" in prev:
			#if prev["NER_token"]["pos"] == "NNP" and prev["NER_token"]["ner"] != "LOCATION":
			if prev["NER_token"]["pos"] == "NNP":
				if i > 0:
					before = prev["word"] + " " + before
			else:
				break
	complete += before
	complete += words[num_before]["word"]
	for i in range(num_before+1, len(words)-1):
		word = words[i]
		if "NER_token" in word:
			if word["NER_token"]["pos"] == "NNP" or word["NER_token"]["pos"] == "NN" or word["NER_token"]["ner"] == "NUMBER":
				complete += word["word"]
				if i < len(words)-1:
					complete += " "
	return complete

def assemble_nounphrase(words, num_before):
	complete = ""
	before = ""
	for i in range(num_before-1, -1, -1):
		prev = words[i]
		if "NER_token" in prev:
			if (prev["NER_token"]["pos"] == "JJ" or prev["NER_token"]["pos"] == "NN" or prev["NER_token"]["pos"] == "NNP") and prev["tfidf_score"] > 0:
				if i > 0:
					before = prev["word"] + " " + before
			else:
				break
	complete += before
	complete += words[num_before]["word"] + " "
	for i in range(num_before+1, len(words)):
		word = words[i]
		if "NER_token" in word:
			if word["NER_token"]["pos"] == "NNP" or word["NER_token"]["pos"] == "NN" or word["NER_token"]["ner"] == "NUMBER":
				complete += word["word"]
				if i < len(words)-1:
					complete += " "
	return complete

def get_entities(location):
	queries = []
	query_words = []
	location_words = set()
	base = "static/data/" + location + "/"
	with open(base + location + "_NER_output.json") as NER:
		NER_output = json.load(NER)
		with open(base + location + "_scored_transcript_BROWN.json", 'r') as tagged:
			words = json.load(tagged)
			destination = main_location(words)
			for sentence in NER_output["sentences"]:
				nouns = []
				locs = []
				for i,token in enumerate(sentence["tokens"]):
					index = next((idx for idx,i in enumerate(words) if i["start"] == token["characterOffsetBegin"] and i["word"] == token["word"]), None)
					if index != None:
						num_remaining = len(sentence["tokens"])-1 - i
						num_remaining = num_remaining if num_remaining < 3 else 2
						word = words[index]
						if word["NER_token"]:
							# location word
							if word["NER_token"]["ner"] == "LOCATION":
								if word["word"] in destination:
								 	word["query"] = destination
								 	#word["query"] = word["word"]
								else:
								 	word["query"] = assemble_loc(words[index:index+num_remaining])
								locs.append(word)
							# proper noun
							elif word["NER_token"]["pos"] == "NNP" and word["word"] not in destination:
								word["query"] = ""
								#num_before = i if i < 3 and i > 0 else 3
								num_before = 3 if i >= 3 else i
								#word["query"] += assemble_propernoun(words[index-num_before:index+num_remaining], num_before) 
								word["query"] += assemble_propernoun(sentence["tokens"][i-num_before:i+num_remaining], num_before) 
								nouns.append(word)
							# non-proper noun but potentially significant noun phrase
							elif word["NER_token"]["pos"] == "NN":
								word["query"] = ""
								num_before = 3 if i >= 3 else i
								#word["query"] += assemble_nounphrase(words[index-num_before:index+num_remaining], num_before) 
								word["query"] += assemble_propernoun(sentence["tokens"][i-num_before:i+num_remaining], num_before) 
								nouns.append(word)
				# done iterating over tokens
				sorted_nouns = sorted(nouns, key=lambda x:x["tfidf_score"], reverse=True)
				sorted_locs = sorted(locs, key=lambda x:x["tfidf_score"], reverse=True)
				#print sorted_locs
				good_query = False
				backup = ""
				for i,word in enumerate(sorted_nouns):
					if len(queries)> 0 and (queries[-1]["start"] +2) < word["start"]:
						if word["tfidf_score"] > 0.18:
							# determine contextualizing location
							location_word = ""
							if word["query"][len(word["query"])-1] != " ":
								word["query"] += " "
							if len(sorted_locs) > 0:
								if word["NER_token"]["ner"] != "LOCATION":
									word["query"] += sorted_locs[0]["query"]
								location_word = sorted_locs[0]["query"]
							else:
								word["query"] += destination
								location_word = destination
							# determine api
							if location_word.lower().strip() not in location_words:
								word["api"] = "maps"
								#location_words.add(location_word.lower().strip())
							else:
								word["api"] = "images"
							# determine whether to add it to entities to visualize
							if word["query"].lower().strip() not in query_words:
								if len(queries) == 0 or queries[-1]["gentle_token"]["case"] != "success":
									query_words.append(word["query"].lower().strip())
									queries.append(word)
								elif word["gentle_token"]["case"] == "success" and (queries[-1]["gentle_token"]["start"] +4) < word["gentle_token"]["start"]:
									query_words.append(word["query"].lower().strip())
									queries.append(word)
								good_query = True
								break
							else:
								backup = word
				if not good_query:
					if backup != "":
						if len(queries) == 0 or queries[-1]["gentle_token"]["case"] != "success":
							query_words.append(backup["query"].lower().strip())
							queries.append(backup)
						elif backup["gentle_token"]["case"] == "success" and (queries[-1]["gentle_token"]["start"] +4) < backup["gentle_token"]["start"]:
							query_words.append(backup["query"].lower().strip())
							queries.append(backup)
					elif len(sorted_locs) > 0:
						if len(queries) == 0 or queries[-1]["gentle_token"]["case"] != "success": 
							sorted_locs[0]["api"] = "maps" if sorted_locs[0]["query"].lower().strip() not in location_words else "images"
							query_words.append(sorted_locs[0]["query"].lower().strip())
							location_words.add(sorted_locs[0]["query"].lower().strip())
							queries.append(sorted_locs[0])
						elif sorted_locs[0]["gentle_token"]["case"] == "success" and (queries[-1]["gentle_token"]["start"] +4) < sorted_locs[0]["gentle_token"]["start"]:
							sorted_locs[0]["api"] = "maps" if sorted_locs[0]["query"].lower().strip() not in location_words else "images"
							query_words.append(sorted_locs[0]["query"].lower().strip())
							location_words.add(sorted_locs[0]["query"].lower().strip())
							queries.append(sorted_locs[0])
			# done iterating over sentences
			pp.pprint([(word['query'], word['api'], word['start']) for word in queries])
			return queries


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('location')
	args = parser.parse_args()
	location = args.location
	get_entities(location)
