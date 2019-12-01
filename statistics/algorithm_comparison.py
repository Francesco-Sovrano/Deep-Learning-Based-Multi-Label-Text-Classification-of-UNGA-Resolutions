import sys
_, test_set, figure_path = sys.argv

class_count = 18
experiments_count = 11
max_threshold = 3
threshold_multiplier = max_threshold/(experiments_count-1)
algorithms = {
	'AWE': {
		'tf_model':None,
		'concat_target_definitions':True,
		'with_semantic_shifting':True,
		'with_topic_scaling':False,
		'with_document_log_length_scaling':True,
		'with_stemmed_tfidf':True,
		'with_centered_similarity':True,
		'with_tfidf_similarity':False,
		'cache_queries':False,
		'log':False
	},
	'USE-Transformer': {
		'tf_model':'USE_Transformer',
		'concat_target_definitions':True,
		'with_semantic_shifting':True,
		'with_topic_scaling':False,
		'with_document_log_length_scaling':True,
		'with_stemmed_tfidf':True,
		'with_centered_similarity':True,
		'with_tfidf_similarity':False,
		'cache_queries':False,
		'log':False
	},
	'USE-DAN': {
		'tf_model':'USE_DAN',
		'concat_target_definitions':True,
		'with_semantic_shifting':True,
		'with_topic_scaling':False,
		'with_document_log_length_scaling':True,
		'with_stemmed_tfidf':True,
		'with_centered_similarity':True,
		'with_tfidf_similarity':False,
		'cache_queries':False,
		'log':False
	},
	#===========================================================================
	# 'USE-DAN with Topic Weighting': {
	# 	'tf_model':'USE_DAN',
	# 	'concat_target_definitions':True,
	# 	'with_semantic_shifting':True,
	# 	'with_topic_scaling':True,
	# 	'with_document_log_length_scaling':True,
	# 	'with_stemmed_tfidf':True,
	# 	'with_centered_similarity':True,
	# 	'with_tfidf_similarity':False,
	# 	'cache_queries':False,
	# 	'log':False
	# },
	#===========================================================================
	'CDM-Transformer': {
		'tf_model':'USE_Transformer',
		'concat_target_definitions':True,
		'with_semantic_shifting':True,
		'with_topic_scaling':True,
		'with_document_log_length_scaling':True,
		'with_stemmed_tfidf':True,
		'with_centered_similarity':True,
		'with_tfidf_similarity':True,
		'cache_queries':False,
		'log':False
	},
	'CDM-DAN': {
		'tf_model':'USE_DAN',
		'concat_target_definitions':True,
		'with_semantic_shifting':True,
		'with_topic_scaling':True,
		'with_document_log_length_scaling':True,
		'with_stemmed_tfidf':True,
		'with_centered_similarity':True,
		'with_tfidf_similarity':True,
		'cache_queries':False,
		'log':False
	},
	'CDM-AWE': {
		'tf_model':None,
		'concat_target_definitions':True,
		'with_semantic_shifting':True,
		'with_topic_scaling':True,
		'with_document_log_length_scaling':True,
		'with_stemmed_tfidf':True,
		'with_centered_similarity':True,
		'with_tfidf_similarity':True,
		'cache_queries':False,
		'log':False
	},
	#===========================================================================
	# 'CDM without Stemming': {
	# 	'tf_model':'USE_DAN',
	# 	'concat_target_definitions':True,
	# 	'with_semantic_shifting':True,
	# 	'with_topic_scaling':True,
	# 	'with_document_log_length_scaling':True,
	# 	'with_stemmed_tfidf':False,
	# 	'with_centered_similarity':True,
	# 	'with_tfidf_similarity':True,
	# 	'cache_queries':False,
	# 	'log':False
	# },
	# 'CDM-Transformer-NoTargetDefinitions': {
	# 	'tf_model':'USE_Transformer',
	# 	'concat_target_definitions':False,
	# 	'with_semantic_shifting':True,
	# 	'with_topic_scaling':True,
	# 	'with_document_log_length_scaling':True,
	# 	'with_stemmed_tfidf':True,
	# 	'with_centered_similarity':True,
	# 	'with_tfidf_similarity':True,
	# 	'cache_queries':False,
	# 	'log':False
	# },
	# 'CDM-DAN-NoTargetDefinitions': {
	# 	'tf_model':'USE_DAN',
	# 	'concat_target_definitions':False,
	# 	'with_semantic_shifting':True,
	# 	'with_topic_scaling':True,
	# 	'with_document_log_length_scaling':True,
	# 	'with_stemmed_tfidf':True,
	# 	'with_centered_similarity':True,
	# 	'with_tfidf_similarity':True,
	# 	'cache_queries':False,
	# 	'log':False
	# },
	#===========================================================================
}

