# Server stats implementation
from discord.ext import commands
import discord
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!',intents=intents)

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bot.command(name='stats')
    async def server_stats(self, ctx):
        """Display server statistics"""
        try:
            guild = ctx.guild
            
            # Calculate the number of online members
            online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
            
            # Get server creation date
            creation_date = guild.created_at
            days_since_creation = (datetime.now().astimezone() - creation_date).days
            
            # Count channels by type
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            categories = len(guild.categories)
            
            # Count roles (excluding @everyone)
            role_count = len(guild.roles) - 1  # -1 to exclude @everyone
            
            # Get server boost status
            boost_level = guild.premium_tier
            boost_count = guild.premium_subscription_count
            
            # Server features
            features_list = ", ".join(guild.features) if guild.features else "None"
            
            # Server verification level
            verification_level = str(guild.verification_level).title()
            
            # Create the embed
            embed = discord.Embed(
                title=f"{guild.name} Server Statistics",
                description=f"Server ID: {guild.id}",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            # Set the server icon if available
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            
            # Add server information fields
            embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
            embed.add_field(name="Created", value=f"{creation_date.strftime('%B %d, %Y')}\n({days_since_creation} days ago)", inline=True)
            embed.add_field(name="Region", value=guild.region if hasattr(guild, 'region') else "N/A", inline=True)
            
            # Member information
            embed.add_field(name="Members", value=f"Total: {guild.member_count}\nOnline: {online_members}", inline=True)
            embed.add_field(name="Channels", value=f"📝 Text: {text_channels}\n🔊 Voice: {voice_channels}\n📁 Categories: {categories}", inline=True)
            embed.add_field(name="Roles", value=role_count, inline=True)
            
            # Server boost information
            embed.add_field(name="Boost Status", value=f"Level: {boost_level}\nBoosts: {boost_count}", inline=True)
            embed.add_field(name="Verification", value=verification_level, inline=True)
            
            # Features (if not too many)
            if len(features_list) < 1024:  # Discord embed field value limit
                embed.add_field(name="Server Features", value=features_list, inline=False)
            
            # Add footer with timestamp
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"Error displaying server stats: {str(e)}")
            print(f"Server stats error: {e}")

async def setup(bot):
    await bot.add_cog(Stats(bot))