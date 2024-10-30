import json
import re
import spacy
from ftfy import fix_text
from unidecode import unidecode
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import names
from nltk.corpus import wordnet as wn
from nltk import pos_tag
import nltk

from rapidfuzz import process, fuzz
from langdetect import detect, LangDetectException
from imdb import IMDb

### SOME LOADING
spacy_model = spacy.load("en_core_web_sm")
stemmer = PorterStemmer()
female_names = [name.lower() for name in names.words('female.txt')]
male_names = [name.lower() for name in names.words('male.txt')]
ia = IMDb()

### HELPER FUNCTIONS

# loads tweet data
def load_tweets():
    with open('gg2013.json') as f:
        tweet_data = json.load(f)
    return tweet_data

# cleans a singular tweet
def clean_tweet(tweet):
    fixed_tweet = fix_text(tweet)
    cleaned_tweet = unidecode(fixed_tweet)
    cleaned_tweet = re.sub(r"http\S+|www\S+|https\S+", '', cleaned_tweet, flags=re.MULTILINE)
    cleaned_tweet = re.sub(r'\W+', ' ', cleaned_tweet)
    return cleaned_tweet.lower()

# clean the tweet for Spacy name    
def clean_name_tweet(tweet):
    tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
    tweet = re.sub(r'[^\x20-\x7E]', '', tweet)
    tweet = re.sub(r'([.,!?-])\1+', r'\1', tweet)
    tweet = re.sub(r'\s+', ' ', tweet).strip()
    return tweet

# keywords from an award name
def award_keywords(award_name):
    doc = spacy_model(award_name)
    keywords = []
    arbitrary_words = ["performance", "role", "motion", "picture"]
    abbrevations = {"television": "tv"}

    for token in doc:
        if token.text in arbitrary_words or token.is_stop or token.is_punct:
            continue
        elif token.text in abbrevations:
            keywords.append(abbrevations[token.text])
        elif token.ent_type_: 
            keywords.append(token.text)
        elif token.pos_ in {'PROPN', 'NOUN', 'ADJ'}:  
            keywords.append(token.text)
        else:
            keywords.append(token.text)
    return [keyword for keyword in keywords]

# gets names mentioned in a tweet
def get_other(text):
    # names = []
    # valid_chunks = ['NN', 'NNP', 'NNPS', 'NNS']
    # tokens = nltk.tokenize.word_tokenize(text)
    # pos = nltk.pos_tag(tokens)
    # sent = nltk.ne_chunk(pos, binary = False)
    # for i in range(len(sent)):
    #     chunk = sent[i]
    #     word = chunk[0]
    #     # chunk_type = chunk[1]
    #     if word in female_names or word in male_names:
    #         if i + 1 < len(sent) and sent[i+1][1] in valid_chunks:
    #             full_name = sent[i][0] + " " + sent[i+1][0]
    #             names.append(full_name)
    # return names
    names = []
    valid_chunks = ['NN', 'NNP', 'NNPS', 'NNS']
    tokens = nltk.tokenize.word_tokenize(text)
    for i in range(len(tokens)):
        word = tokens[i]
        if word in valid_chunks:
            if i + 1 < len(tokens):
                full_name = tokens[i] + " " + tokens[i+1]
                names.append(full_name)
    return names


# check if the award is in tweet
def award_in_tweet(award_name, cleaned_tweet):
    cleaned_award = clean_tweet(award_name)
    award_tokens = award_keywords(cleaned_award)
    best_pattern = r"(.+) (best) (.+)"
    match = re.search(best_pattern, cleaned_tweet)
    if match:
            best_prev = re.match(best_pattern, cleaned_tweet).group(1)
            best_onwards = re.match(best_pattern, cleaned_tweet).group(2) + " " + re.match(best_pattern, cleaned_tweet).group(3)
            award_in_tweet = all(word in best_onwards for word in award_tokens)
            return award_in_tweet
    else:
        return False
    
def is_english(text):
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False

# check if this is a valid name
def valid_name(name_lowered):
    invalid_characters = ['rt', '@', 'golden', 'globe', '#']
    name_list = name_lowered.split(" ")
    if len(name_list) <= 1 or len(name_list) > 3:
        return False
    first_name = name_list[0]
    if first_name not in male_names and first_name not in female_names:
        return False
    for invalid in invalid_characters:
        if invalid in name_lowered:
            return False
    return True

