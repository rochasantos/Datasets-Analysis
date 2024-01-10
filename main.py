
# Change variable use_gpu to 1 when using GPU
use_gpu = 0
from multiprocessing import Process, Queue
Q = Queue()

from classification_models import auto_knn, auto_random_forest, auto_lr, auto_svm, auto_mlp, balanced_random_forest
#from classification_models import auto_faultnet
#from classification_models import auto_cnn
import os
#from tensorflow import keras
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from datasets.mfpt import MFPT
from datasets.paderborn import Paderborn
from datasets.cwru import CWRU
from datasets.models.hust import HUST
from datasets.models.ottawa import OTTAWA

from imblearn.combine import SMOTEENN, SMOTETomek
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import SMOTE

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
    return y_pred

@timer
def experimenter(source, target, clfs):

    write_in_file("execution_time", f"{target[0]}\n")

    print("\nPerforming Experiments.")
    
    X_source, y_source = source[1].get_acquisitions()
    # print(X_source.shape)
    print("### Source: ", source[0], "###")
    y_source[np.logical_and(y_source!='N', y_source!='H')] = 'F'
    print(f"Labels: {set(y_source)}")
    for label in set(y_source):
        print((f"{label}: {np.sum(y_source==label)}"))
    
    X_train, y_train = X_source, y_source
        
    X_test, y_test = target[1].get_acquisitions()
    print("### Target: ", target[0], "###")
    y_test[np.logical_and(y_test!='N', y_test!='H')] = 'F'
    print(f"Labels: {set(y_test)}")
    for label in set(y_test):
        print((f"{label}: {np.sum(y_test==label)}"))

    for clf in clfs:
        y_pred = run_train_test(clf[1], X_train, y_train, X_test)
        print("\n", clf[0])
        print(f"accuracy: {accuracy_score(y_test, y_pred)}")
        print(f"f1-score: {f1_score(y_test, y_pred, average='macro')}")
        labels = list(set(y_train).union(set(y_test)))
        print(labels)
        print(confusion_matrix(y_test, y_pred, labels=labels))



def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    #### Define experiments classifiers
    clfs = [
            # ('K-Nearest Neighbors', auto_knn.instantiate_auto_knn()),
            # ('Random Forest', auto_random_forest.instantiate_auto_random_forest()),
            ('Balanced Random Forest', balanced_random_forest.instantiate_balanced_random_forest()),
            # ('Logistic Regression', auto_lr.instantiate_auto_lr()),
            # ('SVM', auto_svm.instantiate_auto_svm()),
            # ('MLP', auto_mlp.instantiate_auto_mlp()),
            # ('CNN', auto_cnn.instantiate_auto_cnn()),
            # ('FaultNet', auto_faultnet.instantiate_auto_cnn()),
            ]
   
    

    #### Define experiments data set
    # paderborn = ('Paderborn', Paderborn(bearing_names_file="paderborn_bearings.csv", n_aquisitions=20))
    mfpt = ('MFPT', MFPT())
    # cwru = ('CWRU', CWRU())
    hust = ('HUST', HUST())
    ottawa = ('OTTAWA', OTTAWA())
    

    # dataset download
    # hust[1].download()
    # ottawa[1].download()

    # ottawa[1].load_acquisitions()

    # experimenter(hust, mfpt, clfs)
    experimenter(ottawa, ottawa, clfs)
    

if __name__ == "__main__":
    main()