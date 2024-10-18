import json
import spacy

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

# Function to extract and order keywords from the award name using spaCy
def extract_and_order_keywords_spacy(award_name):
    doc = nlp(award_name.lower())
    keywords = []

    for token in doc:
        if token.is_stop or token.is_punct:
            continue
        if token.ent_type_: 
            keywords.append((token.text, 3))
        elif token.pos_ in {'PROPN', 'NOUN'}:  
            keywords.append((token.text, 2))
        else:
            keywords.append((token.text, 1))

    # Sort keywords by importance (higher weight first)
    keywords.sort(key=lambda x: x[1], reverse=True)
    return [keyword for keyword, weight in keywords]




# Load the JSON file
with open('gg2013.json', 'r') as file:
    tweets = json.load(file)


award_name = "Best performance by an Actress in a Motion Picture - Comedy or Musical"


keywords = extract_and_order_keywords_spacy(award_name)

ranked_keywords = keywords
print(ranked_keywords)