import re
import string
from rapidfuzz import fuzz
from findSpecialAwards import find_special_awards

def find_name(text):
    url_pattern = r'http?:\/\/\S+'
    cleaned_text = re.sub(url_pattern, '', text)
    text = cleaned_text.strip()
    if " in a " in text:
        in_a_pattern = r"(.+?)(?=\s(?:\bfor\b|\bat\b)|[#\.!])"

        match = re.search(in_a_pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    else:
        pattern = r"(.+?)(?=\s(?:\bin\b|\bat\b|\bfor\b)|[#\.!?])"

        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return text
    
def clean_dictionary(dictionary, threshold):
    sorted_items = sorted(dictionary.items(), key=lambda item: item[1])
    sorted_items = list(sorted_items)  

    i = 0
    while i < len(sorted_items):
        award1, count1 = sorted_items[i]
        words = award1.split()
        combine_flag = False

        for j in range(i + 1, len(sorted_items)):
            award2, count2 = sorted_items[j]
            combine_flag = True
            for word in words:
                if len(word) == 1 or word in {'in', 'a', 'or', 'golden', 'globe'}:
                    continue
                if word not in award2:
                    combine_flag = False
                    break

            if combine_flag:
                sorted_items[j] = (award2, count2 + count1)
                break 

        if combine_flag:
            sorted_items.pop(i)
        else:
            i += 1  

    filtered_items = {key: count for key, count in sorted_items if count >= threshold}
    return dict(sorted(filtered_items.items(), key=lambda item: item[1], reverse=True))

def fuzzy_clean(dictionary):
    cleaned_dict = {}
    for key in dictionary:
        add_key = True
        for cleaned_key in cleaned_dict:
            if fuzz.ratio(key, cleaned_key) > 80 or fuzz.token_sort_ratio(key, cleaned_key) > 80 or key in cleaned_key:
                cleaned_dict[cleaned_key] += dictionary[key]
                add_key = False
                break
        if add_key:
            cleaned_dict[key] = dictionary[key]

    return clean_dictionary(cleaned_dict, 25)

def find_awards_from_tweets(tweets):
    award_patterns = [
        r"wins\s+(.+)",
        r"won\s+(.+)",
        r"awarded\s+(.+)",
        r"receives\s+(.+)",
        r"nominee\s+for\s+(.+)",
        r"nominated\s+for\s+(.+)",
        r"(.+)\s+goes\s+to",
        r"(.+)\s+presented\s+to"
    ]

    award_names = {}

    for tweet in tweets:
        text = tweet['text'].lower()

        if 'best' not in text:
            continue

        for pattern in award_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                best_pattern = r"(best\s+.+)"
                best_matches = re.findall(best_pattern, match, re.IGNORECASE)
                for best in best_matches:
                    name = find_name(best).strip()
                    translation_table = str.maketrans("/" , " ", string.punctuation.replace("/", ""))
                    name = name.translate(translation_table)

                    if len(name.split()) > 10:
                        continue
                    if name not in award_names:
                        award_names[name] = 0
                    award_names[name] += 1

    names = list(fuzzy_clean(clean_dictionary(award_names, 10)).keys())
    final_names = set()
    for name in names:
        final_names.add(name)
        if 'actor' in name:
            final_names.add(name.replace('actor', 'actress'))
        if 'actress' in name:
            final_names.add(name.replace('actress', 'actor'))
        if 'actor' in name or 'actress' in name:
            split = name.split('in a')
            if len(split) == 2:
                final_names.add('best' + split[1])

    for name in find_special_awards(tweets):
        final_names.add(name.lower())

    return list(final_names)

# best television series
# best actor in a miniseries tv movie
# best actress in a miniseries tv movie
# best motion picture screenplay
# best actress tv series  comedy or musical
# best supporting actress motion picture
# best motion picture comedy or musical
# best animated feature film
# best tv comedy or musical
# best actress in a motion picture comedy or musical
# best actor tv series  comedy or musical
# best original song
# best actress in a motion picture drama
# best director
# best actor in a tv comedy or musical
# best miniseries tv movie
# best comedy actor in a television series
# best supporting actor tv series miniseries or tv movie
# best tv series drama
# best actor in a motion picture drama
# best screenplay
# best actor in a tv series drama
# best actress in a tv comedy or musical
# best comedy actress in a television series
# best motion picture drama
# best foreign language film
# best actress in a tv series drama
# best supporting actress
# best supporting actor motion picture
# best supporting actor
# best supporting actress tv series miniseries or tv movie
# best actor in a motion picture comedy or musical
# best original song motion picture award