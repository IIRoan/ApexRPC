import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk
import re
from gamemodes import game_modes
from pypresence import Presence, exceptions
import threading
import requests
from time import sleep
from bs4 import BeautifulSoup
import os
import sys

ctk.set_appearance_mode("System")

#Constants
DISCORD_ID = "832730678859792444"
STEAMID_FILE = 'steamid.txt'
REFRESH_INTERVAL = 14000
DISCONNECT_INTERVAL = 2000

class ApexPresenceApp:
    def __init__(self, root):
        self.discord_connected = False
        self.RPC = None
        self.stop_threads = False
        # Title
        header_font = ctk.CTkFont(family="Cascadia", size=20)
        self.title_label = ctk.CTkLabel(
            root, text="Apex presence", font=header_font)
        self.title_label.pack(padx=20, pady=10)

        # Steam ID input field
        try:
            with open(STEAMID_FILE, 'r') as file:
                placeholder_text = file.read().strip()
        except FileNotFoundError:
            placeholder_text = "Your Steam name or ID"

        self.input_field = ctk.CTkEntry(
            root, width=200, placeholder_text=placeholder_text)
        self.input_field.pack(padx=20, pady=10)

        # Submit button itself
        self.submit_button = ctk.CTkButton(
            root, text="Submit", command=self.id_button_event)
        self.submit_button.pack(padx=30, pady=10)

        # Checkbox to Enable Rich Presence
        self.rich_presence_checkbox = tk.IntVar()
        self.rich_presence_checkbox = ctk.CTkCheckBox(
            root, text="Enable Rich Presence", command=self.enable_rpc)
        self.rich_presence_checkbox.pack(padx=20, pady=10)

    def id_button_event(self):
        steam_id = self.input_field.get()

        if re.match(r'\d{17}$', steam_id):
            file = open(STEAMID_FILE, 'w')
            file.write(steam_id)
            file.close()
            self.display_message("Succesfully saved", "green", "2000")
        else:
            self.display_message("Invalid SteamID", "red", "2000")



    def enable_rpc(self):
        if self.rich_presence_checkbox.get() == 1:
            thread = threading.Thread(target=self.connect_to_discord)
            thread.start()
        if self.rich_presence_checkbox.get() == 0:
            self.RPC.clear() 

    def display_message(self, messagetext, messagecolor, time):
        # Remove any existing popup
        if hasattr(self, 'error_canvas'):
            self.remove_popup()

        self.error_canvas = tk.Canvas(
            root, width=200, height=20, bd=0, highlightthickness=0, bg="black")
        self.error_canvas.place(x=50, y=85)
        self.error_text = self.error_canvas.create_text(
                100, 10, text=messagetext, fill=messagecolor)
        root.after(time, self.remove_popup)
            
    def remove_popup(self):
        if hasattr(self, 'error_canvas'):
            self.error_canvas.delete('all')
            delattr(self, 'error_canvas')


    def connect_to_discord(self):
        if self.rich_presence_checkbox.get() == 0:
            self.RPC.clear() 
        
        while self.rich_presence_checkbox.get() == 1:  
            if not self.discord_connected: # Only connect if not already connected
                try:
                    self.RPC = Presence(client_id=DISCORD_ID)
                    self.RPC.connect()
                    self.discord_connected = True
                    self.display_message("connection to Discord established", "green", "2000")
                except exceptions.DiscordNotFound:
                    self.display_message("Could not find Discord.", "red", "2000")
                except Exception as e:
                    self.display_message("Error connecting to Discord.", "red", "2000")

            # Gets new SteamRPC
            steamrpc = self.getSteamRichPresence()
            while steamrpc is None:
                steamrpc = self.getSteamRichPresence()

            # Firing range RPC
            if steamrpc[0] == "Firing Range":
                sdetails = steamrpc[0]
                slarge_image = "training"
                slarge_text = "Firing Range"
                sstate = "Shooting bots"

            # Lobby RPC
            elif steamrpc[0].startswith("Lobby"):
                sdetails = steamrpc[0]
                slarge_image = "lobby"
                slarge_text = "Lobby"
                sstate = "Waiting to play"


    	    #Splits the scraped data to be displayed correctly
            else:
                for game_mode, details in game_modes.items():
                    if steamrpc[0].startswith(game_mode):
                        map, gamemode = steamrpc[0].split("-")
                        sdetails = map
                        slarge_image = details["large_image"]
                        slarge_text = details["large_text"]
                        sstate = gamemode
                        

            # Sends SteamRPC to DiscordRPC
            self.RPC.update(
                details=sdetails,
                large_image=slarge_image,
                large_text=slarge_text,
                state=sstate,
                small_image="logo",
                small_text="Apex Presence",
            )
            self.display_message(f"{sdetails} on {sstate}", "black", "14000")

            if self.rich_presence_checkbox.get() == 1:
                sleep(REFRESH_INTERVAL)
                self.connect_to_discord()
            else:
                break
            
    def getSteamRichPresence(self):
        file = open(STEAMID_FILE, 'r')
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

        attempts = 0
        max_attempts = 20
        

        while attempts < max_attempts:
            try:
                if gamename.text == "Apex Legends":
                    rich_presence = soup.find("span", class_="rich_presence")
                    return [rich_presence.text, gamename.text]
                else:
                    self.RPC.clear()
                    print("game not Apex Legends")
            except AttributeError:
                attempts += 1
                self.RPC.clear()
                self.display_message("User not found or not in game", "red", "1000")
                sleep(1)
                if attempts >= max_attempts:
                    self.remove_popup()
                    raise Exception("Maximum attempts reached")

                
        
        
            
    def close_app(self):
        self.stop_threads = True
        if self.RPC:
            self.RPC.clear()
        self.RPC = None
        root.destroy()
      

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)      
        
# Create the main application window
root = ctk.CTk()
root.title("Apex presence")
icon_path = resource_path('./nessie.png') # Use PNG for Linux
icon = tk.PhotoImage(file=icon_path)
root.iconphoto(False, icon)
root.geometry("300x200")

# Initialize the app
app = ApexPresenceApp(root)


# Bind the close_app method to the window's close event
root.protocol("WM_DELETE_WINDOW", app.close_app)
# Run the application
root.mainloop()
