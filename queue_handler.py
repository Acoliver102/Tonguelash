import discord
from embeds import get_queue_embed

# file contains all the global variables that track the state of the queue
# in the future I might move this to be a Class so that I may have multiple simultaneous queues

# variables for data storage
queue_channel: discord.channel
queue_message: discord.Message

queue_members = []


# make note of where the queue actually is located
def initialize_queue(channel: discord.channel, message: discord.Message):
    global queue_channel
    global queue_message

    queue_channel = channel
    queue_message = message


# method called on button press
async def add_player_to_queue(member: discord.Member, all_players: list):
    global queue_members
    global queue_message

    if member not in all_players:
        queue_members.append(member)

    # add new player to queue
    await queue_message.edit(content="", embed=get_queue_embed(queue_members=queue_members))


# Drop a player from queue and update message.
async def remove_player_from_queue(member: discord.Member):
    global queue_members
    global queue_message

    try:
        queue_members.remove(member)
    except ValueError:
        pass

    await queue_message.edit(content="", embed=get_queue_embed(queue_members=queue_members))


# method called on party reset
# move an entire list of players to the front of queue
async def add_players_to_queue_front(member_list: list):
    global queue_members
    global queue_message

    queue_members = member_list + queue_members

    # add new player to queue
    await queue_message.edit(content="", embed=get_queue_embed(queue_members=queue_members))


# move an entire list of players to the back of queue
async def add_players_to_queue_back(member_list: list):
    global queue_members
    global queue_message

    queue_members = queue_members + member_list

    # add new player to queue
    await queue_message.edit(content="", embed=get_queue_embed(queue_members=queue_members))


# return the first n members and remove them from memory
# used for backfills and clearing queue
def move_first_n_members(n: int):
    global queue_members

    temp = queue_members[:n]
    queue_members = queue_members[n:]

    return temp

