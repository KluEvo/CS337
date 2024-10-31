'''Version 0.4'''
import json
import spacy
from host import find_hosts_from_tweets_nltk
from award_names import find_awards_from_tweets
from findWinners import findWinner
from attireSentiment import clothesSentiment

nlp = spacy.load("en_core_web_sm")

# hard coded award names from gg2013answers.json
AWARD_NAMES = ["best screenplay - motion picture", 
               "best director - motion picture", 
               "best performance by an actress in a television series - comedy or musical",
               "best foreign language film",
               "best performance by an actor in a supporting role in a motion picture",
               "best performance by an actress in a supporting role in a series, mini-series or motion picture made for television",
               "best motion picture - comedy or musical",
               "best performance by an actress in a motion picture - comedy or musical",
               "best mini-series or motion picture made for television",
               "best original score - motion picture",
               "best performance by an actress in a television series - drama",
               "best performance by an actress in a motion picture - drama",
               "cecil b. demille award",
               "best performance by an actor in a motion picture - comedy or musical",
               "best motion picture - drama",
               "best performance by an actor in a supporting role in a series, mini-series or motion picture made for television",
               "best performance by an actress in a supporting role in a motion picture",
               "best television series - drama",
               "best performance by an actor in a mini-series or motion picture made for television",
               "best performance by an actress in a mini-series or motion picture made for television",
               "best animated feature film",
               "best original song - motion picture",
               "best performance by an actor in a motion picture - drama",
               "best television series - comedy or musical",
               "best performance by an actor in a television series - drama",
               "best performance by an actor in a television series - comedy or musical"]

nominees = {}

def load_tweets(year):
    json_file = 'gg' + year + '.json'
    with open(json_file, 'r') as file:
        tweets = json.load(file)
    return tweets

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    hosts = find_hosts_from_tweets_nltk(load_tweets(year), nlp)
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    awards = find_awards_from_tweets(load_tweets(year))
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    global nominees = 
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    winners = {}
    for award in AWARD_NAMES:
        winners[award] = findWinner(award, nominees[award], year, nlp)
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # none
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    ##################################
    ######### CHANGE YEAR HERE #######
    year = '2013'
    ##################################

    hosts = get_hosts(year)
    awards = get_awards(year)

    # additional goals: red carpet
    dressed_awards = clothesSentiment(year, nlp)

    data_json = {
        "hosts": hosts,
        "mined_awards": [award for award in awards]
    }

    with open("gg" + year + "results.json", "w") as json_file:
        json.dump(data_json, json_file, indent=4)

    with open("gg" + year + "results.txt", "w") as txt_file:
        txt_file.write(f"Host(s): {', '.join(hosts)}\n\n")
        txt_file.write(f"Mined Awards: \n")
        for award in awards:
            txt_file.write(f"\t{award}\n")

        txt_file.write("\n")
        for key, value in dressed_awards.items():
            txt_file.write(f"{key}: {value}\n")

    return

if __name__ == '__main__':
    main()