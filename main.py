# bot.py
import os
import random
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError



load_dotenv()                           #loads the .env file and gets the values below
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()     #initializes the intents used by the bot in any server
intents.members = True                  #something like permissions in discord
intents.message_content = True
intents.presences = True

bot = commands.Bot(command_prefix='!',intents=intents)      #sets the prefix for bot commands, can be set to almost anything


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_member_join(member):                #when a new member joins sends a dm welcoming them
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@bot.event
async def on_ready():
    
    guild = discord.utils.get(bot.guilds, name=GUILD)        #loop through data discord sent about guilds

    print(
        f'{bot.user} has connected to the following Guild:\n'
        f'{guild.name}(id: {guild.id})'
        )
    
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@bot.command(name='99', help='Responds with a random quote from Brooklyn 99')
async def nine_nine(ctx):
    
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

@bot.command(name='create-channel')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


# Bot ready event
@bot.event
async def on_ready():
    
    import cogs.subscriptions as sub
    print(f'{bot.user.name} has connected to Discord!')
    
    # Create scheduler for calendar events
    bot.scheduler = AsyncIOScheduler()
    bot.scheduler.start()
    
    # Start task to check for upcoming subscriptions
    sub.check_subscriptions.start()
    
    # Set bot status
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, 
        name="!devhelp for commands"
    ))

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Try `!help` to see all available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param.name}")
    else:
        await ctx.send(f"An error occurred: {error}")
        print(f"Error: {error}")

# Help command
@bot.command(name='devhelp')
async def custom_help(ctx):
    help_embed = discord.Embed(
        title="Utility Bot Commands",
        description="Here are all the available commands:",
        color=discord.Color.blue()
    )
    
    help_embed.add_field(
        name="GIF Commands",
        value="!gif [search term] - Send a GIF related to your search term",
        inline=False
    )
    
    help_embed.add_field(
        name="Dice Commands",
        value="!roll [dice notation] - Roll dice (e.g., !roll 2d6+3)",
        inline=False
    )
    
    help_embed.add_field(
        name="Time Commands",
        value=("!convert [time] [from_tz] [to_tz] - Convert time between timezones\n"
               "!alltime [time] [from_tz] - Show time in all major timezones"),
        inline=False
    )
    
    help_embed.add_field(
        name="Server Commands",
        value="!stats - Show server statistics",
        inline=False
    )
    
    help_embed.add_field(
        name="Calendar Commands",
        value=("!addevent [name] [date] [time] - Add an event\n"
               "!events - List all upcoming events\n"
               "!delevent [event_id] - Delete an event by ID"),
        inline=False
    )
    
    help_embed.add_field(
        name="Subscription Commands",
        value=("!addsub [name] [amount] [due_date] - Add a subscription\n"
               "!subs - List all active subscriptions\n"
               "!delsub [sub_id] - Delete a subscription by ID\n"
               "!renewsub [sub_id] - Mark subscription as paid and update due date"),
        inline=False
    )
    
    await ctx.send(embed=help_embed)

async def load_extenstions():           #loads all cogs
    await bot.load_extension('cogs.subscriptions')
    await bot.load_extension('cogs.calendar_func')
    await bot.load_extension('cogs.gif')
    await bot.load_extension('cogs.roll_dice')
    await bot.load_extension('cogs.convert_time')
    await bot.load_extension('cogs.stats')

async def main():                   # runs extensions and the bot when called with asyncio.run
    async with bot:                 # this helps awaiting coroutines that are created with load_extensions()
        await load_extenstions()
        await bot.start(TOKEN)

asyncio.run(main())
