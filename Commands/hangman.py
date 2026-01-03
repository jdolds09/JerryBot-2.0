import discord
import random_word_gen
from discord.ext import commands

class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word = random_word_gen.random_word()
        self.letters = []
        self.strikes = 0
        self.hit = False
        self.dashes = False

    # Hangman function
    @commands.command()
    async def hangman(self, ctx, *, message=None):
        # User didn't include a letter after !hangman command
        if message is None:
            await ctx.send("You need to include a letter after !hangman")
            await ctx.send("Example: !hangman J")

        else:
            # Get the letter the user guessed
            letter = message[0]
            # User guessed a letter that exists in the hangman word
            if letter in self.word:
                # If user guesses an already correctly guessed letter
                if letter in self.letters:
                    await ctx.send("You already guessed this letter dumbass.")

                else:
                    # If no dashes are output, this stays false and player wins
                    self.dashes = False
                    # Add correctly guessed letter to list
                    self.letters.append(letter)
                    # Output picture of current state of hangman game
                    hangman_picture = f"hangman_{self.strikes}.png"
                    file_path = f"Images/{hangman_picture}"
                    picture = discord.File(file_path)
                    await ctx.send(file=picture)
                    # Output current state of game
                    hangman_word = ""
                    for i in range(len(self.word)):
                        self.hit = False
                        for j in range(len(self.letters)):
                            if self.letters[j] == self.word[i]:
                                hangman_word += self.letters[j]
                                self.hit = True

                        if not self.hit:
                            hangman_word += '-'
                            self.dashes = True
                    await ctx.send(hangman_word)

                    # Check to see if player won
                    if not self.dashes:
                        await ctx.send("**YOU WIN!**")
                        self.word = random_word_gen.random_word()
                        self.letters = []
                        self.strikes = 0

            # Letter guessed is not in the word
            else:
                self.strikes += 1

                # Output picture of current state of hangman game
                hangman_picture = f"hangman_{self.strikes}.png"
                file_path = f"Images/{hangman_picture}"
                picture = discord.File(file_path)
                await ctx.send(file=picture)
                # Output current state of game
                hangman_word = ""
                for i in range(len(self.word)):
                    self.hit = False
                    for j in range(len(self.letters)):
                        if self.letters[j] == self.word[i]:
                            hangman_word += self.letters[j]
                            self.hit = True

                    if not self.hit:
                        hangman_word += '-'
                await ctx.send(hangman_word)

                # Check to see if player lost
                if self.strikes == 6:
                    await ctx.send(f"**HAHAHA YOU LOST! THE WORD WAS {self.word} DUMBASS!**")
                    self.word = random_word_gen.random_word()
                    self.letters = []
                    self.strikes = 0

async def setup(bot):
    await bot.add_cog(Hangman(bot))
