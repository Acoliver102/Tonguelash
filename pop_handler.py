# placeholder until a new pop_message is created
import time

import discord
import config
import embeds

pop_message: discord.message

# keeping track of who's in a pop
popped_members = []
waiting_members = []


# since these buttons only apply inside this handler they can be here
class ReadyButton(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Ready!", style=discord.ButtonStyle.primary)
    async def ready_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        accept_player(interaction.user)


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

    # set up queue timer
    remaining_time = config.queue_timer

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
    pop_message_temp = await channel.send(content=header, view=ReadyButton(),
                                          embed=embeds.get_waiting_embed(waiting_members=waiting_members,
                                                                         remaining_time=remaining_time))
    pop_message = pop_message_temp

    # TODO: There has to be a way to do this without time.sleep
    # TODO: Investigate using sched module
    # Maybe get a starting timestamp and round from current time?
    # Investigate using UNIX timestamps to display remaining time
    while remaining_time >= 0:
        # Update with remaining players and timer
        temp = header + "\nWaiting On: \n "

        for member in waiting_members:
            id = member.id
            temp += f'<@{id}> '

        temp += "\nTime Remaining: " + str(remaining_time)

        await pop_message.edit(content=header, embed=embeds.get_waiting_embed(waiting_members=waiting_members,
                                                                              remaining_time=remaining_time))

        # Wait a second
        time.sleep(1)

        remaining_time -= 1

        # if everyone is ready start the match
        # Probably could be done without the bool but it's not a big deal
        if len(waiting_members) == 0:
            break

    # remove the expired pop message
    await pop_message_temp.delete()

    return


# clear popped members from memory
def clear_pop():
    global popped_members

    popped_members = []
