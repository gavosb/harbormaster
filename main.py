#The Harbor Master bot - main file
#main.py
#Signed: Gavin

import os
import random
import discord
import aiosqlite
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='SALUTE:')
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'harbor.db')

# database functions
async def db_connect(db_path=DEFAULT_PATH):
    con = await aiosqlite.connect(db_path)
    return con

async def access_database(command, *argv):
    conn = await db_connect()
    harbor = await conn.cursor()
    try:
        if argv:
            await harbor.execute(command, (argv[0],))
            await conn.commit()
        else:
            await harbor.execute(command)
    except await aiosqlite.Error as er:
        print('SQLite erri8\]kmM  or: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
    await conn.commit()
    await harbor.close()

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

@bot.command(name='history')
async def history_command(ctx):

    history = [
        (
            'Halifax was founded in November of 2020 by most excellent Commissar g_posting and Magistrate Geotore.'
        ),
        (
            'Halifax and Nova Scotia contributed to the Keep of Knowledge on December 22nd, 2020. '
            'May peace be everlasting in the east.'
        ),
        (
            'The Maritime Federation adopted both Scots Gaelic and English as official languages to represent the national culture in full.'
        )
    ]
    response = random.choice(history)
    await ctx.send(response)

@bot.command(name='quotes')
async def quotes_command(ctx):
    
    quotes = [
        (
            "One Defends, The Other Conquers - g_posting"
        )
    ]
    response = random.choice(quotes)
    await ctx.send(response)
    
@bot.command(name='locations')
async def locations_command(ctx):
    
    locations = [
        (
            "Grifith: -30304, -19312"
        ),
        (
            "Akimiski: -27948, -18138"
        ),
        (
            "Bar Harbor: -23478, -15044"
        ),
        (
            "Gaspé: -21972, -16648"
        ),
        (
            "St. Johns: -17990, -16256"
        ),
        (
            "New Hungary: -21534, -15806"
        ),
        (
            "Halifax: -21738, -15201"
        )
    ]
    response = random.choice(locations)
    await ctx.send(response)
    

    
@bot.command(name='vote')
@commands.has_role('Governor')
async def voting_command(ctx, *argv):
    response = "Received."
    print('voting command...')
    arg = [item for item in argv]
    print(arg)
    conn = await db_connect()
    harbor = await conn.cursor()
    await harbor.execute("SELECT * FROM voting")
    print('voting table: ')
    harborL = [item for item in await harbor.fetchall()]
    await harbor.close()
    print(harborL)
    state = 'none'
    harbor = await conn.cursor()
    await harbor.execute("SELECT for, against FROM voting")
    results = await harbor.fetchall()
    await harbor.close()
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
            await access_database(add_item)
            response = "Vote initiated. " + "for: " + str(forvote) + ", Against: " + str(againstvote)
            
        elif state == '1': #set state to false, end voting
            print("cancelling vote")
            add_item = "UPDATE voting SET state = 0 WHERE state = '1'"
            await access_database(add_item)
            response = ":::FINAL RESULTS:::  " + "for: " + str(forvote) + ", Against: " + str(againstvote)
            
            await access_database("UPDATE voting SET for = 0 WHERE state = '0'")
            await access_database("UPDATE voting SET against = 0 WHERE state = '0'")
            
        elif state == 'none': #initially creates a new vote for a new database
            print("vote created")
            add_item = "INSERT INTO voting VALUES (true, 0, 0)"
            await access_database(add_item) #
            response = "Vote initiated. " + "for: " + str(forvote) + ", Against: " + str(againstvote)
            
    elif arg[0] == "for" and state=="1":
        await access_database("UPDATE voting SET for = for + 1 WHERE state = '1'")
        
    elif arg[0] == "against" and state=="1":
        await access_database("UPDATE voting SET against = against + 1 WHERE state = '1'")
        
    elif arg[0] == "result" and state=="1": #show results
        response = "For: " + str(forvote) + ", Against: " + str(againstvote)
        
    else:
        response = "Command not available."
    await ctx.send(response)
    
    
@bot.command(name='blacklist', help='Lists untrustworthy merchants.')
async def blacklist_command(ctx):
    #blacklist = load_list("SELECT * FROM blacklist")
    conn = await db_connect()
    harbor = await conn.cursor()
    await harbor.execute("SELECT name FROM blacklist")
    blacklist = []
    for i in await harbor.fetchall():
        blacklist.append(''.join(filter(str.isalpha, i)))
    print(blacklist)
    await harbor.close()
    response = "LIST OF LOW REPUTATION MERCHANTS: " + str(blacklist)[1:-1] 
    await ctx.send(response)

@bot.command(name='blacklist-modify')
@commands.has_role('Governor')
async def blacklist_command(ctx, option, username):
    response = "Blacklist modified."
    if option == "add":
        print("adding...")
        add_item = "INSERT INTO blacklist (name) VALUES (?)"
        await access_database(add_item, username)
        response = username + " " + "added to list of low reputation merchants."
        
    elif option == "remove":
        print("deleting...")
        delete_item = "DELETE FROM blacklist WHERE name='" + username + "'"
        await access_database(delete_item)
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
    create_history = """
        CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL
        );
        """
    create_locations = """
        CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        coordinates INT NOT NULL
        );
        """
    create_voting = """
        CREATE TABLE IF NOT EXISTS voting (
        state TEXT NOT NULL,
        for INT NOT NULL,
        against INT NOT NULL
        );
        """
    conn = await db_connect()
    harbor = await conn.cursor()
    await harbor.execute(create_blacklist)
    await harbor.execute(create_history)
    await harbor.execute(create_locations)
    await harbor.execute(create_voting)
    await conn.commit()
    await harbor.close()
        
bot.run(TOKEN)
