# bot.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

import os
import discord
from dotenv import load_dotenv

def log_in(USERNAME, PASSWORD, driver):
    driver.get("https://www.instagram.com/accounts/login")

    # refuse cookies
    try:
        print("trying")
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,\
            '/html/body/div[4]/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[2]'))).click()
    except:
        pass
    
    # input name & password
    driver.find_element(By.NAME, 'username').send_keys(USERNAME)
    driver.find_element(By.NAME, 'password').send_keys(PASSWORD)

    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, \
        '/html/body/div[2]/div/div/div[2]/div/div/div[1]/section/main/div/div/div[1]/div[2]/form/div/div[3]/button'))).click()

def get_json(username, driver):
    # get the text from site
    url = "https://www.instagram.com/web/search/topsearch/?query=" + username
    driver.get(url)
    text = driver.page_source

    # strip it from bullshit
    if "{" not in text or "users" not in text:
        return {}

    # cut off html part
    text = text[text.index("{"):]
    text = text[:text.index("<")]

    # convert it to python and return
    try:
        return json.loads(text)
    except:
        with open("response.txt", "w",encoding="utf-8")as resp_file:
            resp_file.write(text)
        return {}

def encode(string):
    return "".join([char for char in string if char.isnumeric()])

def get_most_likely(usernames, alts):
    return [alt for alt in list(alts) if encode(alt) in set([encode(name) for name in usernames])]

def check_username(driver, username, potential_alts):
    users_json = get_json(username, driver=driver)
    if users_json == {}:
        print("invalid JSON")
        return False

    exists = (False,)
    for user in users_json['users']:
        is_wanted = user['user']['full_name'] == username or user['user']['username'] == username
        if not is_wanted:
            potential_alts.add(user['user']['full_name'])
        else:
            exists = (True, user['user']['pk_id'])
            
    return exists

def checkprivateaccounts():
    with open("wanted_usernames.txt", "r", encoding="utf-8") as wanted:
        usernames_to_check = wanted.read().split(";")# WANTED usernames
    
    with open("pass.txt", "r") as pass_file:
        creds = pass_file.read().split(";")

    MAIN_USERNAME = creds[0] # YOUR username
    MAIN_PASSWORD = creds[1]


    potential_alts = set()
    exists = {}

    # open browser & log in Instagram
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    log_in(MAIN_USERNAME, MAIN_PASSWORD, driver)
    time.sleep(5)

    # iterate through the wanted usernames
    for username in usernames_to_check:
        exists[username] = check_username(driver, username, potential_alts)
        time.sleep(1)
    
    return str(exists)

load_dotenv() # load TOKEN
bot = discord.Bot()

## Logging
@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

## Slash Commands ========================================

## Hello Command
@bot.slash_command(
    name="hello",
    description="Say hello to the bot"
)
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hello! I am Butler, a bot created by the one and only @sammothxc. I am here to help you with your Hitman needs.")

## Check Private Accounts Command
@bot.slash_command(
    name="chkprivate",
    description="Run a script to check if private accounts resurfaced."
)
async def chkprivate(ctx: discord.ApplicationContext):
    await ctx.respond("Checking Hitman Watchlisted accounts...")
    chk = checkprivateaccounts()
    await ctx.respond("Done checking Hitman Watchlisted accounts:" + chk)
## Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))

## LEGWORK
