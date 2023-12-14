
from utils.persist_results import load_results
from statistics import mean, stdev
from sklearn.metrics import accuracy_score, f1_score


def scores(file):

    results = load_results(file)
    
    accuracy = []
    f1_macro = []
    
    for fold in results:

        classifier = fold[1]
        y_actual = fold[2]
        y_pred = fold[3]
        
        accuracy.append(accuracy_score(y_actual, y_pred))
        f1_macro.append(f1_score(y_actual, y_pred, average='macro'))
        
        print("# Classification Model: ", classifier, "#")
        print("Accuracy: ", accuracy, "Mean: ", mean(accuracy), "Std: ", stdev(accuracy))
        print("F1 Macro: ", f1_macro, "Mean: ", mean(f1_macro), "Std: ", stdev(f1_macro))           

        print()
        accuracy = []
        f1_macro = []
   