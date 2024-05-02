# OCLOUD

Check te [GETTING STARTED](./GETTING_STARTED.md) for self hosted tech details.

## HOW USE IT

- Go to https://t.me/omega_gram_bot(Or create your own bot with Botfather).
- Start the bot by hitting the START button or just write `/start` and then ENTER,
    you will get in response, your chat_id, you will use it with requests to ogram API to send files..
- Mute notification of the bot (Optionnal but recommended, to notreceive notifications for each chunk you're sending).
- Go to your `Telegram Settings > Advanced > Automatic` media download and deactive it,
       that will prevent telegram to automatically download a chunk of a file you're uploading!

## DEMO LINKS

Ogram split a file >= 19MB, in multiples chunks and send it throught the Telegram-bot. All the links of the running project :
- [DEMO BOT-LINK (omega_gram_bot)](https://t.me/omega_gram_bot) <br>
- [DEMO PROJECT-LINK (ogramcloud)](https://ogramcloud.com)
- [DEMO API-LINK (ogram_api)](https://ogramcloud.com/api)
- [THE DOCUMENTATION-API](https://documenter.getpostman.com/view/2696027/SzYgRaw1?version=latest)

## REQUIREMENTS

- Python (3.x recommended)
- You need to have an account on Telegram(specially having a chat_id).

## HOW TO CONTRIBUTE

- Create an issue with your feature/improvement (Optionnal but recommended).
- Fork the project.
- Create a branch for your feature/update/fix(Make sure to have the latest master-branch updates).
- Create a Pull Request to develop branch.
- After a check, it will be verify and merge to the project.

**NB: Because, it's on a Beta version, I have limited the upload-size to 100MB as a limit for the APi for tests per uploads for now!**

## AUTHOR

- [dk](https://github.com/sanix-darker)
