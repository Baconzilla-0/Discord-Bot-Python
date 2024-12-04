import os, datetime, discord

class Utils:
    def Folder(Path):
        if os.path.exists(Path) != True:
            os.mkdir(Path)

        return True
    
    def Log(Msg, Timestamp: datetime.datetime, Channel: discord.TextChannel, User):
        ServerFolder = f"./Logs/{Channel.guild.name} - {Channel.guild.id}"
        CatagoryFolder = f"{ServerFolder}/{Channel.category.name} - {Channel.category.id}"
        
        Utils.Folder(ServerFolder)
        Utils.Folder(CatagoryFolder)
        Utils.Folder()

        ChannelType = None
        if Channel.type == discord.ChannelType.text:
            print('Text Channel')
            ChannelType = "Text"
        elif Channel.type == discord.ChannelType.voice:
            print('Voice Channel')
            ChannelType = "Voice"
        

        with open(f"{CatagoryFolder}/{Channel.name} - {Channel.id}.txt", "a") as LogFile:
            try:
                LogFile.write(f"[ {Timestamp.day}/{Timestamp.month}/{Timestamp.year} | {Timestamp.hour}:{Timestamp.minute}:{Timestamp.second} ] {User} > {Msg} \n")
            except UnicodeError:
                print("Unicode shit itself again :[")
            print(f"[ {Timestamp.day}/{Timestamp.month}/{Timestamp.year} | {Timestamp.hour}:{Timestamp.minute}:{Timestamp.second} ] {User} > {Msg}")
    
    def Bar(Max, Value, Length):
        PartBar = ""
        Percent = Value / Max
        Scaled = int(Percent * Length)
        Remain = Length - Scaled
        print(Scaled, Remain)
        PartBar = PartBar.rjust(Scaled,"█")
        for i in range(Remain):
            PartBar = PartBar + "▒"
        
        return f"{PartBar}"
    