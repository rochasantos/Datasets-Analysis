
# Change variable use_gpu to 1 when using GPU
use_gpu = 0
from multiprocessing import Process, Queue
Q = Queue()

from classification_models import auto_knn, auto_random_forest, auto_lr, auto_svm, auto_mlp
#from classification_models import auto_faultnet
#from classification_models import auto_cnn
from utils import persist_results, metrics
import os
#from tensorflow import keras
import numpy as np

from datasets.mfpt import MFPT
from datasets.paderborn import Paderborn
from datasets.ottawa import Ottawa
from datasets.cwru import CWRU

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
    if use_gpu == 1:
        Q.put(y_pred)

    y_proba = classifier.predict_proba(X_test)
    if use_gpu == 1:
        Q.put(y_proba)

    return y_pred, y_proba

@timer
def experimenter(source, target, clfs):

    write_in_file("execution_time", f"{target[0]}\n")
    # dataset[1].download()

    print("Performing Experiments.")
    
    X_train, y_train = source[1].load_acquisitions()
    print("### Source: ", source[0], "###")
    y_train[y_train!='N'] = 'F'
    print(f"Labels: {set(y_train)}")
    for label in set(y_train):
        print((f"{label}: {np.sum(y_train==label)}"))
    X_test, y_test = target[1].load_acquisitions()
    print("### Target: ", target[0], "###")
    y_test[y_test!='N'] = 'F'
    print(f"Labels: {set(y_test)}")
    for label in set(y_test):
        print((f"{label}: {np.sum(y_test==label)}"))

    results = []
    for clf in clfs:
        if use_gpu == 1:
            p = Process(target=run_train_test, args=(clf[1], X_train, y_train, X_test))
            p.start()

            y_pred = Q.get()

            y_proba = Q.get()

            p.join()
        else:                        
            y_pred, y_proba = run_train_test(clf[1], X_train, y_train, X_test)

        results.append([target[0], clf[0], y_test, y_pred, y_proba])

    saved_results = persist_results.save_results(results)
    metrics.scores(saved_results)


def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    #### Define experiments classifiers
    clfs = [#('K-Nearest Neighbors', auto_knn.instantiate_auto_knn()),
            ('Random Forest', auto_random_forest.instantiate_auto_random_forest()),
            # ('Logistic Regression', auto_lr.instantiate_auto_lr()),
            # ('SVM', auto_svm.instantiate_auto_svm()),
            # ('MLP', auto_mlp.instantiate_auto_mlp()),
            # ('CNN', auto_cnn.instantiate_auto_cnn()),
            # ('FaultNet', auto_faultnet.instantiate_auto_cnn()),
            ]
   
    

    #### Define experiments data set
    #dataset = ('Paderborn', Paderborn(bearing_names_file="paderborn_bearings.csv", n_aquisitions=20))
    #dataset = ('Paderborn', Paderborn(bearing_names_file="paderborn_bearings_min.csv", n_aquisitions=4))
    source = ('MFPT', MFPT())
    #dataset = ('Ottawa', Ottawa())
    #dataset = ('Ottawa', Ottawa(downsample=True))
    target = ('CWRU', CWRU())
    #dataset = ('CWRU', CWRU(bearing_names_file="cwru_bearings_debug.csv"))

    experimenter(source, target, clfs)


if __name__ == "__main__":
    main()
