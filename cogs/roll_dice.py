# Dice roller implementation
import re
import discord
from discord.ext import commands
from dotenv import load_dotenv
import random

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents) 

class DiceRoller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.command(name='roll')
    async def roll_dice(self, ctx, *, dice_notation=None):
        """Roll dice using standard dice notation (e.g., 2d6+3)"""
        if not dice_notation:
            # Default to rolling a single d20 if no notation is provided
            dice_notation = "1d20"
        
        try:
            # Parse the dice notation with regex
            # Format: NdS+M where N=number of dice, S=sides per die, M=modifier
            pattern = r"(\d+)d(\d+)([+-]\d+)?"
            match = re.match(pattern, dice_notation.lower().replace(" ", ""))
            
            if not match:
                await ctx.send("Invalid dice notation! Please use format like '2d6+3'.")
                return
                
            num_dice = int(match.group(1))
            sides = int(match.group(2))
            modifier = match.group(3)
            mod_value = int(modifier) if modifier else 0
            
            # Limit the number of dice to prevent abuse
            if num_dice > 100:
                await ctx.send("Too many dice! Please roll 100 or fewer.")
                return
                
            if sides > 1000:
                await ctx.send("Dice too large! Please use dice with 1000 or fewer sides.")
                return
            
            # Roll the dice
            rolls = [random.randint(1, sides) for _ in range(num_dice)]
            total = sum(rolls) + mod_value
            
            # Create the response message
            if num_dice == 1 and mod_value == 0:
                result_message = f"🎲 You rolled a **{total}**!"
            else:
                # Show individual dice for smaller rolls
                if num_dice <= 10:
                    dice_results = " + ".join([str(r) for r in rolls])
                    if mod_value != 0:
                        mod_sign = "+" if mod_value > 0 else ""
                        result_message = f"🎲 You rolled {dice_notation}: ({dice_results}) {mod_sign}{mod_value} = **{total}**"
                    else:
                        result_message = f"🎲 You rolled {dice_notation}: ({dice_results}) = **{total}**"
                else:
                    # For larger rolls, just show the sum of dice
                    dice_sum = sum(rolls)
                    mod_sign = "+" if mod_value > 0 else ""
                    result_message = f"🎲 You rolled {dice_notation}: {dice_sum} {mod_sign}{mod_value} = **{total}**"
            
            await ctx.send(result_message)
            
        except Exception as e:
            await ctx.send(f"Error rolling dice: {str(e)}")
            print(f"Dice rolling error: {e}")

# function to allow roll_dice command to be accessed by main.py

async def setup(bot):
    await bot.add_cog(DiceRoller(bot))