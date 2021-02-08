# discord-bot

### Setup
1. Clone the repo.
2. Create a virtualenv and activate it.
   ```
   $ virtualenv -p python3 venv
   $ venv/bin/activate
   ```
3. Install dependencies: ``pip install -r requirements-dev.txt``
4. Run ``pre-commit install``

### Fixing lint errors.
Run `black . && isort .`
