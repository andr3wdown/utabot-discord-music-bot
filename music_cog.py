import discord
from discord.ext import commands
from yt_dlp import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        
        self.music_queue = []
        
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.current_song = None
        self.vc = None
        
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                if item.startswith('https://www.youtube.com/watch?v='):
                    item = item.replace('https://www.youtube.com/watch?v=', '')
                    item = item[:11]
                  
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
                video_url = f'https://www.youtube.com/watch?v={info["display_id"]}'
                thumbnail_url = f'http://img.youtube.com/vi/{info["display_id"]}/maxresdefault.jpg'    
                
            except Exception:
                print("Couldn't find a song!")
                return False
        return {'source': info['url'], 'title': info['title'], 'video_url' : video_url, 'thumbnail_url' : thumbnail_url}
    
    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.current_song = self.music_queue[0][0]
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            self.music_queue.pop(0) 
        else:
            print('stopped playing!')
            self.is_playing = False
            
    def get_queue(self):
        retval = ""
        for i in range(0, len(self.music_queue)):
            if i > 10: break
            retval += self.music_queue[i][0]['title'] + '\n'
        return retval
    
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.current_song = self.music_queue[0][0]
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
                if self.vc == None:
                    embed = discord.Embed(title=f'Oops there seems to have been a prombel!', description="Couldn't connect to the vc") 
                    await ctx.send(embed = embed)
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])       
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            self.music_queue.pop(0)
    
    @commands.command(name='play', aliases=['p'], help='Play the selected song from youtube!')
    async def play(self, ctx, *args):
        query = ' '.join(args)
        
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            embed = discord.Embed(title=f'Oops there seems to have been a prombel!', description="Please connect to a voice channel!") 
            await ctx.send(embed = embed)
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                embed = discord.Embed(title=f'Oops there seems to have been a prombel!', description="Couldn't download the song. Try a different keyword!") 
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(title=f'Done!', description=f"{song['title']} has been added to the queue! {song['video_url']}") 
                embed.set_image(url=song['thumbnail_url'])
                await ctx.send(embed = embed)
                self.music_queue.append([song, voice_channel])
                
                if self.is_playing == False:
                    await self.play_music(ctx)
                    
    @commands.command(name='fplay', aliases=['f', 'forceplay'], help='Play the selected song immediately from youtube!')
    async def fplay(self, ctx, *args):      
        query = ' '.join(args)
        
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            embed = discord.Embed(title=f'Oops there seems to have been a prombel!', description="Please connect to a voice channel!") 
            await ctx.send(embed = embed)
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                embed = discord.Embed(title=f'Oops there seems to have been a prombel!', description="Couldn't download the song. Try a different keyword!") 
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(title=f'Done!', description=f"{song['title']} will be played now! {song['video_url']}") 
                embed.set_image(url=song['thumbnail_url'])
                await ctx.send(embed = embed)
                self.music_queue.insert(0, [song, voice_channel])
                self.vc.stop()
                await self.play_music(ctx)
    
        
    @commands.command(name='pause', aliases=['stop'], help='Pauses the current song being played!')
    async def pause(self, ctx):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            
    @commands.command(name='resume', aliases=['r'], help='Resumes the current song being played!')
    async def resume(self, ctx):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()
            
    @commands.command(name='skip', aliases=['s'], help='Skips the current song being played!')
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            embed = discord.Embed(title=f"Skipping current song!", description=f" ") 
            await ctx.send(embed = embed)
            await self.play_music(ctx)
            
            
    @commands.command(name='queue', aliases=['q'], help='Skips the current song being played!')
    async def queue(self, ctx):
        retval = self.get_queue()
        embed = discord.Embed(title=f"Here's the current queue!", description=f"The queue is empty! Type uta?play <song title> to add a song.")
        
        if self.current_song == None:
            await ctx.send(embed = embed)
        else:    
            embed = discord.Embed(title=f"Currently playing", description=f"{self.current_song['title']}")
            if retval != "":              
                embed.add_field(name="Here's the current queue!", value=f"{retval}")
            else:
                embed.add_field(name="Here's the current queue!", value=f"The queue is empty! Type uta?play <song title> to add a song.")
            await ctx.send(embed = embed)
               
    @commands.command(name='clear', aliases=['c'], help='Clears the queue!')
    async def clear(self, ctx, *args):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        embed = discord.Embed(title=f"Success!", description=f"The queue has been cleared! Stopping current song...") 
        await ctx.send(embed = embed)
        
    @commands.command(name='remove', aliases=['removelast'], help='Removes the last song from the queue!')
    async def remove(self, ctx):
        if len(self.music_queue) > 0:
            song = self.music_queue.pop()
            embed = discord.Embed(title=f"{song[0]['title']} has been removed from the queue!", description=f" ") 
            retval = self.get_queue()
            if retval != "":
                embed.add_field(name=f"Here's the current queue!", value=f"{retval}") 
                await ctx.send(embed = embed)
            else:
                embed.add_field(name=f"Here's the current queue!", value=f"The queue is empty! Type uta?play <song title> to add a song.") 
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(title=f"No songs in queue!", description=f"The queue is empty so there's nothing to remove!") 
            await ctx.send(embed = embed)
    
    @commands.command(name='leave', aliases=['disconnect', 'l'], help='Kicks the bot from the voice channel!')
    async def leave(self, ctx):
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []
        await self.vc.disconnect()