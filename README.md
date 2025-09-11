# Hardbot

Community discord bot at hardcord.

Join us at [this.goeshard.org/discord](https://this.goeshard.org/discord)

## Instructions to contribute: 

### Create a Test Server From Our Template

- Get the current template link, use it to create a new server from the template. https://discord.new/aWG2QJFURMPB
- Now you have the server, but you need to register a bot with discord before you can use it in your server template. 

### Configure a Discord Bot Account for Your Test Bot

- Go to https://discord.com/developers/applications
- Click `New Application`; name it `MyHardbot` or whatever.
- Click `Installation` tab and set the settings like in the picture, then copy the Install link and go there.

insert pic 1

- It's very important the `Administrator` permission is given or the bot won't be able to do anything.
- Accept, accept. Your bot user should be in your template server but it will be offline.

insert pic 2

### Configure the Bot Code to Your Test Bot Account

- Download the hardbot code with git `git clone https://github.com/divSelector/hardbot.git`
- Go into the `hardbot` folder and make a file called `.env`
- Open the file and put this into it

```
DISCORD_BOT_TOKEN=
```

- Now we need to go get this token. Go back to your Discord Developer settings and under your `MyHardbot`
- Click the `Bot` tab and look for your Token string. If you can't see it, click the `Reset Token` button to get a new one.
- While you are on this tab, scroll down to where it says `Message Content Intent` and turn that checkbox on.
- Go back to the `.env` file and paste it in there

```
DISCORD_BOT_TOKEN=whatever123long456
```

### Install and Run the Bot

- Now you need to create a python virtual environment: `python -m virtualenv venv` from inside the hardbot folder.
- Activate the environment:
    On Windows: `venv\Scripts\activate`
    on Linux: `source venv/bin/activate`
- Install the dependencies: `pip install -r requirements.txt`
- Run the Bot: `python src/main.py`

When it says something like `Logged on as MyHardbot#7929` Your test bot will be online.

When you make changes to the code, bring the bot down and put it back up.

## When you're done working on your contributions

Just delete the server. The reason why is if you do another feature, you'll want the current state of the real server, and thus you'll need to recreate the server from whatever the current template link is. Permission and role and channel settings tend to get tinkered with a lot.

The good news is that you'll be able to add your bot back into new template servers with the same link as before and won't have to set all that up again.