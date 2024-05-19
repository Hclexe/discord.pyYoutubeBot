import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

# Botu ve intents'leri tanımla
intents = discord.Intents.default()
intents.message_content = True  # Mesaj içeriği okuma izni

bot = commands.Bot(command_prefix='!', intents=intents)

# YTDL ayarları
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.command(name='join', help='Ses kanalına katılır')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("Bir ses kanalında değilsiniz.")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='Ses kanalından ayrılır')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Ses kanalında değilim.")

@bot.command(name='play', help='Bir YouTube URL\'si ile müzik çalar')
async def play(ctx, url):
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

    await ctx.send(f'Şimdi oynatılıyor: {player.title}')

@bot.command(name='pause', help='Çalan müziği duraklatır')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("Şu anda müzik çalmıyor.")

@bot.command(name='resume', help='Duraklatılmış müziği devam ettirir')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("Müzik duraklatılmamış.")

@bot.command(name='stop', help='Çalan müziği durdurur')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    voice_client.stop()

# Botu çalıştır

bot.run('key')




