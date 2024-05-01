import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

from songqueue import *
from ytsearch import get_video
from info import get_info

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents = intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'{bot.user} is online and running.')

@bot.command()
async def join(ctx):
    '''
    Allows the bot to join the voice channel that the user is currently in. If the user is 
    not in a voice channel when the command is ran, the bot will not do anything.
    '''
    if ctx.author.voice:
        try:
            channel = ctx.message.author.voice.channel
            await channel.connect()
            await ctx.send(f'Joined `{channel.name}`, type **!help** for options.')

        except Exception:
            await ctx.send("Something went wrong...could not connect to the voice channel.")

@bot.command()
async def leave(ctx):
    '''
    Allows the bot to leave the voice channel that it is currently in. If the bot is not 
    in a voice channel when the command is ran, the bot will not do anything.
    '''
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx):
    '''
    Allows users to play a song if it is found on YouTube. When the command is ran 
    additional times, the songs are added to a queue to be played after the current 
    song.
    '''
    voice = ctx.voice_client
    if voice:
        try: 
            search = ctx.message.content.split('!play ', 1)[1]

        except Exception:
            await ctx.send('You must enter a search query along with the !play command.')
            return

        try:
            await ctx.send(f'Searching for `\"{search}\"`...', )
            url, title = get_video(search)
            ffmpeg_options = {'before_options': '-reconnect 1', 'options': '-vn'}
            source = discord.FFmpegOpusAudio(url, **ffmpeg_options)
            
            guild_id = ctx.message.guild.id

            if guild_id not in queues:
                queues[guild_id] = []
                titles[guild_id] = []
                current_songs[guild_id] = ''

            if voice.is_playing() or voice.is_paused():
                queues[guild_id].append(source)
                titles[guild_id].append(title)
                await ctx.send(f'Added `{title}` to queue.')
            else:
                await ctx.send(f'**Now playing** :notes: `{title}`')
                current_songs[guild_id] = title
                voice.play(source, after = lambda x: play_next(ctx, guild_id))

        except Exception as e:
            print(e)
        
@bot.command()
async def playnow(ctx):
    '''
    Allows the user to skip the current song and immediately play another song without 
    affecting the queue. If no song is currently playing, play the song requested by this 
    command.
    '''
    voice = ctx.voice_client
    if voice:
        try: 
            search = ctx.message.content.split('!playnow ', 1)[1]

        except Exception:

            await ctx.send('You must enter a search query along with the !playnow command.')
            return
        
        try:
            await ctx.send(f'Searching for `\"{search}\"`...', )
            url, title = get_video(search)
            ffmpeg_options = {'before_options': '-reconnect 1', 'options': '-vn'}
            source = discord.FFmpegOpusAudio(url, **ffmpeg_options)
            
            guild_id = ctx.message.guild.id

            if guild_id not in queues:
                queues[guild_id] = []
                titles[guild_id] = []

            if voice.is_playing() or voice.is_paused():
                queues[guild_id].insert(0, source)
                titles[guild_id].insert(0, title)

                await skip(ctx)
                await ctx.send(f'**Now playing** :notes: `{current_songs[guild_id]}`')
            else:
                await ctx.send(f'**Now playing** :notes: `{title}`')
                current_songs[guild_id] = title
                voice.play(source, after = lambda x: play_next(ctx, guild_id))

        except Exception as e:
            print(e) 

@bot.command()
async def pause(ctx):
    '''
    Allows users to pause the current song. If no audio is currently playing, return a 
    message to the text channel indicating so.
    '''
    voice = ctx.voice_client
    if voice:
        if (voice.is_playing()):
            voice.pause()
        else:
            await ctx.send('No audio is currently playing in the voice channel.')

@bot.command()
async def resume(ctx):
    '''
    Allows users to resume the current song. If audio is already playing, return a 
    message to the text channel indicating so.
    '''
    voice = ctx.voice_client
    if voice:
        if (voice.is_paused()):
            voice.resume()
        elif (voice.is_playing()):
            await ctx.send('Audio is already playing in the voice channel.')
        else:
            pass

