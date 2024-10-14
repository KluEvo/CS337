import json
import re
import nltk
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
import spacy
from fuzzywuzzy import process

from fuzzywuzzy import fuzz

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Ensure necessary downloads
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('stopwords')
# Load spaCy model

# Load stopwords
STOPWORDS = set(stopwords.words('english'))

def load_tweets(json_file):
    with open(json_file, 'r') as file:
        tweets = json.load(file)
    return tweets

def clean_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r'\W+', ' ', text)
    return text.lower()

# Function to detect names
def detect_name(name, text):
    # Process the text with spaCy
    doc = nlp(text)

    # Extract named entities
    entities = [ent.text for ent in doc.ents if ent.label_ in {"PERSON"}]

    # Function to check if an entity matches any name in nameArr
    def matches_name(entity):
        first_name, last_name = name.split()
        if (fuzz.ratio(entity, first_name) > 50 or
            fuzz.ratio(entity, last_name) > 50 or
            fuzz.ratio(entity, name) > 50):
            return True
        return False

    # Check each entity against nameArr
    return any(matches_name(entity) for entity in entities)



def find_winner(award_name, nominees, json_file):
    skipper = 0
    total = 0
    # Load the tweets from the JSON file
    tweets = load_tweets(json_file)

    # Define regex pattern for identifying phrases related to winning
    win_patterns = [
        # r"(.+?)\s+won\s+(.+)",
        # r"(.+?)\s+goes to\s+(.+)",
        r"(.+?)\s+wins\s+(.+)",
        # r"(.+?)\s+awarded\s+(.+)",
    ]
    # Initialize a dictionary to keep track of how many times each nominee is mentioned as a winner
    nominee_mentions = {nominee: 0 for nominee in nominees}

    # Iterate through the tweets and search for patterns
    for tweet in tweets:
        # text = clean_text(tweet['text'])
        text = tweet['text']
        total += 1
        if total % 5000 ==0:
            print(total)

        for pattern in win_patterns:
            person = match_format(text, award_name, pattern)
            if not person:    
                continue
            for nominee in nominees:
                
                # print(text + "\n")
                if detect_name(nominee, person):
                    nominee_mentions[nominee] += 1
        

    # Determine the nominee with the highest count
    winner = max(nominee_mentions, key=nominee_mentions.get)
    print(nominee_mentions)
    print(total - skipper)
    # If no winner was found, return None
    if nominee_mentions[winner] == 0:
        return None

    return winner


def match_format(text, known_award, pattern):
    # Regular expression to extract parts before and after "wins"
    matchRes = re.match(pattern, text)

    if not matchRes:
        return False

    # Extract the parts before and after "wins"
    if "best" in matchRes.group(2).lower():
        person_part = matchRes.group(1)
        award_part = matchRes.group(2)
    elif "best" in matchRes.group(1).lower():
        person_part = matchRes.group(2)
        award_part = matchRes.group(1)
    else:
        return False

    # Additional context check for awards to avoid confusion between similar categories
    def matches_award_context(part, known):
        part_tokens = nlp(part.lower())
        part_tokens_list = [token.text for token in part_tokens]

        if "best" not in part_tokens_list:
            return False
                
        known_tokens = nlp(known.lower())
        known_tokens_list = [token.text for token in known_tokens]
        
        known_index = known_tokens_list.index("best") + 1
        part_index = part_tokens_list.index("best") + 1

        if known_index < len(known_tokens_list) and part_index < len(part_tokens_list):
            if fuzz.ratio(known_tokens_list[known_index], part_tokens_list[part_index]) > 75:
                return True

        return False


    # Check if the extracted parts match the known person and award
    if matches_award_context(award_part, known_award):
        return person_part

    return False

# # Example usage
# baseNO = "'Silver Linings Playbook' Review http://t.co/pgrK5zjq via @examinercom  Jennifer Lawrence wins Best Actress  at #GoldenGlobes  Congrats!"
# known_person = "Jennifer Lawrence"
# known_award = "Golden Globe Award for Best Actress in a Motion Picture – Drama"
# print(match_format(baseNO, known_award, pattern=r"(.+?)\s+wins\s+(.+)"))

# def find_json_files():
#     json_files = []
#     for file_name in os.listdir(os.getcwd()):
#         if fnmatch.fnmatch(file_name, '*.json'):
#             json_files.append(file_name)
#     return json_files

# # Example usage
# directory_path = '/path/to/your/directory'
# json_files_array = find_json_files(directory_path)
# print(json_files_array)


json_file = "gg2013.json"
award_name = "Best Supporting Actress in a Motion Picture – Musical or Comedy"
nominees = [ "Jennifer Lawrence", "Emily Blunt", "Judi Dench", "Maggie Smith", "Meryl Streep"]

winner = find_winner(award_name, nominees, json_file)
print(f"The winner is: {winner}")
