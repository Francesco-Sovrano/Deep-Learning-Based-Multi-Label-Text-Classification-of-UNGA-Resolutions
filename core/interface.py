from .sdg_recognizer import SDGRecognizer
from .sdg_target_recognizer import SDGTargetRecognizer
#from .sdg_indicator_recognizer import SDGIndicatorRecognizer

import warnings
warnings.filterwarnings("ignore")

class GoalInterface():
	DEFAULT_OPTIONS = {
		'tf_model':'USE_DAN',
		'concat_target_definitions':True,
		'with_semantic_shifting':True,
		'with_topic_scaling':True,
		'with_document_log_length_scaling':True,
		'with_stemmed_tfidf':True,
		'with_centered_similarity':True,
		'with_tfidf_similarity':True,
		'cache_queries':True,
		'log':False
	}

	def __init__(self, model_options=None):
		if model_options is None:
			model_options = GoalInterface.DEFAULT_OPTIONS

		self.model = SDGRecognizer(model_options)

	def get_goal(self, text, threshold=0.6):
		similarity_dict = self.model.get_query_similarity(text)
		return self.model.get_index_of_most_similar_documents(similarity_dict['weighted'], threshold=threshold)

class GoalTargetInterface():
	
	def __init__(self, goal_options=None, target_options=None):
		self.goal_interface = GoalInterface(goal_options)
		self.model = self.goal_interface.model
		if target_options is None:
			target_options = GoalInterface.DEFAULT_OPTIONS

		self.model_list = [
			SDGTargetRecognizer(group_id=i, model_options=target_options)
			for i in range(self.goal_interface.model.target_size)
		]

	def get_goal_and_target(self, text, goal_threshold=0.6, target_threshold=0.6):
		sdg_list = self.goal_interface.get_goal(text, goal_threshold)
		result = []
		for sdg in sdg_list:
			i = sdg['index']
			tgt_model = self.model_list[i]
			# Compute target similarities
			similarity_dict = tgt_model.get_query_similarity(text)
			target_list = tgt_model.get_index_of_most_similar_documents(similarity_dict['weighted'], threshold=target_threshold)
			result.append((sdg, target_list))
		return result
