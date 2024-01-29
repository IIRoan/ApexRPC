import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk
import re
from gamemodes import game_modes
from pypresence import Presence
import threading
import requests
from time import sleep
from bs4 import BeautifulSoup

ctk.set_appearance_mode("System")

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
            with open('steamid.txt', 'r') as file:
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
            file = open('steamid.txt', 'w')
            file.write(steam_id)
            file.close()
            self.display_message("Succesfully saved", "green", "2000")
        else:
            self.display_message("Invalid SteamID", "red", "2000")



    def enable_rpc(self):
        if self.rich_presence_checkbox.get() == 1:
            thread = threading.Thread(target=self.mainthread)
            thread.start()
        if self.rich_presence_checkbox.get() == 0:
            self.RPC.clear() 

    def display_message(self, messagetext, messagecolor, time):
        self.error_canvas = tk.Canvas(
        root, width=200, height=20, bd=0, highlightthickness=0, bg="SystemButtonFace")
        self.error_canvas.place(x=50, y=85)
        self.error_text = self.error_canvas.create_text(
                100, 10, text=messagetext, fill=messagecolor)
        root.after(time, self.remove_popup)
        
    def remove_popup(self):
        self.error_canvas.place_forget()    


    def mainthread(self):
        if self.rich_presence_checkbox.get() == 0:
            self.RPC.clear() 
        
        while self.rich_presence_checkbox.get() == 1:  
            if not self.discord_connected: # Only connect if not already connected
                discord_id = "832730678859792444"
                self.RPC = Presence(client_id=discord_id)
                self.RPC.connect()
                self.discord_connected = True
                print("connection to DiscordRPC established")
            
                      
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
                sleep(14)
                self.mainthread()
            else:
                break
            
    def getSteamRichPresence(self):
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
                self.RPC.clear()
                print("game not Apex Legends")
        except AttributeError:
            self.RPC.clear()
            print("Still erroring")
            self.display_message("User not found or not in game", "red", "1000")
                
        
        
            
    def close_app(self):
        self.stop_threads = True
        if self.RPC:
            self.RPC.clear()
        self.RPC = None
        root.destroy()
        
# Create the main application window
root = ctk.CTk()
root.title("Apex presence")
root.iconbitmap("./nessie.ico")
root.geometry("300x200")

# Initialize the app
app = ApexPresenceApp(root)


# Bind the close_app method to the window's close event
root.protocol("WM_DELETE_WINDOW", app.close_app)
# Run the application
root.mainloop()
