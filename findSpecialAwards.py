import re
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