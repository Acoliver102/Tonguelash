# Tonguelash
## Pull people together and launch parties quicker!

Tonguelash is a Discord queueing bot I tried to make as simple as possible. It's still a work in progress, but as time goes on I'll try to keep improving it.

It runs off of python and requires discord.py.

Tonguelash is designed to be a simple as possible to set up and host. All you need is your bot's token and you should be good to go.

Credit goes to BigBoot/fang as the bot that inspired me to make this, both positively and negatively.

## What is Tonguelash? Why should I use it over other queue bots?
It's just a way of making a line of people and then getting X number of people who are here pulled into separate parties. Could be useful for LFG servers, for instance.

It's designed to be easy to set-up and modify, so you can use it as is or make slight tweaks to it to suit your needs. Less features means I can focus on making it more robust.

It also uses a AFK check to avoid creating parties with people who left themselves in queue overnight and are now gone - if you've ever played a Riot game you know the system.

## What doesn't Tonguelash do?
In order to avoid adding extra elements to set up such as databases, Tonguelash does not save any persistent user info. If you want to keep stats or preferences, you should look elsewhere.

It's very barebones right now, so it may not be the most pleasing on the eyes. We're... working on that. UPDATE: We worked on it.

I have not been able to test this bot at scale yet, so keep in mind in may be a little buggy, especially with a higher number of users. If you're filling up 3-5+ parties at a time, then this bot may be a little slower than alternatives.

## Quick Setup
To run the bot, all you need to do is pass the bot token to the config.py file and run tonguelash.py. You will need to install discord.py first.

To make a queue, just run the ~create_queue command in the appropriate channel. The bot will create a qsueue and all subsequent messages will be directed to that channel.

