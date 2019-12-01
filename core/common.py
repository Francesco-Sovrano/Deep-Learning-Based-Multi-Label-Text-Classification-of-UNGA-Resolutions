import numpy as np # for fast array ops
import gensim # for the tf-idf model
from gensim.test.utils import get_tmpfile
from nltk.stem.snowball import SnowballStemmer # for the tf-idf model <http://www.nltk.org/howto/stem.html>
	
def get_document_from_words_vector(document):
	return u' '.join(document)

def get_stemmed_document_from_words_vector(document):
	stemmer = SnowballStemmer("english")
	return [stemmer.stem(token) for token in document]

def build_tfidf(words_vector, very_big_corpus=False):
	# The code in the following block comes from: https://www.oreilly.com/learning/how-do-i-compare-document-similarity-using-python
	########################## START BLOCK ########################## 
	# Build word dictionary
	dictionary = gensim.corpora.Dictionary(words_vector)
	# Build the Bag-of-Words corpus from lemmatized documents
	corpus = [dictionary.doc2bow(gen_doc) for gen_doc in words_vector]
	# Build the tf-idf model from the corpus 
	tfidf_model = gensim.models.TfidfModel(corpus)
	# Build similarities cache
	# Similarity with cache into temporary file is slower than MatrixSimilarity but it can handle bigger corpus
	if very_big_corpus:
		tfidf_corpus_similarities = gensim.similarities.Similarity(get_tmpfile("index"), tfidf_model[corpus], num_features=len(dictionary))
	else:
		tfidf_corpus_similarities = gensim.similarities.MatrixSimilarity(tfidf_model[corpus], num_features=len(dictionary))
	########################## END BLOCK ##########################
	return dictionary, tfidf_model, tfidf_corpus_similarities

def get_query_tfidf_similarity(words_vector, dictionary, tfidf_model, tfidf_corpus_similarities):
	# Get query BoW (Bag of Words)
	query_bow = dictionary.doc2bow(words_vector)
	# Get query tf-idf
	query_tfidf = tfidf_model[query_bow]
	# Get query similarity vector
	return tfidf_corpus_similarities[query_tfidf]

def get_corpus_similarity(docvec_similarity):
	# Get the topic similarity for every sub-corpus, by averaging the docvec similarities of every sub-corpus
	return np.average(docvec_similarity,-1)

def get_weighted_similarity(tfidf_similarity, docvec_similarity, corpus_similarity, query_length, with_semantic_shifting=True, with_topic_scaling=True, with_document_log_length_scaling=True):
	# Build combined similarity
	weighted_similarity = tfidf_similarity
	
	if with_semantic_shifting:
		weighted_similarity += docvec_similarity
		
	if with_topic_scaling:
		# Get the topic weight
		topic_weight = np.power(corpus_similarity,2)
		# Compute the weighted similarity for every sub-corpus
		# tfidf_similarity is high for a document when the query words and the document words are similar, but tfidf_similarity may be lower when we use words in the synsets
		# in order to address the aforementioned synset-words problem we sum the tfidf_similarity with the corpus_similarity before scaling it by the semantic_weight
		# we scale by the semantic_weight in order to give significantly more similarity to the documents semantically more closer to the query 
		weighted_similarity *= topic_weight
		
	if with_document_log_length_scaling:
		# the bigger the sentence, the (smoothly) lower the weighted_similarity
		# thus we scale the weighted_similarity by the log of the query length
		weighted_similarity *= 1 + np.log2(query_length) # sum 1 to avoid similarity zeroing
		
	return weighted_similarity

def get_centered_similarity(similarities):
	# Center the weighted_similarity vector: Remove the average weighted_similarity
	similarities -= np.average(similarities)
	# Remove negative components, they are useless for our goal
	similarities = np.maximum(similarities, 0)
	return similarities
