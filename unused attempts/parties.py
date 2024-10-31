import json
import re
import spacy
from fuzzywuzzy import fuzz
import numpy as np

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

def party_analysis(tweets):

    party_names = {}

    for tweet in tweets:
        text = tweet['text'].lower()

        if 'party' in text:
            if len(text.split(': ')) > 1:
                text = text.split(': ')[1]
            # match = re.search(r"(?<=\bthe\b\s)(.*?\bparty\b)", text, re.IGNORECASE)
            pattern = r"the\s(.*\bparty\b)"
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                party_name = matches[-1]
                if " to " in party_name:
                    match_to = re.search(r"(?<=\bto\b\s)(.*?\bparty\b)", text, re.IGNORECASE)
                    if match_to:
                        party_name = match_to.group(1)
                        if party_name not in party_names:
                            party_names[party_name] = 0
                        party_names[party_name] += 1
                else:
                    if party_name not in party_names:
                        party_names[party_name] = 0
                    party_names[party_name] += 1

    print(clean_dictionary(party_names))

json_file_path = 'gg2013.json'
party_analysis(load_tweets(json_file_path))
