from asyncio import AbstractEventLoop
import discord
import types
from .Utils import Utils
from .Types import Types

class Client(discord.Bot):
    def __init__(self, Self, *, loop: AbstractEventLoop | types.NoneType = None, **options: discord.Any):
        super().__init__(loop=loop, **options)
        
        self.Bot = Self
    async def on_ready(self):
        activity = discord.Activity(name="the voices", type=discord.ActivityType.listening)
        await self.change_presence(status=discord.Status.online, activity=activity)
        print(f'Logged on as {self.user}!')

    async def on_message(self, message: discord.Message):
        print(f'Message in {message.guild} from {message.author}: {message.content}')
        if message.author.id != self.Bot.Client.user.id:
            HasCommand = False
            for Cmd in self.Bot.Commands:
                Cmd: Bot.Command
                HasCommand = await Cmd.Run(self.Bot, message)
            for Input in self.Bot.Inputs:
                await Input.Check(message)
        
        #Utils.Log()

    async def on_voice_state_update(self, user: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before != after:
            if after.channel:
                print(f'{user.name} has joined {after.channel.name} in {after.channel.guild.name}')

class Bot:
    Colours = {
        "Help": discord.Colour.green(),
        "Error": discord.Colour.red(),
        "Warn":discord.Colour.yellow(),
        "Feedback": discord.Colour.blue(),
        "Other": discord.Colour.purple()
    }

    def __init__(self):
        self.Commands = []
        self.Inputs = []
        self.Prefix = "-"
        self.Invite = "i dont fakin think so"
        self.Colours = Bot.Colours
        self.CatchErrors = False

        Intents = discord.Intents.default()
        Intents.typing = True
        Intents.messages = True
        Intents.voice_states = True
        Intents.members = True
        Intents.message_content = True
        Intents.message_content = True

        self.Client = Client(self, intents=Intents)


        async def HelpCmd(Response, Args: str):
            HelpList = ""

            for Cmd in self.Commands:
                Cmd: Bot.Command

                HelpList = HelpList + f"{Cmd.Name} | {Cmd.Description}\n"

            HelpEmbed = discord.Embed(title=f"{self.Client.user.name} Help", description=HelpList, color=Bot.Colours["Help"].value)

            await Response.Respond(Embed=HelpEmbed)
        
        self.MultiCommand(self, "Help", "Shows information about various commands.", HelpCmd, False, False, False)

    def Run(self):
        Token = ""
        if Token == "":
            with open("./Token.txt", "r") as TokenFile:
                TokenLines = TokenFile.readlines()
                Token = TokenLines[0]
        
        self.Client.run(Token)

    class Input:
        def __init__(self, Bot, Channel: discord.TextChannel, User, Prompt, Callback):
            self.Channel = Channel
            self.User = User
            self.Prompt = Prompt
            self.Callback = Callback
            self.Active = False
            self.Message = None

            Bot.Inputs.append(self)

        async def Display(self):
            self.Active = True
            self.Message = await self.Channel.send(self.Prompt)

        async def Check(self, Msg: discord.Message):
            if self.Active:
                if Msg.channel.id == self.Channel.id:
                    if Msg.author.id == self.User.id:
                        print(f"Received Input: {Msg.content}")
                        await self.Callback(Msg)
                        await Msg.delete(reason="Input received.")
                        await self.Message.delete(reason="Input received.")
                        self.Active = False

    class Command:
        def __init__(self, Parent, Name, Description, Callback, Args = True, Reply = True, Embedded = True, Server = None):
            self.Name = Name
            self.Description = Description
            self.Callback = Callback
            self.Feedback = ""
            self.Args = Args
            self.Reply = Reply
            self.Embedded = Embedded
            self.Server = Server
            self.Parent = Parent

            self.Parent.Commands.append(self)

        async def Run(self, Bot, Message: discord.Message):
            Errored = False

            if Message.author.id != Bot.Client.user.id:
                Server = False

                if self.Server == None:
                    Server = True
                elif self.Server == Message.guild.id:
                    Server = True

                if Server:
                    if Message.content.split(" ", 1)[0].lower() == (f"{Bot.Prefix}{self.Name}".lower()):
                        RawMessage = Message.content.lstrip(";")
                        if self.Args:
                            try:
                                Args = RawMessage.split(" ", 1)[1]
                            except Exception as E:
                                Args = None
                        else:
                            Args = None
                        
                        if Bot.CatchErrors:
                            try:
                                Colour = "Feedback"
                                self.Feedback = await self.Callback(Types.CommandResponse(False, Message), Args)
                            except Exception as E:
                                Colour = "Error"
                                self.Feedback = f"Could not run command... Exception: `{E}`"
                                Errored = True
                                ##help(E)
                        else:
                            Colour = "Feedback"
                            self.Feedback = await self.Callback(Types.CommandResponse(False, Message), Args)

                        if Args == None and self.Args == True:
                            Colour = "Error"
                            self.Feedback = f"Could not run command... Invalid Args, Use `{Bot.Prefix}help` if you're confused."
                            Errored = True
                        print(f"Command: {self.Name}, Args: {Args}, Raw: {RawMessage}, Feedback: {self.Feedback}")

                        if self.Reply:
                            if self.Feedback:
                                if self.Embedded or Errored:
                                    FeedbackEmbed = discord.Embed(title=self.Feedback, color=Bot.Colours[Colour].value)
                                    await Message.channel.send(embed=FeedbackEmbed)
                                else:
                                    await Message.reply(self.Feedback)
                        return True
                    else:
                        return False
                    
    class SlashCommand(Command):

        def __init__(self, Parent, Name, Description, Callback, Args, Reply, Embedded, Server = None):
            super().__init__(Parent, Name, Description, Callback, Args, Reply, Embedded, Server)

            Parent.Commands.remove(self)

            

            Client: discord.Bot = Parent.Client

            Servers = []
            
            if Server:
                Servers = [Server]
            else:
                for Guild in Client.guilds:
                    Servers.append(Guild.id)
                
            if Server:
                if self.Args:
                    @Client.command(name = Name.lower(), description=Description.lower(), guild_ids=Servers)
                    @discord.option(
                        "args", 
                        description="command arguments, see /help for details",
                        required=True,
                        default='',
                    )
                    async def SlashRun(ctx: discord.ApplicationContext, args):
                        await self.Run(self.Parent, ctx, args)
                else:
                    @Client.command(name = Name.lower(), description=Description.lower(), guild_ids=Servers)
                    async def SlashRun(ctx: discord.ApplicationContext):
                        await self.Run(self.Parent, ctx, None)
            else:
                if self.Args:
                    @Client.command(name = Name.lower(), description=Description.lower())
                    @discord.option(
                        "args", 
                        description="command arguments, see /help for details",
                        required=True,
                        default=''
                    )
                    async def SlashRun(ctx: discord.ApplicationContext, args):
                        await self.Run(self.Parent, ctx, args)
                else:
                    @Client.command(name = Name.lower(), description=Description.lower())
                    async def SlashRun(ctx: discord.ApplicationContext):
                        await self.Run(self.Parent, ctx, None)
        

        async def Run(self, Bot, Ctx: discord.ApplicationContext, Args = None):
            Errored = False
            await Ctx.defer()

            if Bot.CatchErrors:
                try:
                    Colour = "Feedback"
                    self.Feedback = await self.Callback(Types.CommandResponse(True, Ctx), Args)
                except Exception as E:
                    Colour = "Error"
                    self.Feedback = f"Could not run command... Exception: `{E}`"
                    Errored = True
                    ##help(E)
            else:
                Colour = "Feedback"
                self.Feedback = await self.Callback(Types.CommandResponse(True, Ctx), Args)

            if Args == None and self.Args == True:
                Colour = "Error"
                self.Feedback = f"Could not run command... Invalid Args, Use `{Bot.Prefix}help` if you're confused."
                Errored = True
            print(f"Command: {self.Name}, Args: {Args}, Raw: {None}, Feedback: {self.Feedback}")

            if self.Reply:
                if self.Feedback:
                    if self.Embedded or Errored:
                        FeedbackEmbed = discord.Embed(title=self.Feedback, color=Bot.Colours[Colour].value)
                        await Ctx.respond(embed=FeedbackEmbed)
                    else:
                        await Ctx.respond(self.Feedback)
            else:
                await Ctx.delete()
        
    class MultiCommand:
        def __init__(self, Parent, Name, Description, Callback, Args, Reply, Embedded, Server = None):
            self.Slash = Parent.SlashCommand(Parent, Name, Description, Callback, Args, Reply, Embedded, Server)
            self.Text = Parent.Command(Parent, Name, Description, Callback, Args, Reply, Embedded, Server)


    async def Embed(self, Text, Colour: discord.Color, Channel: discord.TextChannel):
        Emb = discord.Embed(title=Text, color=Colour)

        await Channel.send(embed=Emb)
                 
    def Message(Channel: discord.TextChannel, Content: str):
        Channel.send(Content)
