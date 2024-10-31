import re
from fuzzywuzzy import fuzz
import numpy as np

# combine similar keys
# combine keys of full name and just first name
def clean_dictionary(dictionary):
    sorted_data = dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))
    cleaned_dict = {}
    for key in sorted_data:
        add_key = True
        for cleaned_key in cleaned_dict:
            if fuzz.token_sort_ratio(key, cleaned_key) > 80 or key in cleaned_key:
                cleaned_dict[cleaned_key] += sorted_data[key]
                add_key = False
                break
        if add_key:
            cleaned_dict[key] = sorted_data[key]

    return cleaned_dict

# return keys with high counts
def high_outliers(dictionary):
    counts = list(dictionary.values())
    mean = np.mean(counts)
    std_dev = np.std(counts)
    threshold = mean + 2 * std_dev
    outliers = [key for key, count in dictionary.items() if count > threshold]
    return outliers

def find_hosts_from_tweets_nltk(tweets, nlp):

    host_patterns = [
        r"(.+?)\s+hosts\s+(.+)", 
        r"hosted\s+by\s+(.+)"
    ]

    host_mentions = {}

    for tweet in tweets:
        text = tweet['text']

        for pattern in host_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and 'next year' not in text:
                doc = nlp(text)
                entities = [ent.text for ent in doc.ents if ent.label_ in {"PERSON"}]

                if entities:
                    for person in entities:
                        if fuzz.ratio("golden globes", person.lower()) < 80:
                            if person not in host_mentions:
                                host_mentions[person] = 0
                            host_mentions[person] += 1

    cleaned_dict = clean_dictionary(host_mentions)
    return high_outliers(cleaned_dict)
