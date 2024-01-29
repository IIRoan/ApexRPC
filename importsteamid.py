import winreg

def get_steam_id():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam\ActiveProcess")
        active_user, _ = winreg.QueryValueEx(key, "ActiveUser")
        return active_user
    except FileNotFoundError:
        print("Couldn't find the ActiveUser value.")
        return None

print(get_steam_id())
