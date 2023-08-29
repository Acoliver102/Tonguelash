import discord

# TODO: Limit to only the wanted intents in the future
# intents = discord.Intents.all()
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

# bot token
token = 'Bot token here!'

# all commands start with this char
command_prefix = '~'

# number of players need for a pop
players_per_game = 10

# number of seconds queue pops take
queue_timer = 120

# minimum number of people who need to gg/domino in order to end a game
# TODO: Make games time out after x minutes to avoid locked queues
min_endcalls = 2

# whether or not players in the previous party should be added to the front or back of queue
return_to_front = False
