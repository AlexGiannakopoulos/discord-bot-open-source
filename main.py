# bot.py
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()                           #loads the .env file and gets the values below
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()     #initializes the intents used by the bot in any server
intents.members = True                  #something like permissions in discord
intents.message_content = True
client = discord.Client(intents=intents)

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

@bot.command(name='roll_dice', help='Simulates rolling dice and posts the result. type the command followed by the number of dice and the number of sides ex: !roll_dice 2 6')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

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


bot.run(TOKEN)
