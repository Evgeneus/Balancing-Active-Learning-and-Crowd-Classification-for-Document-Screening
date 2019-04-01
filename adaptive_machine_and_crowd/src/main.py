import sys, os
path_to_project = os.path.realpath('main.py')[:-38]
# path_to_project = '/home/evgeny.krivosheev/Active-Hybrid-Classificatoin_MultiPredicate/'
sys.path.append(path_to_project)

from modAL.uncertainty import uncertainty_sampling
from adaptive_machine_and_crowd.src.utils import random_sampling, objective_aware_sampling

from adaptive_machine_and_crowd.src.experiment_handler import run_experiment
import numpy as np

'''
    Parameters for active learners:
    'n_instances_query': num of instances for labeling for 1 query,
    'size_init_train_data': initial size of training dataset,
    'sampling_strategies': list of active learning sampling strategies

    Classification parameters:
    'screening_out_threshold': threshold to classify a document OUT,
    'beta': beta for F_beta score,
    'lr': loss ration for the screening loss

    Experiment parameters:
    'experiment_nums': reputation number of the whole experiment,
    'dataset_file_name ': file name of dataset,
    'predicates': predicates will be used in experiment,
    'B': budget available for classification,
    'B_al_prop': proportion of B for training machines (AL-Box)
'''

if __name__ == '__main__':
    # datasets = 'amazon', 'amazon_binary', 'crisis'
    dataset = 'crisis'
    if dataset == 'amazon':
        # AMAZON DATASET
        predicates = ['is_negative', 'is_book']
        dataset_file_name = '1k_amazon_reviews_crowdsourced_lemmatized.csv'
        dataset_size = 1000
        crowd_acc = {predicates[0]: [0.94, 0.94], predicates[1]: [0.94, 0.94]}
    elif dataset == 'amazon_binary':
        # AMAZON BINARY DATASET
        predicates = ['Y']
        dataset_file_name = '1k_amazon_reviews_crowdsourced_lemmatized.csv'
        dataset_size = 1000
        crowd_acc = {predicates[0]: [0.93, 0.93]}
    elif dataset == 'crisis':
        predicates = ['eye_witness', 'informative', 'damage']
        dataset_file_name = 'crisis-lemmatized_witness_inf_damage.csv'
        dataset_size = 1943
        crowd_acc = {predicates[0]: [0.87, 0.87], predicates[1]: [0.85, 0.85], predicates[2]: [0.90, 0.90]}
    else:
        exit(1)

    # Parameters for active learners
    n_instances_query = 100
    size_init_train_data = 20

    # Classification parameters
    screening_out_threshold = 0.99  # for SM-Run
    stop_score = 50  # for SM-Run Algorithm
    beta = 1
    lr = 5

    # Experiment parameters
    experiment_nums = 10
    policy_switch_point = np.arange(0., 1.01, 0.1)
    budget_per_item = np.arange(1, 9, 1)  # number of votes per item we can spend per item on average
    crowd_votes_per_item_al = 3  # for Active Learning annotation

    for sampling_strategy in [random_sampling, uncertainty_sampling]:
        print('{} is Running!'.format(sampling_strategy.__name__))
        params = {
            'dataset_file_name': dataset_file_name,
            'n_instances_query': n_instances_query,
            'size_init_train_data': size_init_train_data,
            'screening_out_threshold': screening_out_threshold,
            'beta': beta,
            'lr': lr,
            'experiment_nums': experiment_nums,
            'predicates': predicates,
            'sampling_strategy': sampling_strategy,
            'crowd_acc': crowd_acc,
            'crowd_votes_per_item_al': crowd_votes_per_item_al,
            'policy_switch_point': policy_switch_point,
            'budget_per_item': budget_per_item,
            'stop_score': stop_score,
            'dataset_size': dataset_size,
            'path_to_project': path_to_project
        }

        run_experiment(params)
        print('{} is Done!'.format(sampling_strategy.__name__))
