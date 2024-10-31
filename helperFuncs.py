

import os
import re

def find_json_file_and_extract_year():
    directory = os.path.dirname(os.path.abspath(__file__))
    # List all files in the directory
    files = os.listdir(directory)

    pattern = re.compile(r'gg(\d{4})\.json')

    for file in files:
        match = pattern.match(file)
        if match:
            year = match.group(1)
            print(f"Found JSON file: {file}")
            print(f"Extracted year: {year}")
            return year

    print("No matching JSON file found.")

# year = find_json_file_and_extract_year()


from imdb import IMDb

# note: in our use case golden globes of 2013 are for 2012 moves, so in useage, do year of GG -1
def getMoviesAndShowsByYear(name, year):
    # Create an instance of the IMDb class
    ia = IMDb()

    # Search for movies released in the specified year
    search_results = ia.search_movie(f'{name}')

    # Filter the results to include only movies released in the specified year
    items = [item for item  in search_results if 'year' in item and item['year'] == year]

    # Extract relevant information from each movie
    items_list = []
    for item in items:
        item_info = {
            'title': item.get('title', 'N/A'),
            # 'year': item.get('year', 'N/A')
            # 'kind': item.get('kind', 'N/A')
        }
        items_list.append(item_info)

    return items_list

def validNonHuman(itemName, ggYear):
    imdbOut = getMoviesAndShowsByYear(itemName, ggYear-1)
    if imdbOut:
        return True
    return False

# show = "skyfall"
# print(f"checking if '{show}' is a valid show/movie")
# movies = getMoviesAndShowsByYear(show, int(year)-1)
# if movies:
#     print(movies)
# else:
#     print("not found")


from nltk.corpus import wordnet as wn
from nltk import pos_tag

# Function to check if a word is a profession
def isProfession(word):
    # Check if the word is a noun
    tagged_word = pos_tag([word])
    if tagged_word[0][1] != 'NN':
        return False

    # Check if the word is lexically a person
    synsets = wn.synsets(word)
    for synset in synsets:
        if 'person' in synset.lexname():
            return True
    return False

def checkHumanAward(awardName):
    awardWords = awardName.split()
    for word in awardWords:
        if isProfession(word):
            return True
    return False

# example usage:
# print(checkHumanAward("best animated feature film"))


from collections import Counter
from fuzzywuzzy import fuzz


def remove_symbols(a_tweet):
    a_tweet = a_tweet.lower()
    entity_prefixes = ['@','#']
    words = []
    for word in a_tweet.split():
        word = word.strip()
        if word and word[0] not in entity_prefixes:
            words.append(word)
    return ' '.join(words)

def find_special_awards(tweets):
    regexp = "(?<=the)(.*)(?=award)"
    specials = []

    for i in tweets:
        tweet = remove_symbols(i['text'])
        result = re.search(regexp, tweet)
        if result:
            start,end = result.span()
            if end - start > 25 or end - start < 10:
                continue
            specials.append(tweet[start:end])
    specials = list(Counter(specials).most_common(100))
    special_awards = specials[0:5]

    
    awards = []
    for i in special_awards:
        cont = True
        if fuzz.ratio(i[0].lower(), "golden globes") > 70 or "golden globe" in i[0].lower():
            cont = False
        if cont:
            itxt = i[0].title()
            awards.append(itxt.strip())

    return list(set(awards))