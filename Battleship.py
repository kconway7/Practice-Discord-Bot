import discord
from discord.ext import commands

bot = commands.Bot(command_prefix= "!")

class Battleship(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        #boolean defaulted to False, changes if game is being played
        self.playing = False
        self.board1 = ""
        self.board2 = ""
        self.boardToShowOne = ""
        self.boardToShowTwo = ""
        self.turn = ""

    async def render(self, context, board):

        # lists for setting up the board, contain number and letter emojis
        numbers = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":keycap_ten:"] 
        letters = [":regional_indicator_a:", ":regional_indicator_b:", ":regional_indicator_c:", ":regional_indicator_d:", ":regional_indicator_e:", 
        ":regional_indicator_f:", ":regional_indicator_g:", ":regional_indicator_h:", ":regional_indicator_i:", ":regional_indicator_j:"]

        stringBoard = ""
        stringBoard = stringBoard + ":black_medium_small_square:"

        # sets first row as all the neccessary letter emojis
        for x in range(len(board[0])):
            stringBoard = stringBoard + letters[x]
        stringBoard = stringBoard + "\n"

        #nested for loop that sets the rest of the rows with the number emojis
        i = 0
        for row in board:
            stringBoard = stringBoard + numbers[i]
            i+=1
            for square in row:
                stringBoard = stringBoard + square
            stringBoard = stringBoard + "\n"

        await context.send(stringBoard)

    #command to start a game of battleship
    @commands.command()
    async def battleship(self, context, player2 : discord.Member, ver : int = 5, hor : int = 5):
        if self.playing == False:
            self.playing = True
            self.player1 = context.author
            self.player2 = player2
            self.turn = self.player1
            # these lines of code generate the blue square emoji grid
            self.board1 = [[":blue_square:"]*hor for x in range(ver)]
            self.board2 = [[":blue_square:"]*hor for x in range(ver)]
            self.boardtoshow1 = [[":blue_square:"]*hor for x in range(ver)]
            self.boardtoshow2 = [[":blue_square:"]*hor for x in range(ver)]
            await self.render(self.player1, self.board1)
            await self.render(self.player2, self.board2)
            await self.player1.send("Your game of Battleship has begun. Type !place [xy] to place your ships.")
            await self.player2.send("Your game of Battleship has begun. Type !place [xy] to place your ships.")
        else:
            await context.send("There is already a game of battleship being played.")

    #keeps track of maximum ships and when the game ends
    def shipcount(self, board):
        count = 0
        for row in board:
            for square in row:
                if square == ":ship:":
                    count += 1
        return count
    
    #place ships command, able to place all ships at once(optional)
    @commands.command()
    async def place(self, context, *coordinates):
        if self.playing == True:
            if context.author == self.player1:
                board = self.board1
            if context.author == self.player2:
                board = self.board2
            if len(coordinates) == 0:
                await context.send("Please type in the coordinates.")
            else:
                for coordinate in coordinates:
                    if self.shipcount(board) == 6:
                        await context.send("There is a maximum of 6 ships allowed")
                    else:
                        lowerLetter = coordinate[0].lower()
                        number = coordinate[1]
                        if len(coordinate) == 3:
                            number = 10
                        x = ord(lowerLetter) - 97
                        y = int(number) - 1
                        board[y][x] = ":ship:"
            await self.render(context.author, board)
        else:
            await context.send("A game of battleship is not being played.")

    #shoot command changes emoji in grid based on whether a ship was hit or not
    @commands.command()
    async def shoot(self, context, coordinate):
        
        if self.turn == context.author:
            if self.playing == True:
                if context.author == self.player1:
                    boardtoshoot = self.board2
                    boardtoshow = self.boardtoshow2
                    nextshooter = self.player2

                if context.author == self.player2:
                    boardtoshoot = self.board1
                    boardtoshow = self.boardtoshow1
                    nextshooter = self.player1

                lowerLetter = coordinate[0].lower()
                number = coordinate[1]
                if len(coordinate) == 3:
                        number = 10
                x = ord(lowerLetter) - 97
                y = int(number) - 1
                square = boardtoshoot[y][x]

                #if ship is hit
                if square == ":ship:":
                    await context.send("Hit!")
                    boardtoshoot[y][x] = ":boom:"
                    boardtoshow[y][x] = ":boom:"

                #if shot is a miss
                if square == ":blue_square:":
                    await context.send("Miss.")
                    boardtoshoot[y][x] = ":white_medium_square:"
                    boardtoshow[y][x] = ":white_medium_square:"
                    self.turn = nextshooter
                    await nextshooter.send("It is your turn!")

                #if shot hits an already shot position
                if square == ":white_medium_square:" or square == ":boom:":
                    await context.send("You have already shot this square, try again.")

                await self.render(context.author, boardtoshow)

                if self.shipcount(boardtoshoot) == 0:
                    self.playing = False

                    if context.author == self.player1:
                        await self.player1.send("You have won the game!")
                        await self.player2.send("You have lost the game.")
                        await self.render(self.player2, self.board1)
                    
                    if context.author == self.player2:
                        await self.player2.send("You have won the game!")
                        await self.player1.send("You have lost the game.")
                        await self.render(self.player1, self.board2)
            else:
                await context.send("A game of battleship is not being played.")
        else:
            await context.send("It is not your turn.")

    #some error handlers to prevent crashing
    @battleship.error
    async def errorhandler(self, context, error):
        if isinstance(error,commands.errors.MissingRequiredArgument):
            await context.send("Please mention the second player.")

    @shoot.error
    async def errorhandler(self, context, error):
        if isinstance(error,commands.errors.MissingRequiredArgument):
            await context.send("Please define the cooridinate.")

    @place.error
    async def errorhandler(self, context, error):
        if isinstance(error, commands.errors.CommandInvokeError):
            await context.send("Please type in a proper coordinate.")

def setup(bot):
    bot.add_cog(Battleship(bot))
    
bot.run("") #Bot token goes here