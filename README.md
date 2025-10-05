# Fantasy Forum 
THE ULTIMATE PLACE TO DISCUSS ALL STUFF FANTASY, WHETHER THAT MEANS A SIMPLE TRADE QUESTION OR JUST SHOWING OFF YOUR KNOWLEDGE. SEE HOW THE PEOPLE FEEL ABOUT PLAYERS, HEAR THE LATEST UPDATES AND WIN YOUR LEAGUE

Here is a minimal guide to run the Flask app locally.

## NEED
- Python 3.10+ 

## 1) Clone / open the project
```bash
cd /pathtotheproject
```

## 2) Create & activate a virtual environment
**Windows (PowerShell)**
```
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1
```
**macOS / Linux**
```
python3 -m venv .venv
source .venv/bin/activate
```

## 3) Install dependencies
requirements.txt has all the stuff you will need, so download that
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4) Run the app
```
python app.py
```
- The server should be live and you can open at: http://127.0.0.1:5000


## Useful pages
- Home: See all posts that are being made by other people
- About: The about page is just a quick summary of the project and what its about, the true read me
- API Demo: Extra tools for potential search of posts and data, download of JSON and helpful for people who want the data
- Login/Register: Make an account, if you already have one then ust login with it, after successfully doing that you will now be able to post, edit and comment stuff
- Posts: You can create, edit, delete your own posts and can comment on others post 

## To Run Tests
```
pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=90
```
