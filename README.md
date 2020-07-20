<p>
  <img src="./images/logo.jpg" />
  <h1>OgramCloud</h1>
  Use Telegram-servers as free "CLOUD-STORAGE-SERVER" !
</p>

## Links

Ogram split a file >= 19MB, in multiples chunks and send it throught the Telegram-bot. All the links of the running project :
- [DEMO BOT-LINK (omega_gram_bot)](https://t.me/omega_gram_bot) <br>
- [DEMO PROJECT-LINK (ogramcloud)](https://ogramcloud.com)
- [DEMO API-LINK (ogram_api)](https://ogramcloud.com/api)
- [THE DOCUMENTATION-API](https://documenter.getpostman.com/view/2696027/SzYgRaw1?version=latest)

## Requirements

- Python (3.x recommended)
- Pip3
- You need to have an account on Telegram

## How to install

- Go to https://t.me/omega_gram_bot(Or create your own bot with Botfather)
- Start the bot by hitting the START button or just write `/start` and then ENTER, you will get in response, your chat_id, you will use it with requests to ogram API to send files..
- Mute notification of the bot (Optionnal but recommended, to notreceive notifications for each chunk you're sending)
- Go to your Telegram Settings > Advanced > Automatic media download and deactive it, that will prevent telegram to automatically download a chunk of a file you're uploading !
.
- Update your `example.cofig.txt` file to `config.txt` and provide a valid token if you're using you're personnal bot.
- Install dependencies:
```shell
pip3 install -r requirements.txt
```

## How to launch

- You need to start the bot First, you can use this command :
```shell script
python -m app.bot.main
```

- You need to start the rest-api of Ogram on a new terminal too :
```shell script
python -m app.server.main
```

## How to contribute

- Create an issue with your feature/improvement
- Fork the project
- create a branch for you feature(Make sure to have the latest master-branch updates)
- Create a Pull Request to develop branch

If it's working fine and as expected, the administrator will merge it to master !


**NB: Because, it's on a Beta version, I have limited the upload-size to 100MB as a limit for the APi for tests per uploads for now!**

## Author

- Sanix-darker
