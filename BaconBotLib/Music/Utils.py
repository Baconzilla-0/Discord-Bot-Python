import discord
import spotdl
import os

from . import Commands
from . import Types


async def IsURL(Str: str):
    return Str.startswith("http://") or Str.startswith("https://")

async def GenerateAudioSources(SongData: Types.Song):
    Source = discord.FFmpegPCMAudio(SongData.File, executable="./ffmpeg/bin/ffmpeg.exe")
    Tracked = Types.AudioSourceTracked(Source)

    SongData.Source = Tracked

    return SongData

async def PredictFilename(Song: Types.Song):
    if len(Song.Meta.artists) > 1: # If more than one artist
        Artists = str(Song.Meta.artists).rstrip("]").lstrip("[").replace("'", "")
        Name = f"{Artists} - {Song.Meta.name}"
    else: # If single artist
        Name = f"{Song.Meta.artist} - {Song.Meta.name}".replace(":", "-").replace("/", "")
    
    return Name

async def MakeSongDescription(Song: Types.Song, Detail):
    """Detail can be 1, 2 or 3. 3 being the most detail."""
    Data = Song.Meta
    if Detail == 1:
        Description = f"{Data.name} by {Data.artist}"
    elif Detail == 2:
        Description = f"{Data.name} by {Data.artist} on album {Data.album_name}"
    elif Detail == 3:
        Description = f"{Data.name} by {Data.artist} on album {Data.album_name} by {Data.album_artist}"

    return Description
    
async def JoinVoice(Player, Response: Types.CommandResponse):
    if not Player.Voice:
        if Response.Context.guild.voice_client:
            Player.Voice = Response.Context.guild.voice_client
        elif Response.Context.author.voice:
            await Response.Context.author.voice.channel.connect()
            Player.Voice = Player.Server.voice_client
        else:
            await Response.Respond("You have to be in a vc to hear music, sorry deaf people.")
            return None

def Bar(Max, Value, Length):
    PartBar = ""
    Percent = Value / Max
    Scaled = int(Percent * Length)
    Remain = Length - Scaled

    PartBar = PartBar.rjust(Scaled,"█")
    for i in range(Remain):
        PartBar = PartBar + "▒"
    
    return f"{PartBar}"