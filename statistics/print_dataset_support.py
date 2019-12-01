import sys
import json
_, test_set = sys.argv

class_count = 18

with open(test_set) as f:
	sample_data = list(json.load(f))
#print(f'Test-set size: {len(sample_data)}')
#print('Classifying test-set..')
doc_list = [paragraph['paragraph'] for paragraph in sample_data]
#print('Building annotation set..')
annotations = [paragraph['annotation'] for paragraph in sample_data]
goal_annotations = [[p[0] for p in group if len(p) > 0] for group in annotations]
annotations_list = [
	[str(p) for p in annotation]
	for annotation in goal_annotations
]

##################### Compute statistics #####################
# Libraries
import numpy as np
import pandas as pd	
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, balanced_accuracy_score, matthews_corrcoef
from sklearn.metrics import coverage_error, label_ranking_average_precision_score, label_ranking_loss, roc_auc_score, hamming_loss
		
support_dict = {str(v):0 for v in range(class_count)}
for a in annotations_list:
	for y in a:
		support_dict[y] += 1
total_elements = sum(support_dict.values())
for key in support_dict.keys():
	support_dict[key] /= total_elements

for key, value in support_dict.items():
	print(f'Class {key}: {value*100}%')
