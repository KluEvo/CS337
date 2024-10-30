import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
from textblob import TextBlob
from collections import defaultdict
import re

import numpy as np
# Load spaCy model
nlp = spacy.load('en_core_web_sm')

def remove_urls(text):
    # Regular expression pattern to match URLs
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        re.IGNORECASE
    )

    # Find all URLs in the text
    urls = url_pattern.findall(text)

    # Remove all URLs from the text
    for url in urls:
        text = text.replace(url, '')

    return text

# Function to extract relevant tweets
def extract_relevant_tweets(tweets, keywords):
    tweets = np.array(tweets)
    relevant_tweets = []
    for tweet in tweets:
        tweet_text = remove_urls(tweet['text'])
        if any(keyword in tweet_text.lower() for keyword in keywords):
            relevant_tweets.append(tweet_text)
    return list(relevant_tweets)

# Function to perform sentiment analysis
def analyze_sentiment(tweet_text):
    analysis = TextBlob(tweet_text)
    return analysis.sentiment.polarity

# Load the JSON file
with open('gg2013.json', 'r') as file:
    tweets = json.load(file)

# Define keywords related to dressing and fashion
keywords = np.array(['dress', 'outfit', 'fashion', 'style', 'clothes', 'wear', 'dressed'])

# Extract relevant tweets
relevant_tweets = extract_relevant_tweets(tweets, keywords)

# Initialize dictionaries to store sentiment scores
best_dressed = defaultdict(float)
worst_dressed = defaultdict(float)
controversial_dressed = defaultdict(lambda: [0, 0, 0])

total = 0

docs = nlp.pipe(relevant_tweets)

# Analyze sentiment and aggregate scores
for tweet_text in docs:
    total += 1
    if total % 500 == 0:
        print(total)
    for ent in tweet_text.ents:
        if ("goldenglobes" not in ent.text.lower()) and ent.label_ == 'PERSON':
            
            sentiment_score = analyze_sentiment(str(tweet_text))
            person_name = ent.text.title()
            if "'s" in person_name[-2:].lower():
                person_name = person_name[:-2]
            best_dressed[person_name] += (sentiment_score)
            worst_dressed[person_name] -= (sentiment_score)
            if sentiment_score > 0:
                controversial_dressed[person_name][0] += sentiment_score
            else: 
                controversial_dressed[person_name][1] -= sentiment_score
            controversial_dressed[person_name][2] += abs(sentiment_score)


controversy_score = defaultdict(float)

for person in controversial_dressed:
    score = controversial_dressed[person][1] * controversial_dressed[person][0]
    if score >  controversial_dressed[person][2]:
        controversy_score[person] = score / controversial_dressed[person][2]


from collections import Counter
d = Counter(best_dressed)
print("best dressed", d.most_common(1)[0][0])
d = Counter(worst_dressed)
print("worst dressed", d.most_common(1)[0][0])
d = Counter(controversy_score)
print("controversially dressed", d.most_common(1)[0][0])
