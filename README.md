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

Use `python gg_api.py` to run the code. This will create outputs `gg{year}results.json` and `gg{year}results.txt` for the JSON output and human readable results. The `.txt` file includes the output for the additional goal we completed, the red carpet goal with best, worst, and most controversially dressed.

The `python gg_api.py` file assumes there is a `gg{year}.json` file containing the tweets to load. The year can be changed at the beginning of the `main()` function in the `python gg_api.py` file.

`get_nominees()`, `get_winner()`, `get_presenter()`, are run on a hardcoded list of award names, as described in the assignment. These are defined at the beginning of the `python gg_api.py` if they need to be changed to test a different year.
