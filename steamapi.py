import requests
from time import sleep
from bs4 import BeautifulSoup
from tkinter import messagebox


def getSteamRichPresence():
        file = open('steamid.txt', 'r')
        userID = file.read()
        file.close()

        URL = f"https://steamcommunity.com/miniprofile/{int(userID) - 76561197960265728}"
        pageRequest = requests.get(URL)
        
        if pageRequest == "error":
            return ("Error while getting steam miniprofile")
        
        sleep(1)

        # turn the page into proper html formating
        soup = BeautifulSoup(pageRequest.content, "html.parser")
        
    
        #Gets current game
        gamename = soup.find("span", class_="miniprofile_game_name")
        
        
        try:
            if gamename.text == "Apex Legends":
                rich_presence = soup.find("span", class_="rich_presence")
                return [rich_presence.text, gamename.text]
            else:
                print("game not Apex Legends")
        except AttributeError:
            messagebox.showerror("Error", "User not found, in game or hidden")
            