# find a similar key in the dictionary
def find_similar_key(key, dictionary, threshold=75):
    match = process.extractOne(key, dictionary.keys(), scorer=fuzz.ratio)
    
    if match and match[1] >= threshold:
        return match[0]
    else:
        return None
    
# combine any similar names of a dictionary into one
def combine_dict(dictionary):
    combined_dict = {}

    # Iterate over each key in the dictionary
    for key in dictionary.keys():
        similar_key = find_similar_key(key, combined_dict)
        
        if similar_key:
            combined_dict[similar_key] += dictionary[key]
        else:
            combined_dict[key] = dictionary[key]

    return combined_dict

def get_other_names(text):
    return 1

def present_keyword():
    ["present", "read", ]

def nominee_keyword():
    "should have won"
    "deserve win"
    "hope win / hope won "
    "robbed"

### ACTUAL FUNCTIONS

# get starting/ending timestamps  (+/- 3 minutes) of when this award was tweeted about
def get_award_timestamps(award_name):
    cleaned_award = clean_tweet(award_name)
    award_tokens = award_keywords(cleaned_award)

    all_award_timestamps = []
    tweet_data = load_tweets()
    best_pattern = r"(.+) (best) (.+)"
    for tweet in tweet_data:
        timestamp = tweet['timestamp_ms']
        message = tweet['text']
        cleaned_tweet = clean_tweet(message)
        match = re.search(best_pattern, cleaned_tweet)
        if match:
            best_prev = re.match(best_pattern, cleaned_tweet).group(1)
            best_onwards = re.match(best_pattern, cleaned_tweet).group(2) + " " + re.match(best_pattern, cleaned_tweet).group(3)
            award_in_tweet = all(word in best_onwards for word in award_tokens)
            if award_in_tweet:
                all_award_timestamps.append(timestamp)

            # print(f"best prev: {best_prev}")
            # print(f"best onwards: {best_onwards}")
            # print(f"actual tweet {cleaned_tweet}")
    # return [all_award_timestamps[0] - (10 * 60 * 1000), all_award_timestamps[-1] + (10 * 60 * 1000)]
    return [all_award_timestamps[0] -  (5 * 60 * 1000), all_award_timestamps[0] + (15 * 60 * 1000)]

