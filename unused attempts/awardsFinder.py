import json
import re
from nltk import word_tokenize, pos_tag

def load_tweets(json_file):
    with open(json_file, 'r') as file:
        tweets = json.load(file)
    return tweets

def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r'\W+', ' ', text)
    return text.lower()

def extract_award_names(json_file):
    tweets = load_tweets(json_file)
    
    award_names = set()
    
    award_pattern = re.compile(r"best [a-z ]+", re.IGNORECASE)
    
    for tweet in tweets:
        text = tweet['text']
        
        matches = award_pattern.findall(text)
        
        for match in matches:
            tokens = word_tokenize(match)
            tagged = pos_tag(tokens)
            
            award_phrase = []
            for word, tag in tagged:
                if tag in ['JJ', 'NN', 'NNP', 'NNS']:  
                    award_phrase.append(word)
                else:
                    break
            
            if award_phrase:
                award_names.add(" ".join(award_phrase))
    
    return award_names

# example usage:
json_file = "gg2013.json"
print("Extracting Award Names")
award_names = extract_award_names(json_file)
print("Extracted Award Names:")
for award in award_names:
    print(award)
