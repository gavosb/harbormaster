#The Harbor Master bot - main file
#main.py
#Signed: Gavin

import os
import random
import discord
import sqlite3
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='SALUTE:')
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'harbor.db')

# database functions
def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

def access_database(command, *argv):
    conn = db_connect()
    harbor = conn.cursor()
    try:
        if argv:
            harbor.execute(command, (argv[0],))
            conn.commit()
        else:
            harbor.execute(command)
    except sqlite3.Error as er:
        print('SQLite erri8\]kmM  or: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
    conn.commit()
    harbor.close()

# handler functions
@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'CODE ORANGE: {args[0]}\n')
        else:
            raise

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Access Denied.')

# primary event functions
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Greetings, {member.name}. Welcome to The Maritime Federation.'
    )

@bot.command(name='vote')
@commands.has_role('Governor')
async def voting_command(ctx, *argv):
    response = "Received."
    print('voting command...')
    arg = [item for item in argv]
    print(arg)
    conn = db_connect()
    harbor = conn.cursor()
    harbor.execute("SELECT * FROM voting")
    print('voting table: ')
    harborL = [item for item in harbor.fetchall()]
    harbor.close()
    print(harborL)
    state = 'none'
    harbor = conn.cursor()
    harbor.execute("SELECT for, against FROM voting")
    results = harbor.fetchall()
    harbor.close()
    print(results)
    forvote = 0
    againstvote = 0
    try:
        forvote = results[0][0]
        againstvote = results[0][1]
    except:
        pass
    try:
        state = harborL[0][0]
        print('state')
        print(state)
    except IndexError:
        print("failure to alter state")
    if arg[0] == "toggle":
        print("toggling")
        
        if state == '0': # set state to true, resume voting
            print("starting vote")
            add_item = "UPDATE voting SET state = 1 WHERE state = '0'"
            access_database(add_item)
            response = "Vote initiated. " + "for: " + str(forvote) + ", Against: " + str(againstvote)
            
        elif state == '1': #set state to false, end voting
            print("cancelling vote")
            add_item = "UPDATE voting SET state = 0 WHERE state = '1'"
            access_database(add_item)
            response = ":::FINAL RESULTS:::  " + "for: " + str(forvote) + ", Against: " + str(againstvote)
            
            access_database("UPDATE voting SET for = 0 WHERE state = '0'")
            access_database("UPDATE voting SET against = 0 WHERE state = '0'")
            
        elif state == 'none': #initially creates a new vote for a new database
            print("vote created")
            add_item = "INSERT INTO voting VALUES (true, 0, 0)"
            access_database(add_item) #
            response = "Vote initiated. " + "for: " + str(forvote) + ", Against: " + str(againstvote)
            
    elif arg[0] == "for" and state=="1":
        access_database("UPDATE voting SET for = for + 1 WHERE state = '1'")
        
    elif arg[0] == "against" and state=="1":
        access_database("UPDATE voting SET against = against + 1 WHERE state = '1'")
        
    elif arg[0] == "result" and state=="1": #show results
        response = "For: " + str(forvote) + ", Against: " + str(againstvote)
        
    else:
        response = "Command not available."
    await ctx.send(response)
    
    
@bot.command(name='blacklist', help='Lists untrustworthy merchants.')
async def blacklist_command(ctx):
    #blacklist = load_list("SELECT * FROM blacklist")
    conn = db_connect()
    harbor = conn.cursor()
    harbor.execute("SELECT name FROM blacklist")
    blacklist = []
    for i in harbor.fetchall():
        blacklist.append(''.join(filter(str.isalpha, i)))
    print(blacklist)
    harbor.close()
    response = "LIST OF LOW REPUTATION MERCHANTS: " + str(blacklist)[1:-1] 
    await ctx.send(response)

@bot.command(name='blacklist-modify')
@commands.has_role('Governor')
async def blacklist_command(ctx, option, username):
    response = "Blacklist modified."
    if option == "add":
        print("adding...")
        add_item = "INSERT INTO blacklist (name) VALUES (?)"
        access_database(add_item, username)
        response = username + " " + "added to list of low reputation merchants."
        
    elif option == "remove":
        print("deleting...")
        delete_item = "DELETE FROM blacklist WHERE name='" + username + "'"
        access_database(delete_item)
        response = username + " " + "removed from list of low reputation merchants."
    await ctx.send(response)


# main on ready event for the discord bot
@bot.event
async def on_ready():
    print(f'{bot.user} has connected.')
    # initializes databases if they do not exist
    create_blacklist = """
        CREATE TABLE IF NOT EXISTS blacklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
        );
        """
    create_voting = """
        CREATE TABLE IF NOT EXISTS voting (
        state TEXT NOT NULL,
        for INT NOT NULL,
        against INT NOT NULL
        );
        """
    conn = db_connect()
    harbor = conn.cursor()
    harbor.execute(create_blacklist)
    harbor.execute(create_voting)
    conn.commit()
    harbor.close()
        
bot.run(TOKEN)
