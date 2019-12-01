import numpy as np # for fast array ops
from . import common as lib
from .model_manager import ModelManager
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class ConceptRecognizer(ModelManager):
	doc_list = None
	query_cache = {}
	
	def __init__(self, group_id, model_options):
		self.use_tf_model = model_options['tf_model'] is not None
		super().__init__(tf_model=model_options['tf_model'])
		self.log = model_options['log']
		self.group_id = group_id
		self.cache_queries = model_options['cache_queries']
		self.with_stemmed_tfidf = model_options['with_stemmed_tfidf']
		self.with_semantic_shifting = model_options['with_semantic_shifting']
		self.with_topic_scaling = model_options['with_topic_scaling']
		self.with_document_log_length_scaling = model_options['with_document_log_length_scaling']
		self.with_centered_similarity = model_options['with_centered_similarity']
		self.with_tfidf_similarity = model_options['with_tfidf_similarity']
		self.documents, self.target_size = self.get_documents(self.group_id)
		tfidf = self.prepare_tfidf()
		self.spacy_lemmatized_documents, (self.dictionary, self.tfidf_model, self.tfidf_corpus_similarities) = tfidf
		self.populate_cache()
			
	def populate_cache(self):
		# Cache
		if self.use_tf_model:
			all_documents = [doc for group in self.get_all_documents() for doc in group]
			missing_documents = [doc for doc in all_documents if doc not in self.docvec_dict]
			if len(missing_documents) > 0:
				self.cache_docvecs(missing_documents)
			self.corpus_document_embeddings = [self.docvec_dict[q] for q in self.documents]
		
	def prepare_tfidf(self):
		self.use_docvec = self.with_semantic_shifting or self.with_topic_scaling
		if self.log:
			print('with_stemmed_tfidf',self.with_stemmed_tfidf)
			print('with_semantic_shifting',self.with_semantic_shifting)
			print('with_topic_scaling',self.with_topic_scaling)
			print('with_document_log_length_scaling',self.with_document_log_length_scaling)
		# Process the whole corpus: removing upper-cases, performing tokenization, etc..
		documents = [self.format_query(d) for d in self.documents]
		# Get lemmatized documents
		lemmatized_documents = [self.lemmatize_spacy_document(doc) for doc in documents]
		if self.log:
			print('lemmatized_documents', lemmatized_documents)
		spacy_lemmatized_documents = [self.nlp(lib.get_document_from_words_vector(doc)) for doc in lemmatized_documents]
		if self.with_stemmed_tfidf:
			stemmed_documents = [lib.get_stemmed_document_from_words_vector(doc) for doc in lemmatized_documents]
			if self.log:
				print('stemmed_documents', stemmed_documents)
		# Build tf-idf model and similarities
		dictionary, tfidf_model, tfidf_corpus_similarities = lib.build_tfidf(
			words_vector=stemmed_documents if self.with_stemmed_tfidf else lemmatized_documents,
			very_big_corpus=False
		)
		if self.log:
			print("Number of words in dictionary:",len(dictionary))
		return spacy_lemmatized_documents, (dictionary, tfidf_model, tfidf_corpus_similarities)
	
	def get_all_documents(self):
		return [self.get_documents(id)[0] for id in range(len(self.doc_list))]
	
	def get_documents(self, group_id):
		# Build the joint documents set and print some statistics
		documents = [indicator[1] for indicator in self.doc_list[group_id]] 
		if self.log:
			print("Number of documents:",len(documents))
		return documents, len(documents)
	
	def lemmatize_spacy_document(self, doc):
		return [
			token.lemma_ 
			for token in doc
			if not (token.is_stop or token.is_punct)
		]
	
	def format_query(self, query, manipulator=lambda x: x.lower()):
		if self.cache_queries:
			if query in self.query_cache:
				if self.log:
					print('Concept_Recognizer.format_query: using query in cache')
				return self.query_cache[query]
			# Save the original query before changing it, we will use it as key for the caching system
			original_query = query
		# Format/normalize the query
		query = manipulator(query)
		result = self.nlp(query)
		if self.cache_queries:
			self.query_cache[original_query] = result
		return result
	
	def get_docvec_similarity(self, queries):
		missing_queries = [q for q in queries if q not in self.docvec_dict] 
		if len(missing_queries) > 0:
			embeddings = self.embed(missing_queries)
			self.docvec_dict.update({doc:vec for doc,vec in zip(missing_queries, embeddings)})
		query_embeddings = [self.docvec_dict[q] for q in queries]
		cosine_similarities = cosine_similarity(query_embeddings, self.corpus_document_embeddings)
		clip_cosine_similarities = np.clip(cosine_similarities, -1.0, 1.0)
		#=======================================================================
		# sim_scores = 1.0 - np.arccos(clip_cosine_similarities)
		# positive_scores = np.maximum(0, sim_scores)
		# positive_cosine_similarities = np.cos(1 - positive_scores)
		# return positive_cosine_similarities
		#=======================================================================
		return clip_cosine_similarities
	
	def get_combined_wordvec_similarity(self, lemmatized_query, combination_fn=np.average):
		spacy_lemmatized_query = self.nlp(lib.get_document_from_words_vector(lemmatized_query))
		return np.array([spacy_lemmatized_query.similarity(doc) for doc in self.spacy_lemmatized_documents])
	
	def get_query_similarity(self, query):
		original_query = query
		# Get the filtered query (Document object built using lemmas)
		query = self.format_query(query)
		# Get the lemmatized query
		lemmatized_query = self.lemmatize_spacy_document(query)
		# Get the stemmed query for tf-idf
		if self.with_stemmed_tfidf:
			stemmed_query = lib.get_stemmed_document_from_words_vector(lemmatized_query)
		if self.log:
			print('lemmatized_query', lemmatized_query)
			if self.with_stemmed_tfidf:
				print('stemmed_query', stemmed_query)
		similarity_dict = {}
		# Get tf-idf and docvec similarities
		similarity_dict['tfidf'] = lib.get_query_tfidf_similarity(stemmed_query if self.with_stemmed_tfidf else lemmatized_query, self.dictionary, self.tfidf_model, self.tfidf_corpus_similarities)
		# Group by sub-corpus the similarities 
		similarity_dict['tfidf'] = np.reshape(similarity_dict['tfidf'], [-1,self.target_size])
		if self.use_docvec:
			if self.use_tf_model:
				# Get docvec similarity
				similarity_dict['docvec'] = self.get_docvec_similarity(queries=[original_query])
				similarity_dict['docvec'] = np.reshape(similarity_dict['docvec'], [-1,self.target_size]) # Group by sub-corpus the similarities
			# Get averaged wordvec similarity
			similarity_dict['combined_wordvec'] = self.get_combined_wordvec_similarity(lemmatized_query, combination_fn=np.average)
			similarity_dict['combined_wordvec'] = np.reshape(similarity_dict['combined_wordvec'], [-1,self.target_size]) # Group by sub-corpus the similarities 
			# Get the corpus similarity for every sub-corpus, by averaging the docvec similarities of every sub-corpus
			similarity_dict['corpus'] = lib.get_corpus_similarity(similarity_dict['combined_wordvec'])
			similarity_dict['corpus'] = np.expand_dims(similarity_dict['corpus'], -1) # expand_dims because we have sub-corpus

		# Get the weighted similarity
		docvec_similarity = similarity_dict.get('docvec' if self.use_tf_model else 'combined_wordvec', None)
		tfidf_similarity = similarity_dict.get('tfidf', None) if self.with_tfidf_similarity else docvec_similarity
		similarity_dict['weighted'] = lib.get_weighted_similarity(
			tfidf_similarity = tfidf_similarity, 
			docvec_similarity = docvec_similarity, 
			corpus_similarity = similarity_dict.get('corpus', None), 
			query_length = len(lemmatized_query),
			with_semantic_shifting = self.with_semantic_shifting,
			with_topic_scaling = self.with_topic_scaling,
			with_document_log_length_scaling = self.with_document_log_length_scaling
		)
		# Sum the weighted similarity across sub-corpus
		similarity_dict['weighted'] = np.sum(similarity_dict['weighted'], 0)
		# Center the weighted_similarity vector
		if self.with_centered_similarity:
			similarity_dict['weighted'] = lib.get_centered_similarity(similarity_dict['weighted'])
		return similarity_dict
	
	def get_similarity_ranking(self, similarities):
		return np.argsort(similarities)[::-1]%self.target_size
	
	def get_index_of_most_similar_documents(self, similarities, size=None, threshold=0):
		doc_list = self.doc_list[self.group_id]
		final_ranking = self.get_similarity_ranking(similarities)
		index_list = []
		found_all_indices = False
		i = 0
		while not found_all_indices:
			if similarities[final_ranking[i]] >= threshold:
				best = final_ranking[i]
				index_list.append({'id':doc_list[best][0], 'index':int(best), 'similarity':float(similarities[best])})
				i += 1
				found_all_indices = i >= len(final_ranking) or (size is not None and len(index_list) >= size)
			else:
				found_all_indices = True
		return index_list

