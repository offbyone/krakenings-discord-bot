# Krakenings Discord Bot

This bot exists to occasionally send game info to channels in the Krakenings Discord. 

## Usage

```
docker run -e BOT_TOKEN -e GUILD_ID \
    -v bot-config.toml:/etc/bot-config.toml:ro 
    ghcr.io/offbyone/krakenings-discord-bot:latest
```

You can get the bot token from the discord developer portal. The Guild ID is the Discord Server ID. You can get it by enabling developer settings in discord and right clicking on the server. The CHANNEL_ID should be the ID of the voicechannel where the events will be held.

## Adding the bot to a Server

Add the Bot to the Server (only Admins can do this!)

Go to https://discord.com/oauth2/authorize?client_id={clientid}&scope=bot&permissions=8589934592

where the clientid is the id of the bot.

## Building

``` shellsession
docker build -t ghcr.io/offbyone/krakenings-discord-bot:latest . 
```

This will be automatically built on PRs and pushes to `main`, too