# get nominees, winner, presenter(s) for a human award
def get_human_info(award_name):
    nominees_dict = {}
    nominee_regex = r"\b(should.*?(?:win|won)|deserved.*?(?:win|won|it)|wanted.*?(?:win)|hope.*?(?:win|won)|didn.*?(?:win)|did not.*?(?:win)|robbed|nominate|nominee|up for best)\w*\b"

    winner_dict = {}
    winner_regex = r"(.+?)\s+wins\s+(.+)"
    
    presenters_dict = {}
    presenter_regex = r"\b(presents|present|read|hand|announce|introduce)\w*\b"

    award_timestamps = get_award_timestamps(award_name)
    print(award_timestamps)

    tweet_data = load_tweets()
    for tweet in tweet_data:
        timestamp = tweet['timestamp_ms']
        message = tweet['text']
        cleaned_tweet = clean_tweet(message)
        if "rt" in cleaned_tweet:
            cleaned_tweet = cleaned_tweet[3:]
        if timestamp >= award_timestamps[0] and timestamp <= award_timestamps[1]:
            nominee_match = re.search(nominee_regex, cleaned_tweet)
            winner_match = re.search(winner_regex, cleaned_tweet)
            presenter_match = re.search(presenter_regex, cleaned_tweet)
            
            if nominee_match or winner_match or presenter_match:
                name_structure_tweet = clean_name_tweet(message)
                spacy_output = spacy_model(name_structure_tweet)

            if nominee_match:
                for entity in spacy_output.ents:
                    if entity.label_ == 'PERSON':
                        name = entity.text.lower()
                        if valid_name(name):
                            if name in nominees_dict:
                                nominees_dict[name] += 1
                            else:
                                nominees_dict[name] = 1
            
            if winner_match and award_in_tweet(award_name, cleaned_tweet):
                for entity in spacy_output.ents:
                    if entity.label_ == 'PERSON':
                        name = entity.text.lower()
                        if valid_name(name):
                            if name in winner_dict:
                                winner_dict[name] += 1
                            else:
                                winner_dict[name] = 1
            
            if presenter_match:
                for entity in spacy_output.ents:
                    if entity.label_ == 'PERSON':
                        name = entity.text.lower()
                        if valid_name(name):
                            if name in presenters_dict:
                                presenters_dict[name] += 1
                            else:
                                presenters_dict[name] = 1
    
    nominees_sorted = dict(sorted(nominees_dict.items(), key=lambda item: item[1], reverse=True))
    winner_sorted = dict(sorted(winner_dict.items(), key=lambda item: item[1], reverse=True))
    presenters_sorted = dict(sorted(presenters_dict.items(), key=lambda item: item[1], reverse=True))
    nominees_combined = combine_dict(nominees_sorted)
    presenters_combined = combine_dict(presenters_sorted)
    # NOMINEES: max person of winner dict, plus top 4 of nominees dict???
    # PRESENTERS: max one or two
    # print(f"nominees dictionary: {nominees_combined}")
    # print(f"winner dictionary: {winner_sorted}")
    # print(f"presenters dictionary: {presenters_combined}")
    nominees = []
    potential_nominees = []
    presenters = []
    potential_presenters = []

    if winner_sorted:
        winner = list(winner_sorted.keys())[0]
        nominees.append(winner)
    
    top_nominees_list = list(nominees_combined.keys())
    i = 0
    while i < len(top_nominees_list):
        if len(nominees) >= 5:
            break
        nominee = top_nominees_list[i]
        if nominee not in nominees:
            nominees.append(nominee)
        i += 1
    while i < len(top_nominees_list):       
        if len(potential_nominees) >= 5:
            break
        nominee = nominee = top_nominees_list[i]
        potential_nominees.append(nominee)
        i += 1
    
    top_presenters_list = list(presenters_combined.keys())
    i = 0
    while i < len(top_presenters_list):
        if len(presenters) >= 2:
            break
        presenter = top_presenters_list[i]
        if presenter not in presenters:
            presenters.append(presenter)
        i += 1
    while i < len(top_presenters_list):
        if len(potential_presenters) > 10:
            break
        presenter = top_presenters_list[i]
        potential_presenters.append(presenter)
        i += 1

    # print(f"nominees: {nominees}")
    # print(f"potential nominees: {potential_nominees}")
    # print(f"presenters: {presenters}")
    # print(f"potential presenters: {potential_presenters}")

    entire_dict = {"nominees": nominees, "potential nominees": potential_nominees, "presenters": presenters, "potential presenters": potential_presenters}
    return entire_dict 

