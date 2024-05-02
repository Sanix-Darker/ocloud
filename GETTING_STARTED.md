# GETTING STARTED

.
- Update your `example.cofig.txt` file to `config.txt` and provide a valid token if you're using you're personnal bot.

## HOW TO LAUNCH

### NO DOCKER

- Get the repo and Install dependencies:

```bash
$ git clone https://github.com/sanix-darker/ocloud.git
$ pip install -U pip poetry
$ poetry install
```

- The OCloud Telegram-bot is on another repo [OBot](https://github.com/sanix-darker/obot)

You need to start the bot First, you can use this command :
```bash
$ python -m app.bot.main
```

- You need to start the rest-api of OCloud on a new terminal too :

```bash
$ python -m app.server.main
```
