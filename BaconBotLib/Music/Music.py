import discord
import spotdl
import os
import asyncio
import threading

import spotdl.providers
import spotdl.providers.audio
import spotdl.utils
import spotdl.utils.search

from . import Commands
from . import Globals
from . import States
from . import Types
from . import Utils

from ..Bot import Bot as Client

def Debug(txt):
    Enabled = False

    if Enabled:
        print(txt)

class Music:
    def __init__(self, Bot: Client):
        self.Bot = Bot
        self.SpotifyClient = Globals.SPOTIFY

        asyncio.run(Commands.CreateCommands(self, Bot))
        
    class Player:
        def __init__(self, Parent, Response: Types.CommandResponse):
            self.Server = Response.Context.guild
            self.Channel = Response.Context.channel
            self.Voice: discord.VoiceClient = None

            self.Queue = []
            self.Song: Types.Song = None

            self.Repeat = False
            self.State = States.IDLE
            self.Parent: Music = Parent
            self.Paused = False

        async def SetState(self, State: States.State):
            self.State = State

        async def GetState(self):
            return self.State

        async def QueueSong(self, SongData):
            self.Queue.append(SongData)

        async def SetSong(self, SongData):
            self.Song = SongData

        async def SongEnded(self):
            self.Voice.stop()

            if self.Repeat: # track loop
                await self.SetState(States.IDLE)
                await self.LoadSong(self.Song.Meta.url)
                await self.StartPlayer()
            else:
                if len(self.Queue) > 0:
                    NewSong: Types.Song = self.Queue.pop(0)
                    await self.SetState(States.IDLE)
                    await self.SetSong(None) 
                    Song, State = await self.LoadSong(NewSong.Meta.url)
                    await self.SetSong(Song)

                    print(Song)
                    # setup next song
                    #await self.SetSong(NewSong) 
                    await self.StartPlayer()
                else:
                    await self.SetState(States.IDLE)
                    await self.Voice.disconnect(force=True)
                    self.Song = None
                    self.Voice = None

        async def StartPlayer(self):
            await self.SetState(States.PLAYING)
            self.Voice.play(self.Song.Source)

            async def WaitUntilComplete():
                try:
                    while self.Song.Source.Playing:
                        await asyncio.sleep(1)
                except:
                    pass
                
                
                await self.SongEnded()

            await WaitUntilComplete()
  
        async def LoadSong(self, Url, File = False):
            State = await self.GetState()

            if os.path.exists(Url) or await Utils.IsURL(Url):
                if File == False:
                    SongData = Types.Song(Url)
                    await SongData.DownloadAsync()
                else:
                    SongData = Types.Song("https://open.spotify.com/track/1mXuMM6zjPgjL4asbBsgnt?si=e4983c43a5474e19")
                    await SongData.FileLoad(Url)

                

                if State == States.IDLE:
                    if self.Server.voice_client:
                        self.Voice = self.Server.voice_client
                    else:
                        return None, None
                    
                    self.Song = SongData
                    self.Song = await Utils.GenerateAudioSources(self.Song)
                    Debug("Song Loaded")

                    return self.Song, States.PLAYING
                elif State == States.PLAYING or States.PAUSED:
                    await self.QueueSong(SongData)
                    return SongData, States.QUEUED

        async def NowPlaying(self, Response: Types.CommandResponse):
            Channel = self.Channel

            async def GenerateEmbed():
                Song: spotdl.Song = self.Song.Meta
                Source: Types.AudioSourceTracked = self.Song.Source
                
                Time = ((Song.duration * 1000) - Source.Time) / 1000
                
                Embed = discord.Embed(title=f"Now Playing", color=discord.Colour.blue())
                Embed.add_field(name= "Song", value= Song.name, inline= True)
                Embed.add_field(name= "Artist", value= Song.artist, inline= True)
                Embed.add_field(name= "Album", value= Song.album_name, inline= True)

                Bar = Utils.Bar(Song.duration, Time, 25)
                Embed.add_field(name= f"Time Remaining ({int(Time)}/{int(Song.duration)})", value=Bar)

                return Embed
            
            class NowPlayingView(discord.ui.View):
                BotMessage = None

                async def UpdateMessage(BotMessage: Types.CommandResponse):
                    Embed = await GenerateEmbed()
                    await BotMessage.edit(embed=Embed, view=NowPlayingView())

                @discord.ui.button(style=discord.ButtonStyle.primary, emoji="🔎")
                async def Search_Callback(ButtonSelf, Button: discord.Button, Interaction: discord.Interaction):
                    async def Input_Callback(Query: discord.Message):
                        await self.Search(Response, Query.content)

                    Input = self.Parent.Bot.Input(self.Parent.Bot, Channel, Interaction.user, "What do you want to search for?", Input_Callback)
                    await Interaction.response.defer()
                    await Input.Display()

                    await NowPlayingView.BotMessage.delete()

                @discord.ui.button(style=discord.ButtonStyle.primary, emoji="⏯️")
                async def PlayPause_Callback(ButtonSelf, Button: discord.Button, Interaction: discord.Interaction):
                    await Interaction.response.defer()
                    await self.Pause()

                    await NowPlayingView.UpdateMessage(NowPlayingView.BotMessage)

                @discord.ui.button(style=discord.ButtonStyle.primary, emoji="⏩")
                async def Skip_Callback(ButtonSelf, Button: discord.Button, Interaction: discord.Interaction):
                    await Interaction.response.defer()
                    await self.Skip()

                    await NowPlayingView.UpdateMessage(NowPlayingView.BotMessage)
                
                @discord.ui.button(style=discord.ButtonStyle.primary, emoji="🔃")
                async def Refresh_Callback(ButtonSelf, Button: discord.Button, Interaction: discord.Interaction):
                    await Interaction.response.defer()

                    await NowPlayingView.UpdateMessage(NowPlayingView.BotMessage)

                

            Embed = await GenerateEmbed()
            SentMessage = await Response.Respond(Embed=Embed, View=NowPlayingView())
            SentMessage: discord.Message
            NowPlayingView.BotMessage = SentMessage

        async def Search(self, Response: Types.CommandResponse, Query):
            Results = spotdl.utils.search.get_search_results(Query)
            print(Results)
            
            Options = []
            for Result in Results:
                Result: spotdl.Song
                Description = f"By {Result.artist}, Album: {Result.album_name}"
                Option = discord.SelectOption(label=(Result.name[:90]) if len(Result.name) > 90 else Result.name, description=(Description[:90]) if len(Description) > 90 else Description, value=Result.url)
                Options.append(Option)

            Embed = discord.Embed(title= f"Search Results for {Query}")

            class SearchView(discord.ui.View):
                Selected = None
                @discord.ui.select( 
                    placeholder = "Choose a Song", # the placeholder text that will be displayed if nothing is selected
                    min_values = 1, # the minimum number of values that must be selected by the users
                    max_values = 1, # the maximum number of values that can be selected by the users
                    options = Options
                )
                async def SelectSong_Callback(self, Select, Interaction: discord.Interaction): # the function called when the user is done selecting options
                    if Interaction.user.id == Response.Context.author.id:
                        await Interaction.response.send_message(f"Selected Song: {Select.values[0]}, Press play to start.")
                        SearchView.Selected = Select.values[0]

                @discord.ui.button(label="Play", style=discord.ButtonStyle.green, emoji="▶️")
                async def Search_Callback(ButtonSelf, Button: discord.Button, Interaction: discord.Interaction):
                    if Interaction.user.id == Response.Context.author.id:
                        if SearchView.Selected:
                            print(SearchView.Selected)
                            await Interaction.response.defer()
                            Song = Types.Song(SearchView.Selected)
                            await self.Play(SearchView.Selected, Response)
                        else:
                            await Response.Respond("Select a song first!", Private=True)

            await Response.Respond(Embed=Embed, View=SearchView())

        async def GetQueue(self, Response: Types.CommandResponse):
            QueueEmbed = discord.Embed(title="Queue")

            Number = 0
            for Song in self.Queue:
                Song: Types.Song
                Number += 1
                QueueEmbed.add_field(name=f"{Number}. {Song.Meta.name}", value=Song.Meta.artist, inline=False)
            
            await Response.Respond(Embed=QueueEmbed)

        async def Play(self, Query, Response: Types.CommandResponse):
            Url = None

            if await Utils.IsURL(Query):
                Url = Query

                await Utils.JoinVoice(self, Response)

                
                SongData, Status = await self.LoadSong(Url)

                if Status == States.QUEUED:
                    Info = await Utils.MakeSongDescription(SongData, 2)
                    await self.Parent.Bot.Embed(f"Added `{Info}` to the Queue, there are {len(self.Queue)} song(s) infront of it.", discord.Colour.blue(), Response.Context.channel)
                else:
                    await self.NowPlaying(Response)
                    await self.StartPlayer()
            else:
                await self.Search(Response, Query)
        
        async def PlayFile(self, Url: str, Response: Types.CommandResponse):

            if os.path.exists(Url):
                await Utils.JoinVoice(self, Response)

                
                SongData, Status = await self.LoadSong(Url, True)

                if Status == States.QUEUED:
                    Info = await Utils.MakeSongDescription(SongData, 2)
                    await self.Parent.Bot.Embed(f"Added `{Info}` to the Queue, there are {len(self.Queue)} song(s) infront of it.", discord.Colour.blue(), Response.Context.channel)
                else:
                    await self.NowPlaying(Response)
                    await self.StartPlayer()
            else:
                await Response.Respond("Invalid file link :[")
            
        async def Playlist(self, Response: Types.CommandResponse, Url):
            Playlist = spotdl.utils.search.get_simple_songs([Url])
            
            First = Playlist.pop(0)

            async def LoadOthers():
                PathList = []

                for Song in Playlist:
                    SongData = Types.Song(Song.url)
                    SongData.Downloaded = True
                    FileName = await Utils.PredictFilename(SongData)
                    SongData.File = f"./{FileName}.mp3"

                    await self.QueueSong(SongData)

                def Download(Playlist: list):
                    for Song in Playlist:
                        SongData = Types.Song(Song.url)
                        SongData.Download()

                DownloadThread = threading.Thread(target=Download, args=[Playlist])
                DownloadThread.start()

            await LoadOthers()
            await self.Play(First.url, Response)
    
        async def DebugInfo(self, Channel: discord.TextChannel):
            Embed = discord.Embed(title="Debug Info", color=discord.Color.green())

            Embed.add_field(name="State", value=str(self.State.Value))
            Embed.add_field(name="Song", value=await Utils.MakeSongDescription(self.Song, 3))
            Embed.add_field(name="Voice", value=str(self.Voice.channel))

            await Channel.send(embed=Embed)

        # controls
        async def Stop(self, Response: Types.CommandResponse):
            await Response.Context.guild.voice_client.disconnect()

            await self.SetState(States.IDLE)

            self.Queue = []
            self.Song = None
            self.Voice = None

        async def Skip(self):
            self.Song.Source.Playing = False

        async def Pause(self):
                Client = self.Voice
                Client: discord.VoiceClient

                if Client.is_paused():
                    Client.resume()
                    await self.SetState(States.PLAYING)
                else:
                    Client.pause()
                    await self.SetState(States.PAUSED)

                self.Paused = Client.is_paused()

        async def Loop(self):
            if self.Repeat:
                self.Repeat = False
            else:
                self.Repeat = True