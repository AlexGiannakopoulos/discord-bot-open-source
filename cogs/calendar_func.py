# Calendar and event scheduler implementation
import datetime
import uuid
from discord.ext import commands
import discord
from apscheduler.jobstores.base import JobLookupError
from . import data as Data

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents)

class CalendarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Event storage
    events_data = {}

    @bot.command(name='addevent')
    async def add_event(self, ctx, name=None, date_str=None, time_str=None, *, description="No description provided"):
        """Add an event to the calendar with an optional reminder"""
        if not all([name, date_str, time_str]):
            await ctx.send("Please provide all required information: `!addevent [name] [date: YYYY-MM-DD] [time: HH:MM] [optional description]`")
            return
        
        try:
            # Parse date and time
            event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            event_time = datetime.datetime.strptime(time_str, "%H:%M").time()
            
            # Combine into datetime object
            event_datetime = datetime.datetime.combine(event_date, event_time)
            
            # Check if the event is in the past
            if event_datetime < datetime.datetime.now():
                await ctx.send("Cannot schedule events in the past!")
                return
            
            # Generate a unique ID for the event
            event_id = str(uuid.uuid4())[:8]
            
            # Create event dictionary
            event = {
                "id": event_id,
                "name": name,
                "description": description,
                "datetime": event_datetime.isoformat(),
                "creator_id": ctx.author.id,
                "creator_name": ctx.author.name,
                "channel_id": ctx.channel.id
            }
            
            # Load existing events
            events = Data.Data.load_data("events")
            
            # Add the new event
            if not events:
                events = {}
            events[event_id] = event
            
            # Save updated events
            Data.Data.save_data(events, "events")
            
            # Schedule a reminder 15 minutes before
            reminder_time = event_datetime - datetime.timedelta(minutes=15)
            now = datetime.datetime.now()
            
            if reminder_time > now:
                # Schedule the reminder
                bot.scheduler.add_job(
                    CalendarCog.send_event_reminder,
                    'date',
                    run_date=reminder_time,
                    args=[ctx.guild.id, ctx.channel.id, event_id, name],
                    id=f"reminder_{event_id}"
                )
            
            # Create confirmation embed
            embed = discord.Embed(
                title="Event Added",
                description=f"**{name}** has been scheduled!",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Date & Time", value=event_datetime.strftime("%A, %B %d, %Y at %I:%M %p"), inline=False)
            embed.add_field(name="Description", value=description, inline=False)
            embed.add_field(name="Event ID", value=event_id, inline=True)
            embed.set_footer(text=f"Created by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time.")
        except Exception as e:
            await ctx.send(f"Error adding event: {str(e)}")
            print(f"Add event error: {e}")

    async def send_event_reminder(guild_id, channel_id, event_id, event_name):
        """Send a reminder for an upcoming event"""
        try:
            channel = bot.get_channel(channel_id)
            if not channel:
                return
            
            events = Data.Data.load_data("events")
            if event_id not in events:
                return
                
            event = events[event_id]
            event_datetime = datetime.datetime.fromisoformat(event["datetime"])
            
            embed = discord.Embed(
                title="⏰ Event Reminder",
                description=f"The event **{event_name}** is starting in 15 minutes!",
                color=discord.Color.orange()
            )
            
            embed.add_field(name="Time", value=event_datetime.strftime("%I:%M %p"), inline=True)
            embed.add_field(name="Description", value=event["description"], inline=False)
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Event reminder error: {e}")

    @bot.command(name='events')
    async def list_events(self, ctx):
        """List all upcoming events"""
        try:
            events = Data.Data.load_data("events")
            
            if not events:
                await ctx.send("No events are currently scheduled!")
                return
            
            # Sort events by date/time
            sorted_events = []
            for event_id, event in events.items():
                event_datetime = datetime.datetime.fromisoformat(event["datetime"])
                if event_datetime > datetime.datetime.now():
                    sorted_events.append((event_datetime, event))
            
            sorted_events.sort(key=lambda x: x[0])
            
            if not sorted_events:
                await ctx.send("No upcoming events!")
                return
            
            # Create an embed to display events
            embed = discord.Embed(
                title="📅 Upcoming Events",
                color=discord.Color.blue()
            )
            
            for event_time, event in sorted_events:
                # Format the date
                formatted_time = event_time.strftime("%a, %b %d at %I:%M %p")
                
                # Format the event title and include the event ID
                title = f"{event['name']} (ID: {event['id']})"
                
                # Add field for this event
                embed.add_field(
                    name=title,
                    value=f"**When:** {formatted_time}\n**Description:** {event['description']}\n**Created by:** {event['creator_name']}",
                    inline=False
                )
            
            embed.set_footer(text="Use !delevent [ID] to remove an event")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error listing events: {str(e)}")
            print(f"List events error: {e}")

    @bot.command(name='delevent')
    async def delete_event(self, ctx, event_id=None):
        """Delete an event by its ID"""
        if not event_id:
            await ctx.send("Please provide an event ID to delete: `!delevent [event_id]`")
            return
        
        try:
            events = Data.Data.load_data("events")
            
            if not events or event_id not in events:
                await ctx.send(f"No event found with ID: {event_id}")
                return
            
            event = events[event_id]
            
            # Check if user is the creator or has manage server permissions
            is_admin = ctx.author.guild_permissions.manage_guild
            is_creator = ctx.author.id == event["creator_id"]
            
            if not (is_admin or is_creator):
                await ctx.send("You can only delete events you created!")
                return
            
            # Remove the event
            del events[event_id]
            Data.Data.save_data(events, "events")
            
            # Cancel the reminder job if it exists
            try:
                bot.scheduler.remove_job(f"reminder_{event_id}")
            except JobLookupError:
                pass  # Job doesn't exist or already ran
            
            await ctx.send(f"Event **{event['name']}** has been deleted!")
            
        except Exception as e:
            await ctx.send(f"Error deleting event: {str(e)}")
            print(f"Delete event error: {e}")

async def setup(bot):
    await bot.add_cog(CalendarCog(bot))
