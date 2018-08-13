import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer


# load and vectorize data
def load_vectorize_data(file_name, predicates, seed):
    df = pd.read_csv('../data/ohsumed_data/{}'.format(file_name))
    df_screening_pos = df.loc[df['Y'] == 1]
    df_screening_neg = df.loc[df['Y'] == 0]

    X_screening_pos = df_screening_pos['tokens'].values
    X_screening_neg = df_screening_neg['tokens'].values
    X = np.append(X_screening_pos, X_screening_neg)

    y_screening = np.append(np.ones(X_screening_pos.shape[0]),
                            np.zeros(X_screening_neg.shape[0]))

    y_predicate = {}  # gt labels per predicate
    for pr in predicates:
        y_predicate[pr] = np.append(df_screening_pos[pr].values,
                                    df_screening_neg[pr].values)

    # vectorize and transform text
    vectorizer = TfidfVectorizer(lowercase=False, max_features=2000, ngram_range=(1, 1))
    X = vectorizer.fit_transform(X).toarray()

    # shuffle X, y in unison
    np.random.seed(seed)
    idx = np.random.permutation(y_screening.shape[0])
    X, y_screening = X[idx], y_screening[idx]
    for pr in predicates:
        y_predicate[pr] = y_predicate[pr][idx]

    return X, y_screening, y_predicate


# random sampling strategy for modAL
def random_sampling(_, X, n_instances=1, seed=123):
    np.random.seed(seed)
    query_idx = np.random.randint(X.shape[0], size=n_instances)

    return query_idx, X[query_idx]


# certainty sampling strategy for modAL
def certainty_sampling(classifier, X, n_instances=1, **predict_proba_kwargs):
    prob_in = classifier.predict_proba(X, **predict_proba_kwargs)[:, 1]
    query_idx = np.argpartition(prob_in, -n_instances)[-n_instances:]

    return query_idx, X[query_idx]


# sampling takes into account conjunctive expression of predicates
def objective_aware_sampling(classifier, X, learners_, n_instances=1, **uncertainty_measure_kwargs):
    from modAL.uncertainty import classifier_uncertainty, multi_argmax
    uncertainty = classifier_uncertainty(classifier, X, **uncertainty_measure_kwargs)
    l_prob_in = np.ones(X.shape[0])
    if learners_:
        for l in learners_.values():
            l_prob_in *= l.learner.predict_proba(X)[:, 1]
        uncertainty_weighted = np.power(l_prob_in * uncertainty, 1 / (len(learners_) + 1))
    else:
        uncertainty_weighted = uncertainty

    query_idx = multi_argmax(uncertainty_weighted, n_instances=n_instances)

    return query_idx, X[query_idx]


# transfrom data from k-fold CV and print results in csv
def transform_print(data_df, sampl_strategy, predicates):
    # compute mean and std, and median over k-fold cross validation results
    df_concat = pd.concat(data_df)
    by_row_index = df_concat.groupby(df_concat.index)
    df_means = by_row_index.mean()
    df_std = by_row_index.std()
    df_median = by_row_index.median()

    # form dataframe for printing out in csv
    df_to_print = df_means
    df_to_print.columns = ['num_items_queried', 'precision_mean',
                           'recall_mean', 'f_beta_mean', 'loss_mean']

    df_to_print['precision_median'] = df_median['precision']
    df_to_print['recall_median'] = df_median['recall']
    df_to_print['f_beta_median'] = df_median['f_beta']
    df_to_print['loss_median'] = df_median['loss']

    df_to_print['precision_std'] = df_std['precision']
    df_to_print['recall_std'] = df_std['recall']
    df_to_print['f_beta_std'] = df_std['f_beta']
    df_to_print['loss_std'] = df_std['loss']

    df_to_print['sampling_strategy'] = sampl_strategy
    df_to_print.to_csv('../data/multi_classifier_al/screening_al_{}_{}_certainty.csv'
                       .format(predicates[0], predicates[1]), index=False)
