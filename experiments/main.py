
from classification_models import auto_knn, auto_random_forest, auto_lr
from classification_models import auto_cnn
from classification_models import auto_resnet
from utils import persist_results, metrics
import os

import numpy as np

from datasets.mfpt import MFPT
#from datasets.paderborn import Paderborn
from datasets.paderborn_paper import Paderborn

def write_in_file(file_name, message):
    with open(file_name, 'a') as file:
        file.write(message)

import time
import functools
def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        write_in_file("execution_time", f"{run_time} s\n")
        return value
    return wrapper_timer

@timer
def run_train_test(classifier, X_train, y_train, X_test):
    classifier.fit(X_train, y_train)
    y_pred = classifier.predict(X_test)
    y_proba = classifier.predict_proba(X_test)
    return y_pred, y_proba

@timer
def experimenter(dataset, clfs, splits):
    print("### Dataset: ", dataset[0], "###")
    write_in_file("execution_time", f"{dataset[0]}\n")
    dataset[1].download()
    results = []
    print("Performing Experiments.")
    for folds in splits:
        for clf in clfs:
            fold_number = 1
            print(folds[0], clf[0])
            write_in_file("execution_time", f"{folds[0]} - {clf[0]}\n")
            for X_train, y_train, X_test, y_test in getattr(dataset[1], folds[1])():
                write_in_file("execution_time", f"{fold_number}: ")
                print("fold_number: ", fold_number)
                y_pred, y_proba = run_train_test(clf[1], X_train, y_train, X_test)
                results.append([dataset[0], folds[0], clf[0], fold_number, y_test, y_pred, y_proba])
                fold_number = fold_number + 1
    saved_results = persist_results.save_results(results)
    metrics.scores(saved_results)


def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    clfs = [#('K-Nearest Neighbors', auto_knn.instantiate_auto_knn()),
            #('Random Forest', auto_random_forest.instantiate_auto_random_forest()),
            ('FaultNet', auto_cnn.instantiate_auto_cnn()),
            #('Logistic Regression', auto_lr.instantiate_auto_lr()),
            #('ResNet', auto_resnet.instantiate_auto_resnet()),
            ]

    splits = [('Kfold', 'kfold'),
              #('StratifiedKfold', 'stratifiedkfold'),
              #('GroupKfold by Acquisition', 'groupkfold_acquisition'),
              #('GroupKfold by Settings', 'groupkfold_settings'),
              #('GroupKfold by Bearings', 'groupkfold_bearings'),
             ]

    dataset = ('Paderborn', Paderborn(bearing_names_file="paderborn_bearings_paper.csv", n_aquisitions=20))
    experimenter(dataset, clfs, splits)


if __name__ == "__main__":
    main()
