import discord
import BaconBotLib as BotLib
from BaconBotLib.Types import Types

Bot = BotLib.Bot()
Music = BotLib.Music(Bot)

async def KillCommand(Response: Types.CommandResponse, Args: str):
    await Response.Respond(Embed=discord.Embed(title=f"Bye!", color=discord.Color.red()))
    exit("User Exited")
Bot.MultiCommand(Bot, "Kill", "Stops the bot.", KillCommand, False, False, False)

async def SayCommand(Response: Types.CommandResponse, Args: str):
    Args = Args.split(" ", 2)
    Guild =  Bot.Client.get_guild(int(Args[0]))
    Channel = Guild.get_channel(int(Args[1]))
    Message = await Channel.send(Args[2])
    Embed = discord.Embed(title=f"Sent message in server `{Guild.name}`, `{Channel.name}`", description=f"[Message Link](https://discord.com/channels/{Guild.id}/{Channel.id}/{Message.id})")

    await Response.Respond(Embed=Embed)

Bot.MultiCommand(Bot, "Say", f"I love spreading misinformation, syntax: {Bot.Prefix}say [serverid] [channelid] [Text]", SayCommand, True, False, False)

async def InviteCommand(Response: Types.CommandResponse, Args: str):
    return f"Here Ya Go! ||{Bot.Invite}||"
Bot.MultiCommand(Bot, "Invite", "Get the bots invite link.", InviteCommand, False, True, False)

async def HelloCommand(Response: Types.CommandResponse, Args: str):
    return f"Hello, <@{Response.Context.author.id}>"
Bot.MultiCommand(Bot, "Hello", "Say Hello! :D", HelloCommand, False, True, False)

async def DMCommand(Response: Types.CommandResponse, Args: str):
    Send = Args.split(" ", 1)[1]
    Mention = Args.split(" ", 1)[0].removeprefix("<@").removesuffix(">")

    #User = Response.Context.mentions[0]
    User = Bot.Client.get_user(int(Mention))
    DirectMessage = User.dm_channel
    if DirectMessage == None:
        DirectMessage = await User.create_dm()

    Embed = discord.Embed(title=f"From: {Response.Context.author.name} in {Response.Context.guild.name}", description=Send, color=Bot.Colours["Other"].value)

    await Response.Respond(Embed=Embed)
    await DirectMessage.send(embed=Embed)
Bot.MultiCommand(Bot, "DM", f"Sends a dm to a user of your choice, syntax: {Bot.Prefix}DM `@Mention` [Your text here].", DMCommand, True, False, True)

async def JoinCommand(Response: Types.CommandResponse, Args: str):
    if (Response.Context.author.voice): # If the person is in a channel
        channel = Response.Context.author.voice.channel
        await channel.connect()
        return f"Bot joined <#{Response.Context.author.voice.channel.id}>"
    else: #But is (s)he isn't in a voice channel
        return "You must be in a voice channel first so I can join it."
Bot.MultiCommand(Bot, "Join", "Makes the bot join your voice channel.", JoinCommand, False, True, False)

async def LeaveCommand(Response: Types.CommandResponse, Args: str):
    if (Response.Context.guild.voice_client): # If the bot is in a voice channel 
        await Response.Context.guild.voice_client.disconnect(force=True) # Leave the channel 
        return f"Bot left"
    else: # But if it isn't
        return "I'm not in a voice channel, use the join command to make me join"
Bot.MultiCommand(Bot, "Leave", "makes the bot leave your voice channel.", LeaveCommand, False, True, False)

Bot.Run()