def test_algorithm(item):
	algorithm_name, model_options = item
	import json
	import numpy as np
	from core import GoalInterface
	import random

	#print(f'Loading JSON test-set {test_set}..')
	with open(test_set) as f:
		sample_data = list(json.load(f))
	#print(f'Test-set size: {len(sample_data)}')
	#print('Classifying test-set..')
	doc_list = [paragraph['paragraph'] for paragraph in sample_data]
	#print('Building annotation set..')
	annotations = [paragraph['annotation'] for paragraph in sample_data]
	goal_annotations = [[p[0] for p in group if len(p) > 0] for group in annotations]
	target_annotations = [[p[1] for p in group if len(p) > 0] for group in annotations]
	
	docvec_collection = {}
	
	#print(f'Testing algorithm {algorithm_name}..')
	experiments = [ 
		{
			'model_options': model_options, 
			'threshold': threshold_multiplier*i
		} 
		for i in range(experiments_count) 
	]
	
	results = []
	for id,exp in enumerate(experiments):
		interface = GoalInterface(model_options=exp['model_options'])
		tf_model = exp['model_options']['tf_model']
		if tf_model is not None:
			if tf_model not in docvec_collection:
				#print(f'Caching tf model {tf_model}..')
				interface.model.cache_docvecs(doc_list)
				docvec_collection[tf_model] = interface.model.docvec_dict
			else:
				interface.model.docvec_dict = docvec_collection[tf_model]
	
		print(f'Performing experiment {algorithm_name}.{id}..')
		goal_predictions = [interface.get_goal(paragraph['paragraph'], exp['threshold']) for paragraph in sample_data]
		#predictions = [interface.get_sdg(paragraph['paragraph'], exp['threshold']) for paragraph in sample_data]
		#goal_predictions = [[p[0] for p in group if len(p) > 0] for group in predictions]
		#target_predictions = [[p[1] for p in group if len(p) > 0] for group in predictions]
	
		#print('----------Goal Classifier Evaluation----------')
		classification_result = [
			{str(p['id']): p['similarity'] for p in prediction} 
			if len(prediction)>0 else 
			{'0': 1}
			for prediction in goal_predictions
		]
		annotations_list = [
			[str(p) for p in annotation]
			for annotation in goal_annotations
		]
	
		results.append((classification_result, annotations_list))
	return (algorithm_name,results)

##################### Perform experiments, in parallel #####################
# Libraries
import pickle
import os.path

# get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# create cache directory if it does not exist
cache_dir = os.path.join(current_dir,'cache')
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
# load or build cache
cache_file = f'cache_{test_set.replace("/","")}.pkl'
cache_path = os.path.join(cache_dir,cache_file)
print(f'Cache file in {cache_path}.')
if os.path.isfile(cache_path):
	with open(cache_path,'rb') as f:
		experiment_labels_list = pickle.load(f)
else:
	import multiprocessing as mp
	pool = mp.Pool(processes=len(algorithms))
	experiment_labels_list = pool.map(test_algorithm, algorithms.items())
	with open(cache_path,'wb') as f:
		pickle.dump(experiment_labels_list,f)

##################### Compute statistics #####################
# Libraries
import numpy as np
import pandas as pd	
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, balanced_accuracy_score, matthews_corrcoef
from sklearn.metrics import coverage_error, label_ranking_average_precision_score, label_ranking_loss, roc_auc_score, hamming_loss

