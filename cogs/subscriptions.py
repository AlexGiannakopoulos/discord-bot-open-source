# Subscription tracker implementation
import datetime
import uuid
from discord.ext import commands, tasks
import discord
from . import data

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents)


class SubscriptionTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Task to check for upcoming subscription payments
    @tasks.loop(hours=24)
    async def check_subscriptions():
        """Check for subscriptions due within the next 3 days and send reminders"""
        try:
            subscriptions = data.Data.load_data("subscriptions")
            if not subscriptions:
                print("No subscriptions found.")
                return
                
            now = datetime.datetime.now()
            three_days_later = now + datetime.timedelta(days=3)
            
            # Find subscriptions due in the next 3 days
            for sub_id, sub in subscriptions.items():
                # Parse the due date
                due_date = datetime.datetime.fromisoformat(sub["next_due_date"])
                
                # Check if it's due within the next 3 days and hasn't been reminded
                if now <= due_date <= three_days_later and not sub.get("reminded", False):
                    # Mark as reminded
                    sub["reminded"] = True
                    data.Data.save_data(subscriptions, "subscriptions")
                    
                    # Send reminder
                    channel_id = sub["channel_id"]
                    channel = bot.get_channel(channel_id)
                    
                    if channel:
                        days_until_due = (due_date - now).days
                        
                        embed = discord.Embed(
                            title="💰 Subscription Payment Due Soon",
                            description=f"Your subscription to **{sub['name']}** is due in {days_until_due} days!",
                            color=discord.Color.orange()
                        )
                        
                        embed.add_field(name="Amount", value=f"${sub['amount']:.2f}", inline=True)
                        embed.add_field(name="Due Date", value=due_date.strftime("%B %d, %Y"), inline=True)
                        
                        user = await bot.fetch_user(sub["creator_id"])
                        if user:
                            await channel.send(content=f"{user.mention}", embed=embed)
                        else:
                            await channel.send(embed=embed)
        
        except Exception as e:
            print(f"Check subscriptions error: {e}")

    @check_subscriptions.before_loop
    async def before_check_subscriptions():
        """Wait until the bot is ready before starting the subscription check loop"""
        await bot.wait_until_ready()

    @bot.command(name='addsub')
    async def add_subscription(self, ctx, name=None, amount=None, due_date_str=None, *, notes=""):
        """Add a subscription to track"""
        if not all([name, amount, due_date_str]):
            await ctx.send("Please provide all required information: `!addsub [name] [amount] [due_date: YYYY-MM-DD] [optional notes]`")
            return
        
        try:
            # Parse the amount
            try:
                amount_float = float(amount.replace('$', ''))
            except ValueError:
                await ctx.send("Please provide a valid amount (e.g., 9.99)")
                return
            
            # Parse the due date
            try:
                due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                await ctx.send("Please use the date format YYYY-MM-DD (e.g., 2025-05-15)")
                return
                
            # Generate subscription ID
            sub_id = str(uuid.uuid4())[:8]
            
            # Create subscription entry
            subscription = {
                "id": sub_id,
                "name": name,
                "amount": amount_float,
                "next_due_date": due_date.isoformat(),
                "notes": notes,
                "creator_id": ctx.author.id,
                "creator_name": ctx.author.name,
                "channel_id": ctx.channel.id,
                "reminded": False
            }
            
            # Load existing subscriptions
            subscriptions = data.Data.load_data("subscriptions")
            if not subscriptions:
                subscriptions = {}
                
            # Add new subscription
            subscriptions[sub_id] = subscription
            
            # Save updated subscriptions
            data.Data.save_data(subscriptions, "subscriptions")
            
            # Create confirmation embed
            embed = discord.Embed(
                title="Subscription Added",
                description=f"**{name}** subscription has been added to your tracker.",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Amount", value=f"${amount_float:.2f}", inline=True)
            embed.add_field(name="Next Payment", value=due_date.strftime("%B %d, %Y"), inline=True)
            
            if notes:
                embed.add_field(name="Notes", value=notes, inline=False)
                
            embed.add_field(name="Subscription ID", value=sub_id, inline=True)
            embed.set_footer(text=f"Added by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error adding subscription: {str(e)}")
            print(f"Add subscription error: {e}")

    @bot.command(name='subs')
    async def list_subscriptions(self, ctx):
        """List all active subscriptions"""
        try:
            subscriptions = data.Data.load_data("subscriptions")
            
            if not subscriptions:
                await ctx.send("No subscriptions are currently being tracked!")
                return
                
            # Filter subscriptions for this user
            user_subs = {sub_id: sub for sub_id, sub in subscriptions.items() 
                        if sub["creator_id"] == ctx.author.id}
            
            if not user_subs:
                await ctx.send("You don't have any subscriptions being tracked!")
                return
                
            # Get total monthly cost
            total_monthly_cost = sum(sub["amount"] for sub in user_subs.values())
            
            # Sort subscriptions by due date
            sorted_subs = []
            for sub_id, sub in user_subs.items():
                due_date = datetime.datetime.fromisoformat(sub["next_due_date"])
                sorted_subs.append((due_date, sub))
                
            sorted_subs.sort(key=lambda x: x[0])
            
            # Create an embed to display subscriptions
            embed = discord.Embed(
                title="📊 Your Subscription Tracker",
                description=f"Total monthly cost: **${total_monthly_cost:.2f}**",
                color=discord.Color.blue()
            )
            
            for due_date, sub in sorted_subs:
                # Format the due date
                formatted_date = due_date.strftime("%B %d, %Y")
                
                # Calculate days until due
                days_until_due = (due_date - datetime.datetime.now()).days
                if days_until_due < 0:
                    due_status = "❗ **OVERDUE**"
                elif days_until_due == 0:
                    due_status = "⚠️ **DUE TODAY**"
                else:
                    due_status = f"Due in {days_until_due} days"
                    
                # Format the subscription info
                value = f"💵 Amount: **${sub['amount']:.2f}**\n📅 Due: {formatted_date} ({due_status})"
                    
                if sub["notes"]:
                    value += f"\n📝 Notes: {sub['notes']}"
                    
                embed.add_field(
                    name=f"{sub['name']} (ID: {sub['id']})",
                    value=value,
                    inline=False
                )
                
            embed.set_footer(text="Use !delsub [ID] to remove a subscription")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error listing subscriptions: {str(e)}")
            print(f"List subscriptions error: {e}")

    @bot.command(name='delsub')
    async def delete_subscription(self, ctx, sub_id=None):
        """Delete a subscription by its ID"""
        if not sub_id:
            await ctx.send("Please provide a subscription ID to delete: `!delsub [subscription_id]`")
            return
            
        try:
            subscriptions = data.Data.load_data("subscriptions")
            
            if not subscriptions or sub_id not in subscriptions:
                await ctx.send(f"No subscription found with ID: {sub_id}")
                return
                
            sub = subscriptions[sub_id]
            
            # Check if user is the creator
            if ctx.author.id != sub["creator_id"] and not ctx.author.guild_permissions.administrator:
                await ctx.send("You can only delete subscriptions you created!")
                return
                
            # Remove the subscription
            sub_name = sub["name"]
            del subscriptions[sub_id]
            data.Data.save_data(subscriptions, "subscriptions")
            
            await ctx.send(f"Subscription **{sub_name}** has been deleted from your tracker!")
            
        except Exception as e:
            await ctx.send(f"Error deleting subscription: {str(e)}")
            print(f"Delete subscription error: {e}")

    @bot.command(name='renewsub')
    async def renew_subscription(self, ctx, sub_id=None):
        """Mark a subscription as paid and update the next due date"""
        if not sub_id:
            await ctx.send("Please provide a subscription ID to renew: `!renewsub [subscription_id]`")
            return
            
        try:
            subscriptions = data.Data.load_data("subscriptions")
            
            if not subscriptions or sub_id not in subscriptions:
                await ctx.send(f"No subscription found with ID: {sub_id}")
                return
                
            sub = subscriptions[sub_id]
            
            # Check if user owns this subscription
            if ctx.author.id != sub["creator_id"] and not ctx.author.guild_permissions.administrator:
                await ctx.send("You can only renew subscriptions you created!")
                return
                
            # Get the current due date
            current_due_date = datetime.datetime.fromisoformat(sub["next_due_date"])
            
            # Calculate the next due date (1 month later)
            if current_due_date.month == 12:
                next_due_date = current_due_date.replace(year=current_due_date.year + 1, month=1)
            else:
                # Try to use the same day of month
                try:
                    next_due_date = current_due_date.replace(month=current_due_date.month + 1)
                except ValueError:
                    # Handle cases like Jan 31 -> Feb 28
                    if current_due_date.month == 1 and current_due_date.day > 28:
                        # February special case
                        next_due_date = current_due_date.replace(month=2, day=28)
                    else:
                        # Use the last day of the next month
                        next_month = current_due_date.month + 1
                        last_day = 30 if next_month in [4, 6, 9, 11] else 31
                        next_due_date = current_due_date.replace(month=next_month, day=last_day)
            
            # Update the subscription
            sub["next_due_date"] = next_due_date.isoformat()
            sub["reminded"] = False
            data.Data.save_data(subscriptions, "subscriptions")
            
            # Create confirmation embed
            embed = discord.Embed(
                title="Subscription Renewed",
                description=f"Your **{sub['name']}** subscription has been marked as paid.",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Amount Paid", value=f"${sub['amount']:.2f}", inline=True)
            embed.add_field(name="Next Payment Due", value=next_due_date.strftime("%B %d, %Y"), inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error renewing subscription: {str(e)}")
            print(f"Renew subscription error: {e}")

async def setup(bot):
    await bot.add_cog(SubscriptionTracker(bot))