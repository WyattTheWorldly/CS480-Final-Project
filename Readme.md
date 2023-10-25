# CS480 Final Project
---

## Getting setup
- Install Python =< 3.9
- Install PostgreSQL via https://www.postgresql.org/download/
- Setup Pyenv with Python 3.9 (See below)
- Install project requirements via ```pip install -r requirements.txt```
- Change default password for PostgreSQL for project with ```ALTER USER postgres WITH PASSWORD 'groupD';```
---

### Setting up Pyenv

For Windows run: ```Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"```

For Unix/MacOS run: ```curl https://pyenv.run | bash```
- Might have to add stuff for it to work with Bash / Fish mentioned [here](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv)

**Then do**
```bash
pyenv install 3.9
pyenv virtualenv 3.9 venv_480project
cd /path/to/CS480-Final-Project
pyenv activate venv_480project
```
From here, you then would run the requirements.txt, app, etc.
