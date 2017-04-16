from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords as stop_words # http://www.nltk.org/book/ch02.html
from nltk.corpus import reuters as rt
from nltk.corpus import gutenberg as gt
from nltk.corpus import brown
import nltk.tokenize.texttiling
from gensim import corpora, models, utils
import json
import re
import codecs 

tokenizer = RegexpTokenizer(r'[a-zA-Z]+\'[a-zA-Z]+|[a-zA-Z]+')
untrimmed_docs = [] # uncleaned documents, which we need when just examining the word
docs = [] 	# all the cleaned, tokenized documents

def compile_stopwords():
	_stopwords = stop_words.words('english') # from nltk
	more_stopwords = open('data/stopwords.txt', 'r').readlines() # our own list of stopwords
	for word in more_stopwords:
		_stopwords.append(word.rstrip('\r\n'))
	return _stopwords

stopwords = compile_stopwords()

def clean_text(raw):
	raw = raw.lower()
	tokens = tokenizer.tokenize(raw)
	stopped_tokens = [i for i in tokens if i not in stopwords and i.isalpha()]
	return stopped_tokens

def create_dictionary(data, corpus):
	# for p in data.split('\r\n'):
	# 	untrimmed_docs.append(p)
	# 	docs.append(clean_text(p))
	# untrimmed_docs.append(data)
	docs.append(clean_text(data))
	#tt = nltk.tokenize.texttiling.TextTilingTokenizer()
	#for segment in tt.tokenize(data):
	#	docs.append(clean_text(segment))
	
	if corpus == "gutenberg":
		one_doc = []
		for i in gt.fileids():
			one_doc = one_doc + [x.lower() for x in rt.words(i) if not x.lower() in stopwords]
			#docs.append(cleaned_doc)
		docs.append(one_doc)
	if corpus == "reuters":
		one_doc = list()
		for i in rt.fileids():
			#cleaned_doc = [x.lower() for x in rt.words(i) if not x.lower() in stopwords]
			#docs.append(cleaned_doc)
			one_doc = list(set(one_doc + [x.lower() for x in rt.words(i) if not x.lower() in stopwords]))
		docs.append(one_doc)
	if corpus == "brown":
		categories = ['adventure', 'belles_lettres', 'editorial', 'fiction', 'government', 'hobbies', 'humor', 'learned', 'lore', 'mystery', 'news', 'religion', 'reviews', 'romance', 'science_fiction']
		#categories = ['adventure', 'editorial', 'fiction', 'hobbies', 'learned', 'mystery', 'news', 'religion', 'reviews', 'romance', 'science_fiction']
		#for c in categories:
		#	cleaned_doc = [x.lower() for x in brown.words(categories=c) if not x.lower() in stopwords]
		#	docs.append(cleaned_doc)
		cleaned_doc = [x.lower() for x in brown.words(categories=categories) if not x.lower() in stopwords]
		docs.append(cleaned_doc)
	my_dictionary = corpora.Dictionary(docs)
	print my_dictionary
	print len(docs)
	return my_dictionary

def create_corpus(my_dictionary):
	return [my_dictionary.doc2bow(doc) for doc in docs]

def generate_tfidf(data, corpus):
	scored_transcript = []
	my_dictionary = create_dictionary(data, corpus)
	my_corpus = create_corpus(my_dictionary) # convert tokenized documents into a document-term matrix
	tfidf = models.tfidfmodel.TfidfModel(my_corpus)
	corpus_tfidf = tfidf[my_corpus]

	# tt = nltk.tokenize.texttiling.TextTilingTokenizer()
	# num_tiles = len(tt.tokenize(data))

	# for i in range(0,num_tiles):
	scores = map(lambda x: (my_dictionary[x[0]], x[1]), corpus_tfidf[0])
	beg_of_doc = data.index(data)
	for m in re.finditer(ur'(\w|\'\w)+', data, re.UNICODE):
		start, end = m.span()
		word = m.group().encode('utf-8')
		score = next((x[1] for x in scores if x[0] == word.lower()), 0)
		#if score != 0:
		scored_transcript.append({
			"word": word,
			"start": start + beg_of_doc,
			"end": end + beg_of_doc,
			"tfidf_score": score
		})

	sortedlist = sorted(scored_transcript, key=lambda x:x['tfidf_score'], reverse=True)
	toplist = []
	idx = 0
	#while len(toplist) < 20:
	while len(toplist) < 100:
		if sortedlist[idx]["word"].lower() not in toplist:
			toplist.append(sortedlist[idx]["word"].lower())
			print sortedlist[idx]["word"].lower(), sortedlist[idx]["tfidf_score"]
		idx += 1

	return scored_transcript