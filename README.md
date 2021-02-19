# Devsnest Discord Bot
![Python Versions](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-orange)

This repository is a basic roadmap to setup bot in your local system in a efficient way for everyone.

## Support!!

If you need some help for something, do join our discord community [here](https://discord.gg/ZUAJYjqD).

Want to reach us directly? You can reach us [here](https://devsnest.in/).

---------------------------------------------------------------------------------------------

## How to get started!!

1. Clone Repository
    ```shell script
    $ git clone https://github.com/devs-nest/discord-bot.git
    ```
2. Create a virtual environment
    ```shell script
    $ virtualenv venv -p python3
    $ source venv/bin/activate
    ```

3. Install packages
    ```shell script
    $ pip install -r requirements.txt  or pip3 install -r requirements.txt
    ```

4. Add values in .env
    ```
    refer to sample.env
    ```
5. Run server
    ```shell script
    $ python main.py or python3 main.py
    ```
---------------------------------------------------------------------------------------------

## Discord basics

Brief overview of some basic things...

| Variable          | What it is                                                            |
| ------------------| ----------------------------------------------------------------------|
| BOT_PREFIX        | The prefix(es) of your bot                                            |
| TOKEN             | The token of your bot                                                 |
| APPLICATION_ID    | The application ID of your bot                                        |
| OWNERS            | The user ID of all the bot owners                                     |
| BLACKLIST         | The user ID of all the users who can't use the bot                    |
| STARTUP_COGS      | The cogs that should be automatically loaded when you start the bot   |
---------------------------------------------------------------------------------------------
## Commands of the bot which you can use in your sever

|  Commands         | Purpose of command                                                    |
| ------------------| ----------------------------------------------------------------------|
| dn-help           | To get all commands with its functionality                            |
| dn-fetch          | To get list of questions                                              |
| dn-mark-done      | To mark question done                                                 |
| dn-mark-undone    | To mark question undone                                               |
| dn-mark-doubt     | To get mark question as doubt                                         | 
| dn-report         | To get progress report                                                |
| dn-leaderboard    | To get list of top 10 students of week                                |
---------------------------------------------------------------------------------------------

How can you contribute?

1. Clone the repo.
2. Create a virtualenv and activate it.
   ```shell script
   $ virtualenv -p python3 venv
   $ venv/bin/activate
   ```
3. Install dependencies.
   ```shell script
   $ pip install -r requirements-dev.txt
   ```
4. Run
   ```shell script
   $ pre-commit install
   ```
5. Create a new branch
   ```shell script
   $ git checkout -b feature/<your-feature-name>
   ```
6. Commit your changes and push it on github
   ```shell script
   $ git commit -am "<what changes you have made>" && git push origin feature/<your-feature-name>
   ```
7. Create a PR, and get it reviewed, that's it.

### Fixing lint errors.
1. Run the following command, it will autofix the errors in the files.
   ```shell script
    $ black . && isort .
   ```
2. Run the following command and fix the errors.
    ```shell script
    $ flake8 .
   ```

### Note:
Main is our holy grail, never push anything directly to main.

## Authors
* **[Devsnest](https://github.com/devs-nest)** - The community of some gems.
