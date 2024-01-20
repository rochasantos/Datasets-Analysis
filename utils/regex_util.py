import re

def extract_groups_from_words(words, pattern):
    extracted_groups = []

    for word in words:
        match = pattern.match(word)
        if match:
            groups = match.groups()
            extracted_groups.append(groups)

    return extracted_groups