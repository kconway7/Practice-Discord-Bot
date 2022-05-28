import discord
from discord.ext import commands, tasks

bot = commands.Bot(command_prefix="!")

class MyPoll(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.numbers = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

    @commands.command()
    async def poll(self, context, minutes : int, title, *options):

        # defaults to basic yes and no poll if no options are given
        if len(options) == 0:
            pollEmbed = discord.Embed(title = title, description = f"You have **{minutes}** minutes remaining!" )
            message = await context.send(embed = pollEmbed)
            await message.add_reaction("👍")
            await message.add_reaction("👎")

        #poll with options in embed, labeled with number emojis
        else:
            pollEmbed = discord.Embed(title = title, description = f"You have **{minutes}** minutes remaining!" )
            for number, option in enumerate(options):
                pollEmbed.add_field(name = f"{self.numbers[number]}", value = f"**{option}**", inline = False)
            message = await context.send(embed = pollEmbed)
            for x in range(len(pollEmbed.fields)):
                await message.add_reaction(self.numbers[x])

        self.poll_loop.start(context, minutes, title, options, message)

    #task that checks every minute if poll is finished
    @tasks.loop(minutes = 1)
    async def poll_loop(self, context, minutes, title, options, message):

        count = self.poll_loop.current_loop
        remaining_time = minutes - count

        newEmbed = discord.Embed(title = title, description = f"You have **{remaining_time}** minutes remaining!" )
        for number, option in enumerate(options):
                newEmbed.add_field(name = f"{self.numbers[number]}", value = f"**{option}**", inline = False)

        await message.edit(embed = newEmbed)

        if remaining_time == 0:
            counts = []
            message = discord.utils.get(bot.cached_messages, id = message.id)
            reactions = message.reactions

            for reaction in reactions:
                counts.append(reaction.count)
            max_value = max(counts)
            i = 0
            for count in counts:
                if count == max_value:
                    i += 1
            if i > 1:
                await context.send("It's a Draw!")

            else:
                max_index = counts.index(max_value)

                if len(options) == 0:
                    winneremoji = reactions[max_index]
                    await context.send("Times Up!")

                    if winneremoji.emoji == "👍":
                        await context.send("Looks like people think that way.")
                    if winneremoji.emoji == "👎":
                        await context.send("Looks like people don't think that way.") 
                else:
                    winner = options[max_index]
                    winneremoji = reactions[max_index]

                    await context.send("Times Up!")
                    await context.send(f"{winneremoji.emoji} **{winner}** has won the Poll!")
                
            self.poll_loop.stop()

def setup(bot):
    bot.add_cog(MyPoll(bot))

bot.run("") #Bot token goes here