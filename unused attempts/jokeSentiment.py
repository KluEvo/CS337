import json
import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")

with open('gg2013.json', 'r') as file:
    tweets = json.load(file)

def is_joke(text):
    joke_indicators = ["haha", "punchline", "XD", "lmao"]
    return any(indicator in text.lower() for indicator in joke_indicators)

jokes = defaultdict(list)

for tweet in tweets:
    text = tweet['text']
    user = tweet['user']['screen_name']

    if is_joke(text):
        jokes[text].append(user)

ranked_jokes = sorted(jokes.items(), key=lambda x: len(x[1]), reverse=True)

print("Best jokes of the night and who told them:")
for joke, users,  in ranked_jokes[:3]:
    print(f"Joke: {joke}")
    print(len(users))
