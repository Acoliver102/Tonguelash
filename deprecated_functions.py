# This file contains older functions from previous stages of the project.
# Cross reference w/ description to see the last versions where they were used if you want a reference on how they work
import discord

from player_handler import add_player_to_queue, remove_player_from_queue, accept_player, drop_player, requeue_player
from tonguelash import queue_message


# convenience member to quickly get the formatting from queue_members
# could be nice to have similar functions for pops and games in the future that could be moved to a lib
# removed when we started using embeds instead of raw text
def get_queue_content(queue_members: list):
    temp = "Current Queue:  \n"

    for member in queue_members:
        id = member.id
        temp += f"<@{id}> \n"

    return temp


# update to avoid using time.sleep in afk
# still a little buggy but I'm being rate-limited and I'm not sure if that's the problem
# Tried to use a cog instead of sleep
# so buggy I'm locking it in here as a MLS
# Got me rate limited on several occasions
# DO NOT TOUCH UNLESS YOU'RE VERY CONFIDENT

'''
class AfkTimerCog(commands.Cog):
    def __init__(self, popped_players):
        self.remaining_time = queue_timer
        # self.timer.start()
        self.edit_message = ""
        self.header = "Match Ready For:  \n"
        self.popped_list = popped_players

        for member in popped_players:
            self.header += f'<@{member.id}> '

    def cog_unload(self):
        self.timer.cancel()

    def get_time(self):
        return self.remaining_time

    async def start_timer(self):
        global is_popping

        is_popping = True
        self.remaining_time = queue_timer

        self.edit_message = await queue_channel.send(content=self.header, view=ReadyButton(), embed=get_waiting_embed(queue_timer))

        self.timer.start()

    @tasks.loop(seconds=1.0)
    async def timer(self):
        global is_popping
        global popped_members

        await self.edit_message.edit(content=self.header, view=ReadyButton(), embed=get_waiting_embed(self.remaining_time))
        self.remaining_time -= 1

        if len(waiting_members) == 0:
            await create_game(self.popped_list)
            is_popping = False
            print("deleted msg")
            await self.edit_message.delete()
            self.timer.stop()

        if self.remaining_time < 0:
            is_popping = False
            temp_members = filter(lambda x: x not in waiting_members, self.popped_list)

            # if there are enough then fill in and restart the check
            if len(queue_members) >= len(waiting_members):
                print("refilling")
                await pop_queue(self.popped_list)
                print("deleted msg")
                await self.edit_message.delete()
                self.timer.stop()
            # return all members to queue
            else:
                popped_members = []
                for member in temp_members:
                    await add_player_to_queue(member)
                print("deleted msg")
                await self.edit_message.delete()
                self.timer.stop()
'''


# reaction handler
# will be deprecated soon but keeping this in as backup
# removed when we moved to buttons instead of reacts

# @bot.event
async def on_reaction_add(reaction, user, pop_message=discord.Message, games=dict):
    # placeholder to avoid errors
    bot = ""

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
