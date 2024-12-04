import discord

class Types:
    
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
                    print("yeah i deleted it")
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
                    print("yeah i deleted it t")
                    await self.Context.delete()
