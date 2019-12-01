import spacy # for natural language processing
# python3 -m spacy download en_core_web_md
from sklearn.preprocessing import normalize

SPACY_MODEL = 'en_core_web_md'
MODULE_URL = {
	'USE_Transformer': 'https://tfhub.dev/google/universal-sentence-encoder-large/3',
	'USE_DAN': 'https://tfhub.dev/google/universal-sentence-encoder/2'
}

class ModelManager():
	nlp = None
	__tf_placeholders_dict = None
	__session = None
	__docvec_dict = {}
	__tf_model = None
	
	@property
	def docvec_dict(self):
		return ModelManager.__docvec_dict
	
	## the attribute name and the method name must be same which is used to set the value for the attribute
	@docvec_dict.setter
	def docvec_dict(self, var):
		ModelManager.__docvec_dict = var
	
	@staticmethod
	def cache_docvecs(doc_list):
		if ModelManager.__session is not None:
			message_embeddings = ModelManager.embed(doc_list)
			docvec_dict = {doc:vec for doc,vec in zip(doc_list, message_embeddings)}
			ModelManager.__docvec_dict.update(docvec_dict)
	
	@staticmethod
	def load_nlp_model():
		print('Loading spacy model <{}>...'.format(SPACY_MODEL))
		# go here <https://spacy.io/usage/processing-pipelines> for more information about Language Processing Pipeline (tokenizer, tagger, parser, etc..)
		nlp = spacy.load(SPACY_MODEL)
		return nlp
	
	@staticmethod
	def load_tf_model(tf_model):
		import tensorflow as tf
		from tensorflow_hub import Module as TFHubModule
		# Reduce logging output.
		#tf.logging.set_verbosity(tf.logging.ERROR)
		
		# Create graph and finalize (finalizing optional but recommended).
		g = tf.Graph()
		with g.as_default():
			# We will be feeding 1D tensors of text into the graph.
			text_input = tf.placeholder(dtype=tf.string, shape=[None])
			embed = TFHubModule(MODULE_URL[tf_model], trainable=False)
			embedded_text = embed(text_input)
			init_op = tf.group([tf.global_variables_initializer(), tf.tables_initializer()])
		g.finalize() # Finalizes this graph, making it read-only.
		
		# Create session and initialize.
		session = tf.Session(graph=g, config=tf.ConfigProto(use_per_session_threads=False))
		session.run(init_op)
		tf_placeholders = {
			'embedded_text': embedded_text,
			'text_input': text_input
		}
		return tf_placeholders, session
	
	@staticmethod
	def embed(doc_list, norm=None):
		# Feed doc_list into current tf graph
		embedding = ModelManager.__session.run(
			ModelManager.__tf_placeholders_dict['embedded_text'], 
			feed_dict={ModelManager.__tf_placeholders_dict['text_input']: doc_list}
		)
		# Normalize the embeddings, if required
		if norm is not None:
			embedding = normalize(embedding, norm=norm)
		return embedding
	
	def __init__(self, tf_model=None):
		# Load Spacy
		if ModelManager.nlp is None:
			ModelManager.nlp = ModelManager.load_nlp_model()
		# Load TF model
		if tf_model is None:
			__tf_placeholders_dict = None
			__session = None
			__docvec_dict = {}
			__tf_model = None
		elif tf_model != ModelManager.__tf_model:
			if ModelManager.__tf_model is None:
				ModelManager.__tf_model = tf_model
				ModelManager.__tf_placeholders_dict, ModelManager.__session = ModelManager.load_tf_model(tf_model)
			else:
				raise ValueError('Cannot load {} in this process, because {} has been already loaded.'.format(tf_model, ModelManager.__tf_model))
