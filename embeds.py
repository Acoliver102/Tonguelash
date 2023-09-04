import discord


def get_queue_embed(queue_members: list):
    embed = discord.Embed(title=str(len(queue_members)) + " Member(s) waiting.", description="Join with the buttons.",
                          color=0x00ff00)

    temp = ""
    for member in queue_members:
        temp += f"<@{member.id}> \n"

    if len(queue_members) == 0:
        temp = "Queue is empty."

    embed.add_field(name="Current Queue: ", value=temp, inline=False)

    return embed


def get_game_embed(game_members: list):
    embed = discord.Embed(title="Full Party:", description="Only use the buttons below AFTER the party is done.",
                          color=0x00ff00)

    temp = ""
    for member in game_members:
        temp += f"<@{member.id}> "

    embed.add_field(name="Matched with: ", value=temp, inline=False)

    return embed


def get_waiting_embed(waiting_members: list, remaining_time):
    embed = discord.Embed(title="Party found!", color=0x00ff00)

    temp = ""
    for member in waiting_members:
        temp += f"<@{member.id}> "

    embed.add_field(name="Waiting on: ", value=temp, inline=False)
    embed.add_field(name="Time remaining: ", value=str(remaining_time), inline=False)

    return embed

def get_waiting_embed_unix(waiting_members: list, end_time):
    embed = discord.Embed(title="Party found!", color=0x00ff00)

    temp = ""
    for member in waiting_members:
        temp += f"<@{member.id}> "

    embed.add_field(name="Waiting on: ", value=temp, inline=False)
    embed.add_field(name="Time remaining: ", value=end_time, inline=False)

    return embed

