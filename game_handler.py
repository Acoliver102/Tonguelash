# Placeholder dicts to store game data
# Uses the game message as a key for all three
# games maps msg -> list of players
# drops maps msg -> list of dropping players
# endcalls maps msg -> list of players calling for end
games = {}
drops = {}
endcalls = {}


# example of how the dictionary based storage works
def add_player_endcall(game, player):
    endcalls[game].append(player)


# if a player wants to requeue add an endcall but don't add them to drop list
async def requeue_player(game, player):
    if player not in endcalls[game]:
        endcalls[game].append(player)


# add player endcall and add them to drop list
async def drop_player(game, player):
    if player not in endcalls[game]:
        endcalls[game].append(player)

    if player not in drops[game]:
        drops[game].append(player)


# initialize a new game
def store_game_info(game_message, players):
    games[game_message] = players
    drops[game_message] = []
    endcalls[game_message] = []


# remove a finished game from memory
def del_game_info(game_message):
    del games[game_message]
    del drops[game_message]
    del endcalls[game_message]


# given a player return list of all players in their current party
def get_party_of_player(player):
    for game, players in games.items():
        if player in players:
            return players

    return []