statistics_list = []
for id, (algorithm_name, experiment_labels) in enumerate(experiment_labels_list):
	experiment_results = {}
	experiments_support = []
	for ex,(classification_result, annotations_list) in enumerate(experiment_labels):
		# '------Multiclass Evaluation on best-ranked in Multilabel Intersection------'
		y_test = []
		y_predicted = []
		for annotations,prediction_dict in zip(annotations_list,classification_result):
			prediction = list(prediction_dict.keys())
			intersection_list = list(set(annotations).intersection(set(prediction)))
			if len(intersection_list) > 0:
				#===============================================================
				# y = random.choice(intersection_list)
				#===============================================================
				y = intersection_list[0]
				y_predicted.append(y)
				y_test.append(y)
			else:
				y_predicted.append(prediction[0])
				y_test.append(annotations[0])
		
		support_dict = {str(v):0 for v in range(class_count)}
		for y in y_test:
			support_dict[y] += 1
		experiments_support.append(np.array(list(support_dict.values())))
		
		best_ranked_multiclass = { 
			'Best-Ranked Accuracy': accuracy_score(y_test, y_predicted),
			#'Balanced Accuracy': balanced_accuracy_score(y_test, y_predicted),
			#'Support': precision_recall_fscore_support(y_test, y_predicted)[-1],
			#'Best-Ranked F1 Macro': precision_recall_fscore_support(y_test, y_predicted, average='macro')[2],
			#'Best-Ranked F1 Micro': precision_recall_fscore_support(y_test, y_predicted, average='micro')[2],
			'Best-Ranked F1 Weighted': precision_recall_fscore_support(y_test, y_predicted, average='weighted')[2],
			#'Best-Ranked MCC': matthews_corrcoef(y_test, y_predicted)
		}
		
		# '------Multilabel Evaluation------'
		y_true = np.array([
			[1 if str(l) in a else 0 for l in range(class_count)]
			for a in annotations_list
		])
		y_predicted = np.array([
			[1 if str(l) in prediction_dict else 0 for l in range(class_count)] 
			for prediction_dict in classification_result
		])
		y_score = np.array([
			[prediction_dict.get(str(l),0) for l in range(class_count)]
			for prediction_dict in classification_result
		])
		
		average_true_labels = np.average(np.sum(y_true,-1))
		multilabel = { 
			#'Average True Labels': average_true_labels,
			#'Coverage Ratio': average_true_labels/coverage_error(y_true, y_score),
			'Label Ranking Average Precision Score': label_ranking_average_precision_score(y_true, y_score),
			#'Label Ranking Loss': label_ranking_loss(y_true, y_score),
			#'Hamming Loss': hamming_loss(y_true, y_score),
			#'F1 Macro': precision_recall_fscore_support(y_true, y_predicted, average='macro')[2],
			#'F1 Micro': precision_recall_fscore_support(y_true, y_predicted, average='micro')[2],
			#'Precision Samples': precision_recall_fscore_support(y_true, y_predicted, average='samples')[0],
			#'Recall Samples': precision_recall_fscore_support(y_true, y_predicted, average='samples')[1],
			#'F1 Samples': precision_recall_fscore_support(y_true, y_predicted, average='samples')[2],
			#'Precision': precision_recall_fscore_support(y_true, y_predicted, average='weighted')[0],
			#'Recall': precision_recall_fscore_support(y_true, y_predicted, average='weighted')[1],
			'F1 Weighted': precision_recall_fscore_support(y_true, y_predicted, average='weighted')[2],
		}
		all = {}
		all.update(best_ranked_multiclass)
		all.update(multilabel)
		experiment_results.update({round(threshold_multiplier*ex,2): all})
	
	np.set_printoptions(suppress=True)
	print(f"{algorithm_name}'s Average BR Support:", np.average(np.array(experiments_support), 0))
	
	df = pd.DataFrame.from_dict(data=experiment_results, orient='index')
	df = df.reset_index()
	df.columns = ['Threshold' if x=='index' else x for x in df.columns]
	df = df.melt('Threshold', var_name='Statistic', value_name='Score')
	statistics_list.append((algorithm_name,df))
	
df = {algorithm_name: df for algorithm_name, df in statistics_list if algorithm_name in algorithms}
df = pd.concat(df)
df = df.reset_index()
del df['level_1']
df.columns = ['Experiment' if x=='level_0' else x for x in df.columns]
print('--Data--')
print(df)

##################### Create plot #####################
# Libraries
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image

#sns.set(font_scale=3)
sns.set_context('paper')
#sns.set_style('darkgrid')
#plt.rcParams["axes.grid"] = True
#plt.rcParams.update({'font.size': 24})

g = sns.FacetGrid(
	data=df, 
	col='Statistic', 
	ylim=(0,1),
	#hue='Experiment', 
	sharey=False, 
	sharex=False, 
	col_wrap=2,
	height=4, 
	aspect=1,
	legend_out=False,
)
def labeled_pointplot(x,y,hue, **kwargs):
	hue_order = kwargs.get("hue_order", None)
	palette = kwargs.get("palette", None)
	
	ax = sns.pointplot(x,y,hue, linestyles=['--']*len(hue_order), **kwargs)
	ylim_min, ylim_max = ax.get_ylim()
	ylim_delta = ylim_max - ylim_min
	for o,h in enumerate(hue_order):
		y_hue_values = [v for v,c in zip(y.values,hue.values) if c ==h]
		best_y = max(y_hue_values)
		plt.axhline(best_y, color=palette[o], linestyle='-')
		yticks = list(ax.get_yticks())
		closest_tick = min(yticks, key=lambda x: np.abs(x-best_y))
		if np.abs(best_y-closest_tick) > ylim_delta*0.03:
			yticks.append(round(best_y,2))
		ax.set_yticks(yticks)

experiment_list = list(algorithms.keys())
g = g.map(
	labeled_pointplot, 'Threshold', 'Score', 'Experiment', 
	palette=sns.color_palette('colorblind',len(experiment_list)),
	#palette=sns.cubehelix_palette(len(experiment_list), start=.5, rot=-.75), 
	hue_order=experiment_list,
	#markers=["o","s","<",'$f$',">"],
)
# Add legend
g = g.add_legend()
# Save figure
g.savefig(figure_path)
print(f'Figure saved at {figure_path}')
