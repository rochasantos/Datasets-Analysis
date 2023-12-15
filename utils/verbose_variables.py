
def count_labels(labels):
    labels_name = list(set(labels))
    disc_labels = {'label': label for label in labels_name}
    for label in labels:
        for key, value in disc_labels.items():
            if disc_labels[key] == label:
                disc_labels[key] += 1
    return disc_labels