import discord
import spotdl
import os

from . import Commands
from . import Globals


class AudioSourceTracked(discord.AudioSource):
    def __init__(self, source):
        self._source = source
        self.Playing = True
        self.Time = 0

    def read(self) -> bytes:
        data = self._source.read()
        if data:
            self.Time += 20
        else:
            self.Playing = False
        return data
    
class Song:
    def __init__(self, Url):

        self.Meta = spotdl.Song.from_url(Url) # get song data from spotify
        self.Downloaded = False
        self.File = None
        self.Source: AudioSourceTracked = None

    async def DownloadAsync(self):
        File = None
        Name = None

        if len(self.Meta.artists) > 1: # If more than one artist
            Artists = str(self.Meta.artists).rstrip("]").lstrip("[").replace("'", "")
            Name = f"{Artists} - {self.Meta.name}"
        else: # If single artist
            Name = f"{self.Meta.artist} - {self.Meta.name}".replace(":", "-").replace("/", "")
        

        if not os.path.isfile(f"./Temp/{Name}.mp3"): #if file does not exist
            Downloaded = Globals.SPOTIFY.downloader.search_and_download(self.Meta)
            File = Downloaded[1].name
            os.rename(File, f"./Temp/{File}")
        else: #if file exists
            File = f"{Name}.mp3"

        File = f"./Temp/{File}" #get path to file

        self.Downloaded = True
        self.File = File

    async def FileLoad(self, Path):
        self.Downloaded = True
        self.File = Path

    def Download(self):
        File = None
        Name = None

        if len(self.Meta.artists) > 1: # If more than one artist
            Artists = str(self.Meta.artists).rstrip("]").lstrip("[").replace("'", "")
            Name = f"{Artists} - {self.Meta.name}"
        else: # If single artist
            Name = f"{self.Meta.artist} - {self.Meta.name}".replace(":", "-").replace("/", "")
        

        if not os.path.isfile(f"./Temp/{Name}.mp3"): #if file does not exist
            Downloaded = Globals.SPOTIFY.downloader.search_and_download(self.Meta)
            File = Downloaded[1].name
            os.rename(File, f"./Temp/{File}")
        else: #if file exists
            File = f"{Name}.mp3"

        File = f"./Temp/{File}" #get path to file

        self.Downloaded = True
        self.File = File

class CommandResponse: #allows for slash commands to work without recoding
    def __init__(self, Slash, Context: discord.ApplicationContext | discord.Message = None, ):
        self.Slash = Slash
        self.Context = Context


    async def Respond(self, Message = None, Embed = None, View = None):
        self.Context: discord.ApplicationContext | discord.Message

        if self.Slash:
            print("Slash command reply")
            if Message:
                await self.Context.send(Message)
            elif Embed:
                if View:
                    return await self.Context.respond(embed = Embed, view = View)
                else:
                    return await self.Context.respond(embed = Embed)
            else:
                await self.Context.delete()

        else:
            print("Text Command reply")
            if Message:
                await self.Context.reply(Message)
            elif Embed:
                if View:
                    return await self.Context.channel.send(embed = Embed, view = View)
                else:
                    return await self.Context.channel.send(embed = Embed)
            else:
                await self.Context.delete()

