import time, datetime
import sched

import discord
from discord.ext import commands, tasks

import config
import embeds

pop_message: discord.message

# keeping track of who's in a pop
popped_members = []
waiting_members = []

# ending timestamp
end_time = ""


# since these buttons only apply inside this handler they can be here
class ReadyButton(discord.ui.View):
    def __init__(self, head_text):
        super().__init__(timeout=None)
        self.header = head_text

    @discord.ui.button(label="Ready!", style=discord.ButtonStyle.primary)
    async def ready_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        accept_player(interaction.user)
        await interaction.message.edit(content=self.header,
                                       embed=embeds.get_waiting_embed_unix(waiting_members=waiting_members,
                                                                           end_time=end_time))


@tasks.loop(seconds=1, count=config.queue_timer)
async def queue_timer():
    if len(waiting_members) == 0:
        queue_timer.stop()


@queue_timer.after_loop
async def after_timer():
    return


# remove a player from the list of un-accepted players when they ready
def accept_player(player):
    global waiting_members

    if player in waiting_members:
        waiting_members.remove(player)


# seeing who in a pop is readying
async def afk_check_pop(channel, popped_players, new_players):
    global popped_members
    global waiting_members
    global pop_message
    global end_time

    # set up queue timer
    remaining_time = config.queue_timer

    end_time = f'<t:{int(time.time()) + config.queue_timer}:R>'

    scheduler = sched.scheduler(time.time, time.sleep)

    # mem issues w/ refs requires you to make copy here
    popped_members = popped_players.copy()
    waiting_members = new_players.copy()

    print(popped_members)

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
    pop_message_temp = await channel.send(content=header, view=ReadyButton(header),
                                          embed=embeds.get_waiting_embed_unix(waiting_members=waiting_members,
                                                                              end_time=end_time))
    pop_message = pop_message_temp

    # start queue countdown
    await queue_timer.start()

    # remove the expired pop message
    await pop_message_temp.delete()

    return


# clear popped members from memory
def clear_pop():
    global popped_members

    popped_members = []
