import json
import spacy
from collections import defaultdict

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Load the JSON file
with open('gg2013.json', 'r') as file:
    tweets = json.load(file)

# Function to check if a tweet contains a joke
def is_joke(text):
    # Simple heuristic: look for laughter or common joke phrases
    joke_indicators = ["haha", "punchline", "XD", "lmao"]
    return any(indicator in text.lower() for indicator in joke_indicators)

# Process tweets to find jokes
jokes = defaultdict(list)

for tweet in tweets:
    text = tweet['text']
    user = tweet['user']['screen_name']

    if is_joke(text):
        jokes[text].append(user)

# Rank jokes by the number of times a user's jokes appear
ranked_jokes = sorted(jokes.items(), key=lambda x: len(x[1]), reverse=True)

# Print the best jokes and who told them
print("Best jokes of the night and who told them:")
for joke, users,  in ranked_jokes[:3]:
    print(f"Joke: {joke}")
    print(len(users))
