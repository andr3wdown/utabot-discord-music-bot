import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = """
        My prefix is - uta?
        Commands:
        help - displays commands
        play <song name> - searches for the song on youtube and adds it to the queue
        fplay <song name> - instantly adds the song to the top of the queue and plays it
        queue - display current queue
        skip - skip the current song
        clear - clear the current queue
        pause - pauses the current song
        resume - resumes the current song
        remove - removes the last song of the queue
        leave - leave the voice channel
        """
        self.text_channel_text = []
        
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_text.append(channel)
                
        await self.send_to_all(self.help_message)
        
    async def send_to_all(self, msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(msg)
    
    @commands.command(name = 'help', aliases=['h'], help='Displays all the commands.')
    async def help(self, ctx):
        embed = discord.Embed(title=f"here's my commands!", description=f"{self.help_message}") 
        await ctx.send(embed = embed)