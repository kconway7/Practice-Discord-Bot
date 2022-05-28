import discord
import random
from datetime import datetime
from discord import role
from discord.ext import commands, tasks
from discord.member import Member
bot = commands.Bot(command_prefix = "!")

#has adminstrative capabilities check, used for the more powerful commands
# can use a variation with @commands.has_role(<role or roles goes here as string>)
async def is_admin(context):
        if not context.author.guild_permissions.administrator:
            await context.send("You lack the administrative capabilities to perform this command.")
            return False
        return True

#ping command
@bot.command()
async def ping(context):
    await context.send("Pong!")

#coinflip command
@bot.command()
async def coinflip(context):
    num = random.randint(1,2)
    if num == 1:
        await context.send("Heads!")
    else:
        await context.send("Tails!")

#rock, paper, scissors command
@bot.command()
async def rps(context, hand):
    hands = ["✌️", "✋", "👊"]
    bothand = random.choice(hands)
    await context.send(bothand + "\n")
    
    if hand == bothand:
            await context.send("Draw!")
            return    
    if hand == hands[0] and bothand == hands[1]:
        await context.send("You Win!")
        return
    elif hand == hands[1] and bothand == hands[2]:
        await context.send("You Win!")
        return
    elif hand == hands[2] and bothand == hands[0]:
        await context.send("You Win!")
        return
    else:
         await context.send("I Win!")

# alarm task to check if time is equal to the time specified by the user
@tasks.loop(seconds = 1)
async def alarm(context, hour, minute):
    now = datetime.now().time()
    if now.hour == hour and now.minute == minute:
        await context.author.create_dm()
        await context.author.dm_channel.send("It's Time!")
        alarm.stop()

#command to start alarm task loop
@commands.command()
async def startalarm(context, date):
    hour, minute = date.split(":")
    hour = int(hour)
    minute = int(minute)
    alarm.start(context, hour, minute)

#info that shows commands in embed
@bot.command(aliases = ["info"])
async def about(context):
    MyEmbed = discord.Embed(title = "Commands", description = "These are the Commands that I can do", color = discord.Colour.lighter_grey())
    MyEmbed.set_thumbnail(url = "https://cdn.mos.cms.futurecdn.net/my8AUCgUhKERqBBwdPQuXG.jpg")
    MyEmbed.add_field(name = "!ping", value = "If I am working, I'll respond!")
    MyEmbed.add_field(name = "!coinflip", value = "Lets you flip a coin. Head or Tails.")
    MyEmbed.add_field(name = "!rps <emoji>", value = "Rock, Paper Scissors. Use these emojis ✌️, ✋, or 👊")
    await context.send(embed = MyEmbed)

#group of commands realting to editing server information
@bot.group()
async def edit(context):
    pass 

@edit.command()
@commands.check(is_admin)
async def servername(context, *,input):
    await context.guild.edit(name = input)

@edit.command()
@commands.check(is_admin)
async def region(context, *,input):
    await context.guild.edit(region = input)

@edit.command()
@commands.check(is_admin)
async def createtextchannel(context, *,input):
    await context.guild.create_text_channel(name = input)

@edit.command()
@commands.check(is_admin)
async def createvoicechannel(context, *,input):
    await context.guild.create_voice_channel(name = input)

@edit.command()
@commands.check(is_admin)
async def createrole(context, *,input):
    await context.guild.create_role(name = input)
#End of group commands


# list of kick, ban and unban commands
@bot.command()
@commands.check(is_admin)
async def kick(context, member : discord.Member, *, reason = None):
    await context.guild.kick(member)

@bot.command()
@commands.check(is_admin)
async def ban(context, member : discord.Member, *, reason = None):
    await context.guild.ban(member)

@bot.command()
@commands.check(is_admin)
async def unban(context, *,input):
    name, discriminator = input.split("#")
    banned_members = await context.guild.bans()
    for bannedmember in banned_members:
        username = bannedmember.user.name
        disc = bannedmember.user.discriminator
        if name == username and discriminator == disc:
            await context.guild.unban(bannedmember.user)

#command for deleting messages in a text channel
@bot.command()
@commands.check(is_admin)
async def purge(context, amount, day : int = None, month : int = None, year : int = datetime.now().year):
    if amount == "/":
        if day == None or month == None:
            return 
        else:
            await context.channel.purge(after = datetime(year, month, day))
    else:
        await context.channel.purge(limit = int(amount) + 1)

# Error catcher to infrom users how to user purge command
@purge.error
async def errorhandler(context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await context.send("You must specify a number of messages to delete or a date in (int day, int month, int year) format")
    if isinstance(error, commands.CommandInvokeError):
        await context.send("You must specify a number of messages to delete or a date in (int day, int month, int year) format")

# list of commands for muting,deafening and moving members in voicechat
@bot.command()
@commands.check(is_admin)
async def mute(context, member : discord.Member):
    await member.edit(mute = True)

@bot.command()
@commands.check(is_admin)
async def unmute(context, member : discord.Member):
    await member.edit(mute = False)
    
@bot.command()
@commands.check(is_admin)
async def deafen(context, member : discord.Member):
    await member.edit(deafen = True)

@bot.command()
@commands.check(is_admin)
async def undeafen(context, member : discord.Member):
    await member.edit(deafen = False)

@bot.command()
@commands.check(is_admin)
async def move(context, member : discord.Member, *,voiceChannel : discord.VoiceChannel = None):
    await member.edit(voice_channel = voiceChannel)

@bot.command()
async def reload(context):
    bot.reload_extension("Cogs")

bot.load_extension("Cogs")
#bot.load_extension("Battleship")
#bot.load_extension("Poll Bot")
bot.run("") #Bot token goes here