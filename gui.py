import tkinter
import tkinter.messagebox
import customtkinter
import webbrowser
import re
import threading
import subprocess
from time import sleep
from main import mainthread

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue") 

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Apex Legends Presence")
        self.geometry(f"{800}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # Initialize check_var, run_loop_thread and subprocesses
        self.check_var = tkinter.StringVar()
        self.run_loop_thread = None
        self.subprocesses = []

        # Create a checkbox in the sidebar
        self.sidebar_checkbox = customtkinter.CTkCheckBox(self.sidebar_frame, text="Check me", command=self.checkbox_event, variable=self.check_var, onvalue="on", offvalue="off")
        self.sidebar_checkbox.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Apex Presence", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        
        #Displays current RPC
        self.my_variable = "Map: Placeholder"       
        self.middle_label = customtkinter.CTkLabel(self, text="Current rich presence :")
        self.middle_label.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        self.middle_label = customtkinter.CTkLabel(self, text=self.my_variable)
        self.middle_label.grid(row=2, column=1, padx=20, pady=20, sticky="nsew")
        
        #Github button
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Github", command=self.sidebar_button_event)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)


        #Theming options        
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Theme:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))



        # create main entry and button
        try:
            with open('steamid.txt', 'r') as file:
                placeholder_text = file.read().strip()
        except FileNotFoundError:
            placeholder_text = "Your Steam name or ID"
        
        self.entry = customtkinter.CTkEntry(self, placeholder_text=placeholder_text)
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Submit", command=self.id_button_event)
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # set default values
        self.appearance_mode_optionemenu.set("Dark")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def sidebar_button_event(self):
        webbrowser.open('https://github.com/')
        

    #new steamid check
    def id_button_event(self):
        steam_id = self.entry.get()
        
        if re.match(r'\d{17}$', steam_id):
            file = open('steamid.txt', 'w')
            file.write(steam_id)
            file.close()
        else:
            print("invalid Steam ID")
            
    #main checkbox event

    def checkbox_event(self):
        if self.check_var.get() == "on":
            self.checkbox_active = True
            self.run_loop_thread = threading.Thread(target=self.run_loop)
            self.run_loop_thread.start()
        else:
            self.checkbox_active = False
            if self.run_loop_thread is not None:
                self.run_loop_thread.join()

    def run_loop(self):
        while self.checkbox_active:
            mainthread()
            sleep(1)

    def destroy(self):
        self.checkbox_active = False
        if self.run_loop_thread is not None:
            self.run_loop_thread.join()
        for subprocess in self.subprocesses:
            subprocess.terminate()
        super().destroy()



if __name__ == "__main__":
    app = App()
    app.mainloop()