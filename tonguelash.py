import discord
from discord.ext import commands
import time

# LONGTERM LIST OF FEATURES:
# Button to ping unaccepted players
# Button to ping all players in a game
# Button to deny a queue pop and trigger refills early to avoid wasting time
# Need to test how multiple games affects the bot
# Need to test with more people in general

# TODO: Limit to only the wanted intents in the future
intents = discord.Intents.all()
# intents.message_content = True
# intents.reactions = True

# bot token
token = 'Bot Token Here!'

# TODO: Move command_prefix to a constants file
bot = commands.Bot(command_prefix='~', intents=intents)

# placeholders until the global vars are init with first call
queue_channel = bot.get_channel(0)
queue_message = 0

# placeholder until a new pop_message is created
pop_message = 0

# number of players need for a pop
# TODO: Move to a constants file
players_per_game = 10

# placeholders for data storage list
# maybe make a data struct class for this?
queue_members = []
popped_members = []
waiting_members = []

# global bool to prevent simultaneous pops
is_popping = False

# number of seconds queue pops take
queue_timer = 120

# minimum number of people who need to gg/domino in order to end a game
# TODO: Make games time out after x minutes to avoid locked queues
min_endcalls = 2

# Placeholder dicts to store game data
# Uses the game message as a key for all three
# games maps msg -> list of players
# drops maps msg -> list of dropping players
# endcalls maps msg -> list of players calling for end
games = {}
drops = {}
endcalls = {}


# Starting work on Buttons
class QueueButtons(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await add_player_to_queue(interaction.user)

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.danger)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await remove_player_from_queue(interaction.user)


