from run_tfidf import generate_tfidf
from run_NER import generate_NER
import argparse, codecs, json

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('location')
	parser.add_argument('corpus')
	args = parser.parse_args()
	location = args.location
	corpus = args.corpus
	base = "data/" + location + "/"
	data = codecs.open(base + location + ".txt", 'r', "utf-8").read()
	
	scored_transcript = generate_tfidf(data, corpus)
	tagged_transcript = generate_NER(location)

	with open(base + location + '_gentle_output.json', 'r') as gentle_output:
		gentle_words = json.load(gentle_output)
		for sentence in tagged_transcript["sentences"]:
			for token in sentence["tokens"]:
				tfidf_word_index = next((idx for idx,i in enumerate(scored_transcript) if i["start"] == token["characterOffsetBegin"] and i["word"] == token["word"]), None)
				if tfidf_word_index != None:
					scored_transcript[tfidf_word_index]["NER_token"] = token
					if (scored_transcript[0]["start"] == 0):
						gentle_word = next((i for i in gentle_words["words"] if i["startOffset"] == scored_transcript[tfidf_word_index]["start"] and i["word"] == scored_transcript[tfidf_word_index]["word"]), None)
					else:
						gentle_word = next((i for i in gentle_words["words"] if i["startOffset"] == scored_transcript[tfidf_word_index]["start"]-1 and i["word"] == scored_transcript[tfidf_word_index]["word"]), None)
					scored_transcript[tfidf_word_index]["gentle_token"] = gentle_word

	# if corpus == "reuters":
	# 	with open('data/naples_scored_transcript_REUTERS.json', 'w') as output:
	# 		json.dump(scored_transcript, output, sort_keys=True, indent=4, separators=(',',': '))
	# if corpus == "gutenberg":
	# 	with open('data/naples_scored_transcript_GUTENBERG.json', 'w') as output:
	# 		json.dump(scored_transcript, output, sort_keys=True, indent=4, separators=(',',': '))
	if corpus == "brown":
		with open(base + location + '_scored_transcript_BROWN.json', 'w') as output:
			json.dump(scored_transcript, output, sort_keys=False, indent=4, separators=(',',': '))