# get nominees, winner, presenter(s) for a non-human award
def get_other_info(award_name):
    nominees_dict = {}
    nominee_regex = r"\b(should.*?(?:win|won)|deserved.*?(?:win|won|it)|wanted.*?(?:win)|hope.*?(?:win|won)|didn.*?(?:win)|did not.*?(?:win)|robbed|nominate|nominee|up for best)\w*\b"

    winner_dict = {}
    winner_regex = r"(.+?)\s+wins\s+(.+)"
    
    presenters_dict = {}
    presenter_regex = r"\b(presents|present|read|hand|announce|introduce)\w*\b"

    award_timestamps = get_award_timestamps(award_name)
    print(award_timestamps)

    tweet_data = load_tweets()
    for tweet in tweet_data:
        timestamp = tweet['timestamp_ms']
        message = tweet['text']
        cleaned_tweet = clean_tweet(message)
        if "rt" in cleaned_tweet:
            cleaned_tweet = cleaned_tweet[3:]
        if timestamp >= award_timestamps[0] and timestamp <= award_timestamps[1]:
            nominee_match = re.search(nominee_regex, cleaned_tweet)
            winner_match = re.search(winner_regex, cleaned_tweet)
            presenter_match = re.search(presenter_regex, cleaned_tweet)
            
            if nominee_match or winner_match or presenter_match:
                name_structure_tweet = clean_name_tweet(message)
                spacy_output = spacy_model(name_structure_tweet)

            if nominee_match:
                for entity in spacy_output.ents:
                    if entity.label_ in {"WORK_OF_ART", "PERSON", "ORG"}:
                        name = entity.text.lower()
                        if name in nominees_dict:
                            nominees_dict[name] += 1
                        else:
                            nominees_dict[name] = 1
            
            # if winner_match and award_in_tweet(award_name, cleaned_tweet):
            #     for entity in spacy_output.ents:
            #         if entity.label_ == 'WORK OF ART':
            #             name = entity.text.lower()
            #             if name in winner_dict:
            #                 winner_dict[name] += 1
            #             else:
            #                 winner_dict[name] = 1
            
            # if presenter_match:
            #     for entity in spacy_output.ents:
            #         if entity.label_ == 'PERSON':
            #             name = entity.text.lower()
            #             if valid_name(name):
            #                 if name in presenters_dict:
            #                     presenters_dict[name] += 1
            #                 else:
            #                     presenters_dict[name] = 1
    
    nominees_sorted = dict(sorted(nominees_dict.items(), key=lambda item: item[1], reverse=True))
    winner_sorted = dict(sorted(winner_dict.items(), key=lambda item: item[1], reverse=True))
    presenters_sorted = dict(sorted(presenters_dict.items(), key=lambda item: item[1], reverse=True))
    nominees_combined = combine_dict(nominees_sorted)
    presenters_combined = combine_dict(presenters_sorted)
    # NOMINEES: max person of winner dict, plus top 4 of nominees dict???
    # PRESENTERS: max one or two
    print(f"nominees dictionary: {nominees_combined}")
    print(f"winner dictionary: {winner_sorted}")
    print(f"presenters dictionary: {presenters_combined}")
    # nominees = []
    # potential_nominees = []
    # presenters = []
    # potential_presenters = []

    # if winner_sorted:
    #     winner = list(winner_sorted.keys())[0]
    #     nominees.append(winner)
    
    # top_nominees_list = list(nominees_combined.keys())
    # i = 0
    # while i < len(top_nominees_list):
    #     if len(nominees) >= 5:
    #         break
    #     nominee = top_nominees_list[i]
    #     if nominee not in nominees:
    #         nominees.append(nominee)
    #     i += 1
    # while i < len(top_nominees_list):       
    #     if len(potential_nominees) >= 5:
    #         break
    #     nominee = nominee = top_nominees_list[i]
    #     potential_nominees.append(nominee)
    #     i += 1
    
    # top_presenters_list = list(presenters_combined.keys())
    # i = 0
    # while i < len(top_presenters_list):
    #     if len(presenters) >= 2:
    #         break
    #     presenter = top_presenters_list[i]
    #     if presenter not in presenters:
    #         presenters.append(presenter)
    #     i += 1
    # while i < len(top_presenters_list):
    #     if len(potential_presenters) > 10:
    #         break
    #     presenter = top_presenters_list[i]
    #     potential_presenters.append(presenter)
    #     i += 1

    # print(f"nominees: {nominees}")
    # print(f"potential nominees: {potential_nominees}")
    # print(f"presenters: {presenters}")
    # print(f"potential presenters: {potential_presenters}")

    # entire_dict = {"nominees": nominees, "potential nominees": potential_nominees, "presenters": presenters, "potential presenters": potential_presenters}
    # return entire_dict


def get_everything(award_name):
    list_words = ["performance", "actor", "actress", "director", "producer"]
    if any(word in award_name for word in list_words):
        # human
        return get_human_info(award_name)
    else:
        # movie, song, etc.
        return get_other_info(award_name)
    
dict_returned = get_human_info("best performance by an actress in a motion picture - drama")
print(dict_returned)

# get_everything("cecil b. demille award")

# sentence = "RT @goldenglobes: Best Original Score - Mychael Danna - Life of Pi - #GoldenGlobes"
# spacy_output = spacy_model(clean_name_tweet(sentence))

# for entity in spacy_output.ents:
#     print("hello")
#     print(entity.text)
# #     if entity.label_ in {"WORK_OF_ART", "PERSON", "ORG"}:
# #         print(entity.text)