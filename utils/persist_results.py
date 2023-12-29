
from datetime import datetime
import csv
import ast
import sys
import os

# Code to avoid error with large results in CSV file
maxInt = sys.maxsize
while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)


def save_results(results):

    now = datetime.now()
    date_time = now.strftime("%Y.%m.%d_%H.%M.%S")
    file_name = date_time + ".csv"
    dir_name = 'log'

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    full_path = os.path.join(dir_name, file_name)

    with open(full_path, 'w', newline="") as csvfile:
        fieldnames = ['dataset', 'classifier', 'y_actual', 'y_pred', 'y_proba']
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        writer.writerows(results)

    return file_name


def load_results(file):
    results = []
    
    file = os.path.join('log', file)
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        
        line_count = 0
        for row in csv_reader:
            
            if line_count == 0:
                line_count += 1
                pass
            
            else:                
                dataset = row[0]
                classifier = row[1]
                
                # y_actual = ast.literal_eval(row[2])
                y_actual = ast.literal_eval(row[2].replace(" ", ",").replace("\n", ""))
                # if len(y_actual) == 1:
                #     y_actual = list(y_actual[0])

                # y_pred = ast.literal_eval(row[3])
                y_pred = ast.literal_eval(row[3].replace(" ", ",").replace("\n", ""))
                # if len(y_pred) == 1:
                #     y_pred = list(y_pred[0])
                
                y_proba = row[4]
                row_results = [dataset, classifier, y_actual, y_pred, y_proba]
                results.append(row_results)
                line_count += 1

    return results
