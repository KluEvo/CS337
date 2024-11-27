# Github Link

https://github.com/KluEvo/CS337

# Setup Instructions

1. Download project files.
2. Create and activate virtual environment in the project directory.

- For macOS:
  - first create the venv: `python3.10 -m venv venv`
  - then activate: `source venv/bin/activate`
- For Windows:
  - first create the venv `python -m venv venv`
  - then activate:
    - (command prompt) `venv\Scripts\activate`
    - (powershell) `.\venv\Scripts\Activate.ps1`

3. Download the requirements:
   `pip install -r requirements.txt`
4. Download the SpaCy models:
   `python -m spacy download en_core_web_sm`
   `python -m spacy download en_core_web_trf`

# How to Run

1. Add `gg{year}.json` to the root directory of the project. ex: gg2013.json

2. Change the year to the specified year in `gg_api.py`, at line 111, at the beginning of the `main()` function.

3. In the virtual environment, run `python gg_api.py`.

4. Results will be outputted in the project root directory. The names of the results will be `gg{year}results.json` and `gg{year}results.txt` for the JSON output and human readable results.

Here is what you can find in the `gg{year}results.txt` human readable result:

- additional goal: red carpet goal with best, worst, and most controversially dressed
- all potential mined presenters (that did not end up being chosen as the presenter of an award)
- all potential mined nominees (that did not end up being chosen as the nominees of an award)

`get_nominees()`, `get_winner()`, `get_presenter()`, are run on a hardcoded list of award names, as described in the assignment. These are defined at the beginning of the `python gg_api.py` if they need to be changed to test a different year.