class ReadyButton(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Ready!", style=discord.ButtonStyle.primary)
    async def ready_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        accept_player(interaction.user)


class MatchButtons(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Play Again!", style=discord.ButtonStyle.green)
    async def requeue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if interaction.user in games[interaction.message]:
            await requeue_player(interaction.message, interaction.user)

    @discord.ui.button(label="Drop From Queue", style=discord.ButtonStyle.danger)
    async def drop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if interaction.user in games[interaction.message]:
            await drop_player(interaction.message, interaction.user)


# reaction handler
# will be deprecated soon but keeping this in as backup
@bot.event
async def on_reaction_add(reaction, user):
    reacted_message = reaction.message

    # ignore own reaction to posts
    if user == bot.user:
        pass
    # reactions to queue
    elif reacted_message == queue_message:
        # add/remove player and remove the reaction
        if reaction.emoji == "👍":
            await reaction.remove(user)
            await add_player_to_queue(user)
        elif reaction.emoji == "👎":
            await reaction.remove(user)
            await remove_player_from_queue(user)
    # reactions to a pop
    elif reacted_message == pop_message:
        # ready a player and remove reaction
        if reaction.emoji == "👍":
            await reaction.remove(user)
            accept_player(user)
    # reaction to an ongoing game
    elif reacted_message in games.keys():
        # remove reaction and act accordingly
        # check if player is actually in the game they are reacting to
        # TODO: Assigning game nums to avoid confusion
        if reaction.emoji == "👍":
            await reaction.remove(user)
            if user in games[reacted_message]:
                await requeue_player(reacted_message, user)
        if reaction.emoji == "👎":
            await reaction.remove(user)
            if user in games[reacted_message]:
                await drop_player(reacted_message, user)


# create_queue command
# TODO: Command integration for: queue reset, queue ping, and players ping
@bot.command()
async def create_queue(ctx):
    # storage for where the queue message is located
    global queue_message
    global queue_channel

    message = await ctx.send("Current Queue:", view=QueueButtons())
    queue_message = message
    queue_channel = message.channel

    # deprecated now with button functionality
    # await message.add_reaction("👍")
    # await message.add_reaction("👎")


# method called on react
async def add_player_to_queue(member: discord.Member):
    global queue_members
    global queue_message

    # avoid double join from people in queue, pop, and game
    all_players = queue_members + popped_members

    for game_members in games.values():
        all_players += game_members

    if member not in all_players:
        queue_members.append(member)

    # add new player to queue
    await queue_message.edit(content=get_queue_content())

    # trigger queue pop if enough for a game
    if len(queue_members) >= players_per_game and not is_popping:
        await pop_queue([])


# convenience member to quickly get the formatting from queue_members
# could be nice to have similar functions for pops and games in the future that could be moved to a lib
def get_queue_content():
    temp = "Current Queue:  \n"

    for member in queue_members:
        id = member.id
        temp += f"<@{id}> \n"

    return temp


# remove a player from the list of un-accepted players when they ready
def accept_player(player):
    global waiting_members

    if player in waiting_members:
        waiting_members.remove(player)


# if a player wants to requeue add an endcall but don't add them to drop list
async def requeue_player(game, player):
    if player not in endcalls[game]:
        endcalls[game].append(player)

    if len(endcalls[game]) >= min_endcalls:
        print("Ending Game!")
        await end_game(game)


# add player endcall and add them to drop list
async def drop_player(game, player):
    if player not in endcalls[game]:
        endcalls[game].append(player)

    if player not in drops[game]:
        drops[game].append(player)

    if len(endcalls[game]) >= min_endcalls:
        print("Ending Game!")
        await end_game(game)


# pop handler - takes players alr readied from prev pop as parameter
async def pop_queue(prev_queue):
    global is_popping
    global queue_members

    print("Queue Popped!")

    # avoid popping queues twice
    # pop ends once fill to ten or no game
    is_popping = True

    # get the required number of new players in from the queue
    players_needed = players_per_game - len(prev_queue)
    fill_players = queue_members[:players_needed]

    popped_queue = prev_queue + fill_players
    remaining_queue = queue_members[players_needed:]

    # remove the popped players from queue
    queue_members = remaining_queue

    # update queue and initiate the afk check sequence
    await queue_message.edit(content=get_queue_content())
    await afk_check_pop(popped_queue, fill_players)


# seeing who in a pop is readying
async def afk_check_pop(popped_players, new_players):
    global pop_message
    global popped_members
    global waiting_members

    # set up queue timer
    remaining_time = queue_timer

    # mem issues w/ refs requires you to make copy here
    popped_members = popped_players.copy()
    waiting_members = new_players.copy()

    print(len(popped_members))

    # create a header listing match members so you can see who's actually in the match
    header = "Match Ready For:  \n"

    for member in popped_players:
        id = member.id
        header += f'<@{id}> '

    # this gets updated each loop cycle
    temp = header + "\nWaiting On: \n "

    for member in waiting_members:
        id = member.id
        temp += f'<@{id}> '

    temp += "\nTime Remaining: " + str(remaining_time)

    # add message and reaction
    # copy needed to fix mem issues with async
    pop_message_temp = await queue_channel.send(content=temp, view=ReadyButton())
    pop_message = pop_message_temp
    # await pop_message.add_reaction("👍")

    # game state holder
    has_game = False

    # TODO: There has to be a way to do this without time.sleep
    # Maybe get a starting timestamp and round from current time?
    while remaining_time >= 0:
        # Update with remaining players and timer
        temp = header + "\nWaiting On: \n "

        for member in waiting_members:
            id = member.id
            temp += f'<@{id}> '

        temp += "\nTime Remaining: " + str(remaining_time)

        await pop_message.edit(content=temp)

        # Wait a second
        time.sleep(1)

        remaining_time -= 1

        # if everyone is ready start the match
        # Probably could be done without the bool but it's not a big deal
        if len(waiting_members) == 0:
            global is_popping
            is_popping = False
            has_game = True
            break

    # Pop sequence ends when a match starts or time runs out
    is_popping = False

    print(len(popped_members))

    if has_game:
        await create_game(popped_players)
    else:
        # backfill mech if time runs out
        # check if there are enough players to make a new game
        temp_members = popped_members.copy()
        print(temp_members[2])

        # for player in temp_members:
        #     print(player.display_name)
        #     if player in waiting_members:
        #         print("Removed " + player.display_name)
        #         temp_members.remove(player)
        #     else:
        #         print("Keeping " + player.display_name)\

        temp_members = filter(lambda x: x not in waiting_members, temp_members)

        # if there are enough then fill in and restart the check
        if len(queue_members) >= len(waiting_members):
            print("refilling")
            await pop_queue(popped_members)
        # return all members to queue
        else:
            popped_members = []
            for member in temp_members:
                await add_player_to_queue(member)

    # remove the expired pop message
    await pop_message_temp.delete()

    return


# Drop a player from queue and update message.
async def remove_player_from_queue(member: discord.Member):
    global queue_members
    global queue_message

    try:
        queue_members.remove(member)
    except ValueError:
        pass

    await queue_message.edit(content=get_queue_content())


# After a ready sequence can create a game
async def create_game(players):
    global games
    global popped_members
    global drops

    # Could also be moved to a convenience function
    temp = "Game With: \n "

    # This was for Feanor please don't ask
    # EDIT: this bit was stupid and I'm gonna fix it now
    # ask him about what the bit was about
    for player in popped_members:
        id = player.id
        temp += f'<@{id}> '

    # create game message
    game_message = await queue_channel.send(content=temp, view=MatchButtons())
    # await game_message.add_reaction("👍")
    # await game_message.add_reaction("👎")

    # store game info in respective dictionaries
    # placeholder info for drops/endcalls
    games[game_message] = popped_members.copy()
    drops[game_message] = []
    endcalls[game_message] = []

    popped_members = []


# Removing a game from memory after it ends and returning players to queue
async def end_game(game_msg):
    # get game info
    game_members = games[game_msg]
    droppers = drops[game_msg]

    # delete game info and message
    del games[game_msg]
    del drops[game_msg]
    del endcalls[game_msg]

    # Add all non-dropped players to the END of queue.
    # TODO: Add an option to add them to the front.
    for member in game_members:
        if member not in droppers:
            await add_player_to_queue(member)

    await game_msg.delete()


# RUN THE BOT (VERY IMPORTANT)
bot.run(token)
