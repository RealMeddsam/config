import os
import json
import requests
from bs4 import BeautifulSoup

LOGIN_URL = "https://auth.roblox.com/v2/login"

def get_csrf_token():
    """Fetch a CSRF token from the login page."""
    session = requests.Session()
    resp = session.get("https://www.roblox.com/login")
    csrf_token = resp.headers.get("X-CSRF-TOKEN")
    return session, csrf_token

def login(username, password):
    session, csrf_token = get_csrf_token()
    if not csrf_token:
        raise Exception("Failed to obtain CSRF token")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": csrf_token,
        "Origin": "https://www.roblox.com",
        "Referer": "https://www.roblox.com/login"
    }
    payload = {
        "ctype": "Username",
        "username": username,
        "password": password
    }

    response = session.post(LOGIN_URL, json=payload, headers=headers)
    set_cookie = response.headers.get("Set-Cookie")
    if not set_cookie:
        raise Exception("Login failed – no cookie received")

    import re
    match = re.search(r'\.ROBLOSECURITY=([^;]+)', set_cookie)
    if not match:
        raise Exception("Could not find .ROBLOSECURITY in Set-Cookie")
    return match.group(1)

def update_json(cookie_value):
    with open("Data.json", "r") as f:
        data = json.load(f)

    data["dummyCookie"] = cookie_value

    with open("Data.json", "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    username = os.environ["ROBLOSECURITY_USERNAME"]
    password = os.environ["ROBLOSECURITY_PASSWORD"]

    try:
        new_cookie = login(username, password)
        update_json(new_cookie)
        print("Cookie refreshed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)