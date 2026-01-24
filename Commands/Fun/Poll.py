import discord
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Poll function
    @commands.command()
    async def poll(self, ctx, *, message = None):

        # Dumbass user didn't format the poll command correctly
        if message is None:
            await ctx.send("You need to have at least one argument dumbass")
            await ctx.send("To create a Yes/No poll, follow the format:")
            await ctx.send("!poll \"Is Jerry the most handsome man on the planet?\"")
            await ctx.send("To create a multi choice poll, follow the format:")
            await ctx.send("!poll \"What are we playing for game night?\" \"KOTOR\" \"KOTOR 2\" \"The Witcher 3\"")

        else:
            # Create reaction variables
            yn_reactions = ["👍", "👎", "🤷‍♂️"]
            num_reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

            #Replace unicode quotation marks with ascii quotation marks
            message = message.replace('\u201c', '"')
            message = message.replace('\u201d', '"')

            #Check to see if user used quotation marks
            quotation_marks = "\""
            if quotation_marks not in message:
                await ctx.send("Separate each argument with quotation marks")
                await ctx.send("To create a Yes/No poll, follow the format:")
                await ctx.send("!poll \"Is Jerry the most handsome man on the planet?\"")
                await ctx.send("To create a multi choice poll, follow the format:")
                await ctx.send("!poll \"What are we playing for game night?\" \"KOTOR\" \"KOTOR 2\" \"The Witcher 3\"")

            # Split the message arguments
            # for some reason the first and last elements of the list are quotation marks
            # so, I am removing the first and last elements of the list
            msg = message.split("\"")
            del msg[0]
            msg.pop()
            # Also for some reason in between each argument there is a blank string
            # Need to get rid of the blank strings
            msg = [i for i in msg if not i.isspace() and i]

            # Dumbass user didn't format the poll command correctly
            if len(msg) == 0:
                await ctx.send("You need to have at least one argument dumbass")
                await ctx.send("To create a Yes/No poll, follow the format:")
                await ctx.send("!poll \"Is Jerry the most handsome man on the planet?\"")
                await ctx.send("To create a multi choice poll, follow the format:")
                await ctx.send("!poll \"What are we playing for game night?\" \"KOTOR\" \"KOTOR 2\" \"The Witcher 3\"")

            # Too many arguments
            elif len(msg) > 10:
                await ctx.send("Too many arguments!")
                await ctx.send("Please limit the number of poll options to 9 or fewer.")

            # Create a Yes/No Poll
            elif len(msg) == 1:
                embed = discord.Embed(title=f" 📊{msg[0]}", color=0x0000FF)
                poll_message = await ctx.send(embed=embed)
                await poll_message.add_reaction(yn_reactions[0])
                await poll_message.add_reaction(yn_reactions[1])
                await poll_message.add_reaction(yn_reactions[2])

            # Create a multi answer Poll
            else:
                embed = discord.Embed(title=f"📊 {msg[0]},", color=0x0000FF)
                del msg[0]
                for i, option in enumerate(msg):
                    embed.add_field(name=f"{msg[i]}", value=f"{num_reactions[i]}", inline=False)

                poll_message = await ctx.send(embed=embed)

                for i, option in enumerate(msg):
                    await poll_message.add_reaction(num_reactions[i])

    async def command_help(self, ctx):
        await ctx.send("**!poll \"[Question]\" OPTIONAL: \"[Choice 1]\" \"[Choice 2]\" \"[Choice 3]\" etc**: Create a Yes/No poll or a multi choice poll.")

async def setup(bot):
    await bot.add_cog(Poll(bot))