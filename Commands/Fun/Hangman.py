import discord
import random_word_gen
from discord.ext import commands

class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hangman_game = {}

    # Hangman function
    @commands.command()
    async def hangman(self, ctx, *, message=None):
        # Get guild id
        guild_id = ctx.guild.id

        # Create hangman game attributes, guild_id is required to keep each server hangman game info separate
        if guild_id not in self.hangman_game:
            self.hangman_game[guild_id] = {}
            self.hangman_game[guild_id]["word"] = random_word_gen.random_word().lower()
            self.hangman_game[guild_id]["letters"] = []
            self.hangman_game[guild_id]["strikes"] = 0
            self.hangman_game[guild_id]["hit"] = False
            self.hangman_game[guild_id]["dashes"] = False

        # User didn't include a letter after !hangman command
        if message is None:
            await ctx.send("You need to include a letter after !hangman dumbass")
            await ctx.send("Example: !hangman J")

        else:
            # Get the letter the user guessed
            letter = message[0].lower()
            # User guessed a letter that exists in the hangman word
            if letter in self.hangman_game[guild_id]["word"]:
                # If user guesses an already correctly guessed letter
                if letter in self.hangman_game[guild_id]["letters"]:
                    await ctx.send("You already guessed this letter dumbass.")

                else:
                    # If no dashes are output, this stays false and player wins
                    self.hangman_game[guild_id]["dashes"] = False
                    # Add correctly guessed letter to list
                    self.hangman_game[guild_id]["letters"].append(letter)
                    # Output picture of current state of hangman game
                    hangman_picture = f"hangman_{self.hangman_game[guild_id]["strikes"]}.png"
                    file_path = f"Images/{hangman_picture}"
                    picture = discord.File(file_path)
                    await ctx.send(file=picture)
                    # Output current state of game
                    hangman_word = ""
                    for i in range(len(self.hangman_game[guild_id]["word"])):
                        self.hangman_game[guild_id]["hit"] = False
                        for j in range(len(self.hangman_game[guild_id]["letters"])):
                            if self.hangman_game[guild_id]["letters"][j] == self.hangman_game[guild_id]["word"][i]:
                                hangman_word += self.hangman_game[guild_id]["letters"][j]
                                self.hangman_game[guild_id]["hit"] = True

                        if not self.hangman_game[guild_id]["hit"]:
                            hangman_word += '-'
                            self.hangman_game[guild_id]["dashes"] = True
                    await ctx.send(hangman_word)

                    # Check to see if player won
                    if not self.hangman_game[guild_id]["dashes"]:
                        await ctx.send("**YOU WIN!**")
                        self.hangman_game[guild_id]["word"] = random_word_gen.random_word()
                        self.hangman_game[guild_id]["letters"] = []
                        self.hangman_game[guild_id]["strikes"] = 0

            # Letter guessed is not in the word
            else:
                self.hangman_game[guild_id]["strikes"] += 1

                # Output picture of current state of hangman game
                hangman_picture = f"hangman_{self.hangman_game[guild_id]["strikes"]}.png"
                file_path = f"Images/{hangman_picture}"
                picture = discord.File(file_path)
                await ctx.send(file=picture)
                # Output current state of game
                hangman_word = ""
                for i in range(len(self.hangman_game[guild_id]["word"])):
                    self.hangman_game[guild_id]["hit"] = False
                    for j in range(len(self.hangman_game[guild_id]["letters"])):
                        if self.hangman_game[guild_id]["letters"][j] == self.hangman_game[guild_id]["word"][i]:
                            hangman_word += self.hangman_game[guild_id]["letters"][j]
                            self.hangman_game[guild_id]["hit"] = True

                    if not self.hangman_game[guild_id]["hit"]:
                        hangman_word += '-'
                await ctx.send(hangman_word)

                # Check to see if player lost
                if self.hangman_game[guild_id]["strikes"] == 6:
                    uppercase_word = self.hangman_game[guild_id]["word"].upper()
                    await ctx.send(f"**HAHAHA YOU LOST! THE WORD WAS __{uppercase_word}__ DUMBASS!**")
                    self.hangman_game[guild_id]["word"] = random_word_gen.random_word()
                    self.hangman_game[guild_id]["letters"] = []
                    self.hangman_game[guild_id]["strikes"] = 0

    async def command_help(self, ctx):
        await ctx.send("**!hangman [letter]**: Play a game of hangman.")

async def setup(bot):
    await bot.add_cog(Hangman(bot))
