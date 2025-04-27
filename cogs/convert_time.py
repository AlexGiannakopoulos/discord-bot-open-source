# Time converter implementation
import pytz
import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents) 

class TimeConverter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.command(name='convert')
    async def convert_time(self, ctx, time_str=None, from_tz=None, to_tz=None):
        """Convert time from one timezone to another"""
        if not all([time_str, from_tz, to_tz]):
            await ctx.send("Please provide all required parameters: `!convert [time] [from_timezone] [to_timezone]`")
            return
        
        try:
            # Check if timezones are valid
            try:
                source_tz = pytz.timezone(from_tz)
                target_tz = pytz.timezone(to_tz)
            except pytz.exceptions.UnknownTimeZoneError:
                await ctx.send(f"Invalid timezone. Use common timezone names like 'US/Eastern', 'Europe/London', etc.")
                return
            
            # Parse the time string (supporting common formats)
            parsed_time = None
            time_formats = [
                "%H:%M",        # 14:30
                "%I:%M %p",     # 2:30 PM
                "%I:%M%p",      # 2:30PM
                "%H%M",         # 1430
            ]
            
            for fmt in time_formats:
                try:
                    parsed_time_obj = datetime.datetime.strptime(time_str, fmt)
                    parsed_time = parsed_time_obj.time()
                    break
                except ValueError:
                    continue
            
            if not parsed_time:
                await ctx.send("Invalid time format. Please use formats like '14:30' or '2:30 PM'.")
                return
            
            # Get current date in source timezone
            now = datetime.datetime.now(source_tz)
            source_datetime = datetime.datetime.combine(now.date(), parsed_time)
            source_datetime = source_tz.localize(source_datetime)
            
            # Convert to target timezone
            target_datetime = source_datetime.astimezone(target_tz)
            
            # Format the result
            embed = discord.Embed(
                title="Time Conversion",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="From",
                value=f"{source_datetime.strftime('%I:%M %p')} {from_tz}",
                inline=True
            )
            
            embed.add_field(
                name="To",
                value=f"{target_datetime.strftime('%I:%M %p')} {to_tz}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error converting time: {str(e)}")
            print(f"Time conversion error: {e}")

    @bot.command(name='alltime')
    async def show_all_timezones(self, ctx, time_str=None, from_tz=None):
        """Show the provided time in all major timezones"""
        if not all([time_str, from_tz]):
            await ctx.send("Please provide all required parameters: `!alltime [time] [from_timezone]`")
            return
        
        try:
            # Check if source timezone is valid
            try:
                source_tz = pytz.timezone(from_tz)
            except pytz.exceptions.UnknownTimeZoneError:
                await ctx.send(f"Invalid timezone. Use common timezone names like 'US/Eastern', 'Europe/London', etc.")
                return
            
            # Parse the time string (supporting common formats)
            parsed_time = None
            time_formats = [
                "%H:%M",        # 14:30
                "%I:%M %p",     # 2:30 PM
                "%I:%M%p",      # 2:30PM
                "%H%M",         # 1430
            ]
            
            for fmt in time_formats:
                try:
                    parsed_time_obj = datetime.datetime.strptime(time_str, fmt)
                    parsed_time = parsed_time_obj.time()
                    break
                except ValueError:
                    continue
            
            if not parsed_time:
                await ctx.send("Invalid time format. Please use formats like '14:30' or '2:30 PM'.")
                return
            
            # Get current date in source timezone
            now = datetime.datetime.now(source_tz)
            source_datetime = datetime.datetime.combine(now.date(), parsed_time)
            source_datetime = source_tz.localize(source_datetime)
            
            # List of major timezones to display
            major_timezones = [
                "US/Pacific", "US/Mountain", "US/Central", "US/Eastern",
                "Europe/Athens","Europe/London", "Europe/Paris", "Europe/Berlin", 
                "Asia/Dubai", "Asia/Kolkata", "Asia/Singapore", 
                "Asia/Tokyo", "Australia/Sydney", "Pacific/Auckland"
            ]
            
            # Create the embed
            embed = discord.Embed(
                title=f"Time Conversion from {time_str} {from_tz}",
                description="Time in major timezones:",
                color=discord.Color.gold()
            )
            
            # Add source time for reference
            embed.add_field(
                name="Original Time",
                value=f"{source_datetime.strftime('%I:%M %p')} {from_tz}",
                inline=False
            )
            
            # Convert to each major timezone
            for tz_name in major_timezones:
                try:
                    tz = pytz.timezone(tz_name)
                    converted_time = source_datetime.astimezone(tz)
                    
                    # Get a user-friendly timezone name
                    friendly_name = tz_name.replace("_", " ").split("/")[-1]
                    
                    embed.add_field(
                        name=friendly_name,
                        value=f"{converted_time.strftime('%I:%M %p')} ({tz_name})",
                        inline=True
                    )
                except pytz.exceptions.UnknownTimeZoneError:
                    continue
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error showing time in all timezones: {str(e)}")
            print(f"All timezones error: {e}")

async def setup(bot):
    await bot.add_cog(TimeConverter(bot))