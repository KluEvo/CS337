import json
import re
import spacy
from rapidfuzz import fuzz, utils
import numpy as np

# Load the English language model
nlp = spacy.load("en_core_web_sm")


def loadTweets(json_file):
    with open(json_file, 'r') as file:
        tweets = json.load(file)
    return tweets


def namesInText(text):
    # Process the text with spaCy
    doc = nlp(text)
    # Extract named entities
    entities = [ent.text for ent in doc.ents if ent.label_ in {"PERSON"}]
    if entities:
        return entities
    return False


# Function to detect names
def findName(name, text):
    # Function to check if an entity matches any name in nameArr
    def matches_name(entity):
        if (fuzz.QRatio(entity, name) > 50):
            return True
        nameParts = name.split()
        for namePart in nameParts:
            if (fuzz.QRatio(entity, namePart) > 50):
                return True    

        return False

    # Check each entity against nameArr
    return any(matches_name(entity) for entity in namesInText(text))



def checkHumans(nominees):
    for nom in nominees:
        doc = nlp(nom)

        # Extract named entities
        entities = [ent.text for ent in doc.ents if ent.label_ in {"PERSON"}]
        if not len(entities):
            return False

def detectTitle(nominee, candidate):
    if nominee.lower() in candidate.lower():
        return True
    return False


def findWinner(award_name, nominees, json_file):
    skipper = 0
    total = 0
    # Load the tweets from the JSON file
    tweets = loadTweets(json_file)
    ss = 1
    
    areHumans = checkHumans(nominees)
    award_match = "best "
    # processing the award name to be more useful
    if "supporting" in award_name:
        award_match = award_name.replace("performance by an", "supporting").strip()
    else:
        award_match = award_name.replace("performance by an ", '').strip()

    print(award_match)
    # Define regex pattern for identifying phrases related to winning
    win_patterns = [
        # r"(.+?)\s+won\s+(.+)",
        r"(.+?)\s+goes to\s+(.+)",
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
        if total % 5000 == 0:
            print(total)

        if 'best' in text.lower():
            # ss = 1
            for pattern in win_patterns:
                candidate = matchFormat(text, award_match, pattern)
                if not candidate:    
                    continue
                for nominee in nominees:
                    # print(text + "\n")
                    if (areHumans and findName(nominee, candidate)) or ((not areHumans) and detectTitle(nominee, candidate)): 
                        nominee_mentions[nominee] += 1
        

    # Determine the nominee with the highest count
    winner = max(nominee_mentions, key=nominee_mentions.get)
    print(nominee_mentions)
    print(total - skipper)
    # If no winner was found, return None
    if nominee_mentions[winner] == 0:
        return None

    return winner

# Additional context check for awards to avoid confusion between similar categories
def matchesContext(part, known):
    # part_tokens = nlp(part.lower())
    # part_tokens_list = [token.text for token in part_tokens]
    part_tokens_list = part.split()

    if "best" not in part_tokens_list:
        return False
            
    # known_tokens = nlp(known.lower())
    # known_tokens_list = [token.text for token in known_tokens]
    known_tokens_list = known.split()

    if "best" not in known:
        return False
        
    known_index = known_tokens_list.index("best") + 1
    part_index = part_tokens_list.index("best") + 1


    if known_index < len(known_tokens_list) and part_index < len(part_tokens_list):
        if fuzz.QRatio(known_tokens_list[known_index], part_tokens_list[part_index], processor=utils.default_process) > 75:
            return True

    return False

def matchFormat(text, known_award, pattern):
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


    # Check if the extracted parts match the known person and award
    if matchesContext(award_part, known_award):
        return person_part

    return False

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


if __name__ == "__main__":
    json_file = "gg2013.json"
    award_match = "best performance by an actor in a motion picture - drama"
    nominees = [ "richard gere",
                "john hawkes",
                "joaquin phoenix",
                "denzel washington",
                    "daniel day-lewis"]

    winner = findWinner(award_match, nominees, json_file)
    print(f"The winner is: {winner}")
