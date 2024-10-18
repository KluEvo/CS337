import json
import re
import spacy
from fuzzywuzzy import fuzz
import numpy as np
from nltk import word_tokenize, pos_tag

nlp = spacy.load("en_core_web_sm")

def load_tweets(json_file):
    with open(json_file, 'r') as file:
        tweets = json.load(file)
    return tweets

def clean_dictionary(dictionary):
    sorted_data = dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))
    cleaned_dict = {}
    for key in sorted_data:
        add_key = True
        for cleaned_key in cleaned_dict:
            if fuzz.ratio(key, cleaned_key) > 80 or key in cleaned_key:
                cleaned_dict[cleaned_key] += sorted_data[key]
                add_key = False
                break
        if add_key:
            cleaned_dict[key] = sorted_data[key]

    return cleaned_dict

def high_outliers(dictionary):
    counts = list(dictionary.values())
    mean = np.mean(counts)
    std_dev = np.std(counts)
    threshold = mean + 2 * std_dev
    outliers = [key for key, count in dictionary.items() if count > threshold]
    return outliers

def find_awards_from_tweets(tweets):
    award_patterns = [
        r"wins\s+(.+)",
        r"awarded\s+(.+)",
        r"receives\s+(.+)",
        r"nominee\s+for\s+(.+)",
        r"nominated\s+for\s+(.+)",
        r"(.+)\s+goes\s+to",
        r"(.+)\s+presented\s+to"
    ]

    for tweet in tweets:
        text = tweet['text']

        for pattern in award_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                doc = nlp(match)
                award_pattern = r"(Best\s[\w\s]+(?:in a|for\s[\w\s]+)?)"
                awards = re.findall(award_pattern, doc.text, re.IGNORECASE)
                for award in awards:
                    doc1 = nlp(award)
                    award_name = None
                    for token in doc1:
                        if token.text.lower() == "best":
                            award_name = award
                    print(award_name)

json_file_path = 'gg2013.json'
awards = find_awards_from_tweets(load_tweets(json_file_path))
print(awards)