@bot.command()
async def skip(ctx):
    '''
    Allows users to skip the current song that is playing. If there are no more songs in 
    the queue, the bot will stop playing audio.
    '''
    voice = ctx.voice_client
    if voice:
        await ctx.send('Skipping current song...')
        guild_id = ctx.message.guild.id   
        if len(queues[guild_id]) >= 1:
            voice.pause()
            source = queues[guild_id].pop(0)
            title = titles[guild_id].pop(0)
            current_songs[guild_id] = title
            voice.play(source, after = lambda x: play_next(ctx, guild_id))
        else:
            voice.stop()

@bot.command()
async def skipto(ctx):
    '''
    Allows users to skip all songs including the current song to another song in queue 
    based on its position.
    '''
    guild_id = ctx.message.guild.id
    if guild_id in queues and guild_id in titles:
        if len(queues[guild_id]) >= 1:
            try:
                index = int(ctx.message.content.split('!skipto ', 1)[1]) - 1
                if 0 <= index <= len(queues[guild_id]) - 1:
                    queues[guild_id] = queues[guild_id][index:]
                    titles[guild_id] = titles[guild_id][index:]
                    await skip(ctx)
                    await ctx.send(f'**Now playing** :notes: `{current_songs[guild_id]}`')

                else:
                    msg = f'Currently, the queue has {len(queues[guild_id])} songs. Please specify an index within this range.'
                    await ctx.send(msg)

            except Exception:
                await ctx.send('You must specify an index to skip to.')
        else:
            await ctx.send('No songs are currently in queue.')

@bot.command()
async def song(ctx):
    '''
    Allows users to display the song that is currently playing.
    '''
    voice = ctx.voice_client
    guild_id = ctx.message.guild.id
    if voice:
        if voice.is_playing() or voice.is_paused():
            await ctx.send(f'**Now playing** :notes: `{current_songs[guild_id]}`')

@bot.command()
async def queue(ctx):
    '''
    Allows users to display the top 10 songs currently in queue.
    '''
    guild_id = ctx.message.guild.id
    if guild_id in titles:
        msg = ''
        limit = 10
        if len(titles[guild_id]) >= 1:
            for i, song in enumerate(titles[guild_id]):
                msg += f'**{i+1}:** `{song}`\n'
                if i == limit - 1:
                    break

            title = 'Top 10 songs currently in queue :musical_note:'
            embed = discord.Embed(colour = discord.Colour.dark_teal(), description = msg, title = title)
            await ctx.send(embed = embed)
        else:
            await ctx.send('No songs are currently in queue.')

@bot.command()
async def remove(ctx):
    '''
    Allows users to remove a song from the queue based on its position.
    '''
    guild_id = ctx.message.guild.id
    if guild_id in queues and guild_id in titles:
        if len(queues[guild_id]) >= 1:
            try: 
                index = int(ctx.message.content.split('!remove ', 1)[1]) - 1
                if 0 <= index <= len(queues[guild_id]) - 1:
                    queues[guild_id].pop(index)
                    removed = titles[guild_id].pop(index)

                    await ctx.send(f'Removed `{removed}` from queue.')

                else:
                    msg = f'Currently, the queue has {len(queues[guild_id])} songs. Please specify an index within this range.'
                    await ctx.send(msg)

            except Exception:
                await ctx.send('You must specify an index to remove from.')
        else:
            await ctx.send('No songs are currently in queue.')

@bot.command()
async def clear(ctx):
    '''
    Allows users to clear the current queue.
    '''
    guild_id = ctx.message.guild.id
    if guild_id in queues and guild_id in titles:
        queues[guild_id].clear()
        titles[guild_id].clear()
        await ctx.send('Queue has been cleared.')

@bot.command()
async def help(ctx):
    '''
    Displays information on all the current commands for the user to use.
    '''
    voice = ctx.voice_client
    if (voice):
        title = 'Help Menu'
        msg = get_info()

        embed = discord.Embed(colour=discord.Colour.dark_teal(), description = msg, title = title)
        await ctx.send(embed = embed)

load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))