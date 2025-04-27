import os
import httpx
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random

load_dotenv()

TENOR_API_KEY = os.getenv('TENOR_API_KEY')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents) 

class Gif(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # GIF command implementation
    @bot.command(name='gif')
    async def send_gif(self, ctx, *, search_term=None):
        """Send a GIF related to the given search term"""
        if not search_term:
            await ctx.send("Please provide a search term for the GIF!")
            return
            
        # Default to a random GIF if no term is provided
        if not search_term:
            search_term = "random"
        
        try:
            # Use Tenor API to get GIFs
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://tenor.googleapis.com/v2/search",
                    params={
                        "q": search_term,
                        "key": TENOR_API_KEY,
                        "limit": 10,
                        "contentfilter": "medium"  # Filter out explicit content
                    }
                )
                
                if response.status_code != 200:
                    await ctx.send(f"Error fetching GIF (Status code: {response.status_code})")
                    return
                    
                data = response.json()
                
                if not data.get("results"):
                    await ctx.send(f"No GIFs found for '{search_term}'")
                    return
                    
                # Get a random GIF from the results
                gif_choice = random.choice(data["results"])
                gif_url = gif_choice["media_formats"]["gif"]["url"]
                
                # Create an embed with the GIF
                embed = discord.Embed(color=discord.Color.purple())
                embed.set_image(url=gif_url)
                
                await ctx.send(embed=embed)
        
        except Exception as e:
            await ctx.send(f"Error fetching GIF: {str(e)}")
            print(f"GIF error: {e}")

# function to allow send_gif command to be accessed by main.py

async def setup(bot):
    await bot.add_cog(Gif(bot))