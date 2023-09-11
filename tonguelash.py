import discord
from discord.ext import commands
import time

import config
import game_handler
import pop_handler
import queue_handler
from config import *
import embeds

bot = commands.Bot(command_prefix=command_prefix, intents=intents)

# global bool to prevent simultaneous pops
is_popping = False


# Buttons trigger events that move members between the 3 handlers
class QueueButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("Join attempted.")
        await interaction.response.defer()
        await queue_handler.add_player_to_queue(interaction.user, get_all_players())
        # checking if queue is full
        if len(queue_handler.queue_members) == config.players_per_game:
            await pop_queue([])

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.danger)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("Leave attempted.")
        await interaction.response.defer()
        await queue_handler.remove_player_from_queue(interaction.user)


#  need to check num of endcalls after every additional change
class MatchButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Play Again!", style=discord.ButtonStyle.green)
    async def requeue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if interaction.user in game_handler.games[interaction.message]:
            await game_handler.requeue_player(interaction.message, interaction.user)

            if len(game_handler.endcalls[interaction.message]) >= config.min_endcalls:
                print("Ending Game!")
                await end_game(interaction.message)

    @discord.ui.button(label="Drop From Queue", style=discord.ButtonStyle.danger)
    async def drop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if interaction.user in game_handler.games[interaction.message]:
            await game_handler.drop_player(interaction.message, interaction.user)

            if len(game_handler.endcalls[interaction.message]) >= config.min_endcalls:
                print("Ending Game!")
                await end_game(interaction.message)


# create_queue command
# locked to admin, can comment out the @commands line to change this
@bot.command()
# @commands.has_permissions(administrator=True)
async def create_queue(ctx):
    message = await ctx.send("", view=QueueButtons(),
                             embed=embeds.get_queue_embed(queue_members=queue_handler.queue_members))
    queue_message = message
    queue_channel = message.channel

    queue_handler.initialize_queue(queue_channel, queue_message)


# pop handler - takes players alr readied from prev pop as parameter to enable backfill
async def pop_queue(prev_queue):
    global is_popping

    print("Queue Popped!")

    # avoid popping queues twice
    # pop ends once fill to ten or no game
    is_popping = True

    # get the required number of new players in from the queue
    players_needed = players_per_game - len(prev_queue)
    fill_players = queue_handler.move_first_n_members(players_needed)

    popped_queue = prev_queue + fill_players

    # update queue
    await queue_handler.queue_message.edit(content="",
                                           embed=embeds.get_queue_embed(queue_members=queue_handler.queue_members))

    # move to pop handler for the pop sequence
    await pop_handler.afk_check_pop(queue_handler.queue_channel, popped_queue, fill_players)

    # if no players waiting (all accepted) move to game creation
    if len(pop_handler.waiting_members) == 0:
        is_popping = False
        await create_game(pop_handler.popped_members)

        # see if there's another queue waiting
        if len(queue_handler.queue_members) >= config.players_per_game:
            await pop_queue([])

    # if not decide between backfill and return to queue
    else:
        temp_members = pop_handler.popped_members.copy()

        # remove all AFK members from list
        temp_members = list(filter(lambda x: x not in pop_handler.waiting_members, temp_members))

        # if there are enough then fill in and restart the check
        if len(queue_handler.queue_members) >= len(pop_handler.waiting_members):
            print("refilling")
            await pop_queue(temp_members)
        # else return all members to queue
        else:
            is_popping = False
            pop_handler.clear_pop()
            for member in temp_members:
                await queue_handler.add_player_to_queue(member, get_all_players())


# After a ready sequence can create a game
async def create_game(players):
    # to ping all players
    temp = ""

    for player in players:
        id = player.id
        temp += f'<@{id}> '

    # create game message
    game_message = await queue_handler.queue_channel.send(content=temp, view=MatchButtons(),
                                                          embed=embeds.get_game_embed(
                                                              game_members=players))

    # store game info in respective dictionaries
    game_handler.store_game_info(game_message, players)

    # remove all players from pop list
    pop_handler.clear_pop()


# Removing a game from memory after it ends and returning players to queue
async def end_game(game_msg):
    # get game info
    game_members = game_handler.games[game_msg]
    droppers = game_handler.drops[game_msg]

    # delete game information and message
    game_handler.del_game_info(game_msg)
    await game_msg.delete()

    # Add all non-dropped players to the END of queue, or the front depending on config
    if config.return_to_front:
        await queue_handler.add_players_to_queue_front(list(filter(lambda x: x not in droppers, game_members)))
        # if we can start a new game do it
        if len(queue_handler.queue_members) >= players_per_game and not is_popping:
            await pop_queue([])
    else:
        await queue_handler.add_player_list_to_queue(list(filter(lambda x: x not in droppers, game_members)))
        if len(queue_handler.queue_members) >= players_per_game and not is_popping:
            await pop_queue([])


# convenience function to avoid letting people into queue who are already somewhere else
def get_all_players():
    all_players = queue_handler.queue_members + pop_handler.popped_members

    for game_members in game_handler.games.values():
        all_players += game_members

    return all_players


# RUN THE BOT (VERY IMPORTANT)
bot.run(token)
