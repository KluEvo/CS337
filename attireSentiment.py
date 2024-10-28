import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
from textblob import TextBlob
from collections import defaultdict

# Download necessary NLTK data
# nltk.download('punkt')
# nltk.download('stopwords')

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Function to preprocess tweets
def preprocess_tweet(tweet):
    tweet = tweet.lower()
    tokens = word_tokenize(tweet)
    tokens = [word for word in tokens if word.isalnum()]
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    return tokens

# Function to extract relevant tweets
def extract_relevant_tweets(tweets, keywords):
    relevant_tweets = []
    for tweet in tweets:
        tweet_text = tweet['text'].lower()
        if any(keyword in tweet_text for keyword in keywords):
            relevant_tweets.append(tweet)
    return relevant_tweets

# Function to perform sentiment analysis
def analyze_sentiment(tweet_text):
    analysis = TextBlob(tweet_text)
    return analysis.sentiment.polarity

# Load the JSON file
with open('gg2013.json', 'r') as file:
    tweets = json.load(file)

# Define keywords related to dressing and fashion
keywords = ['dress', 'outfit', 'fashion', 'style', 'clothes', 'wear', 'dressed']

# Extract relevant tweets
relevant_tweets = extract_relevant_tweets(tweets, keywords)

# Initialize dictionaries to store sentiment scores
best_dressed = defaultdict(list)
worst_dressed = defaultdict(float)
controversial_dressed = defaultdict(lambda: [0, 0, 0])

total = 0
# Analyze sentiment and aggregate scores
for tweet in relevant_tweets[2000:]:
    total += 1
    if total % 500 == 0:
        print(total)
    tweet_text = tweet['text']

    # Use spaCy to extract named entities (people's names)
    doc = nlp(tweet_text.title())
    for ent in doc.ents:
        if ("goldenglobes" not in ent.text.lower()) and ent.label_ == 'PERSON':
            
            sentiment_score = analyze_sentiment(tweet_text)
            person_name = ent.text.title()
            best_dressed[person_name].append(sentiment_score)
            worst_dressed[person_name] += 1
            if sentiment_score > 0:
                controversial_dressed[person_name][0] += 1
            else: 
                controversial_dressed[person_name][1] += 1
            controversial_dressed[person_name][2] += 1


controversy_score = defaultdict(float)

for person in controversial_dressed:
    print(controversial_dressed[person_name])
    score = controversial_dressed[person_name][1] * controversial_dressed[person_name][0]
    if score >  controversial_dressed[person_name][2]:
        controversy_score[person] = score / controversial_dressed[person_name][2]

from collections import Counter
d = Counter(best_dressed)
print(d.most_common(3))
d = Counter(best_dressed)
print(d.most_common()[-5:])
d = Counter(controversy_score)
print(d.most_common())
