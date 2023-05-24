import discord
from discord.ext import commands
from music_cog import music_cog
from help_cog import help_cog

def run_bot():
    TOKEN = '<your discord token here>'
    intents = discord.Intents.default()
    
    intents.message_content = True
    intents.voice_states = True
    prefix = 'uta?'
    client = commands.Bot(intents=intents, command_prefix=prefix, help_command=None)
    
 

    @client.event
    async def on_ready():
        await client.add_cog(help_cog(client))
        await client.add_cog(music_cog(client))
        print(f'{client.user} is now running!')
    
    
    client.run(TOKEN)