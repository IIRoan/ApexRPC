from pypresence import Presence
from steamapi import getSteamRichPresence
import time

discord_id = "832730678859792444"
RPC = Presence(client_id=discord_id)
RPC.connect()

def mainthread():


    #Gets new SteamRPC
    steamrpc = getSteamRichPresence()
    while steamrpc is None:
        steamrpc = getSteamRichPresence()
    
    game_modes = {
        #List of normal maps
        "Storm": {
            "large_image": "stormpoint",
            "large_text": "Storm Point"
        },
        "King": {
            "large_image": "kingscanyon",
            "large_text": "King's Canyon"
        },
        "Olympus": {
            "large_image": "oympus",
            "large_text": "Olympus"
        },
        "Broken": {
            "large_image": "brokenmoon",
            "large_text": "Broken Moon"
        },
        "World": {
            "large_image": "worldsedge",
            "large_text": "World's Edge"
        },
        
        #List of mixtape
        "Skull": {
            "large_image": "skulltown",
            "large_text": "Skull Town"
        },
        "Lava": {
            "large_image": "lavasiphon",
            "large_text": "Lava Siphon"
        },
        "Fragm": {
            "large_image": "fragment",
            "large_text": "Fragment East"
        },
        "Baro": {
            "large_image": "barometer",
            "large_text": "Barometer"
        }
    }
    
    #Firing range RPC
    if steamrpc[0] == "Firing Range":
        sdetails = steamrpc[0]
        slarge_image = "training"
        slarge_text = "Firing Range"
        sstate = "Shooting bots"
        
    #Lobby RPC
    elif steamrpc[0].startswith("Lobby"):
        sdetails = steamrpc[0]
        slarge_image = "lobby"
        slarge_text = "Lobby"
        sstate = "Waiting to play"
    
    else:
        for game_mode, details in game_modes.items():
            if steamrpc[0].startswith(game_mode):
                map, gamemode = steamrpc[0].split("-")
                sdetails = map
                slarge_image = details["large_image"]
                slarge_text = details["large_text"]
                sstate = gamemode
            
            #catches if not in dict
            else:
                map, gamemode = steamrpc[0].split("-")
                sdetails = map
                slarge_image = "Lobby"
                slarge_text = "Map not found"
                sstate = gamemode

        
    #Makpes a list
    richresence = [sdetails, slarge_image, slarge_text, sstate]
    
    #Sends SteamRPC to DiscordRPC
    updatediscord(RPC, richresence)
    
    
    
    

def updatediscord(RPC, richresence):
    RPC.update(
        details= richresence[0],
        large_image=richresence[1], 
        large_text=richresence[2],
        state=richresence[3],
        small_image="logo",
        small_text="Apex Presence @IIRoan",
    )
    
    #only updates every 15 seconds, waits 14 seconds cause 1 second delay in steamapi
    time.sleep(14)
    mainthread()

mainthread()