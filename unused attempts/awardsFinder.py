import json
import re
from nltk import word_tokenize, pos_tag

def load_tweets(json_file):
    with open(json_file, 'r') as file:
        tweets = json.load(file)
    return tweets

def clean_text(text):
    # Remove URLs and non-alphanumeric characters
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r'\W+', ' ', text)
    return text.lower()

def extract_award_names(json_file):
    # Load tweets from JSON file
    tweets = load_tweets(json_file)
    
    # Initialize an empty set to store unique award names
    award_names = set()
    
    # Define a pattern that looks for phrases starting with 'best'
    award_pattern = re.compile(r"best [a-z ]+", re.IGNORECASE)
    
    for tweet in tweets:
        text = tweet['text']
        
        # Search for all occurrences of the pattern
        matches = award_pattern.findall(text)
        
        for match in matches:
            # Use POS tagging to refine the extracted phrases
            tokens = word_tokenize(match)
            tagged = pos_tag(tokens)
            
            # Look for sequences like "Best" followed by adjectives and nouns
            award_phrase = []
            for word, tag in tagged:
                # Keep words as long as they are adjectives or nouns (for award names)
                if tag in ['JJ', 'NN', 'NNP', 'NNS']:  # Adjectives and Nouns
                    award_phrase.append(word)
                else:
                    break
            
            if award_phrase:
                # Reconstruct and add the phrase to the set of award names
                award_names.add(" ".join(award_phrase))
    
    return award_names

# Example usage:
json_file = "gg2013.json"
print("Extracting Award Names")
award_names = extract_award_names(json_file)
print("Extracted Award Names:")
for award in award_names:
    print(award)
