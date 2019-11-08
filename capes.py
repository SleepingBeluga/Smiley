from discord.ext import commands
import discord, sheets

class Capes(commands.Cog):
    @commands.command()
    async def cape(self, ctx, *args):
        # Search for the cape name
        name = ""
        for arg in args:
            name += arg + " "

        name = name[:-1]
        await ctx.send("Getting info")
        info = (await sheets.cape(name))
        await ctx.send("Info collected, parsing...")
        if info:
            output = "**" + info[0] + "**"
            if not info[5] == "":
                output += " (" + info[5] + ")"
            output += "\n"
            if not info[9] == "":
                output += "> Status: **" + info[9] + "**\n"
            if not info[1] == "":
                output += "> Civilian identity: ||" + info[1] + "||\n"
            if not info[3] == "" or not info[4] == "":
                output += "> Affiliation: " + info[3]
                if not info[3] == "" and not info[4] == "":
                    output += ", "
                output += info[4] + "\n"
            if not info[2] == "":
                output += "> Power: " + info[2] + "\n"
            if not info[7] == "":
                output += "> Campaign: " + info[7] + "\n"
            if not info[8] == "":
                output += "> Owner: " + info[8]
                if not info[6] == "":
                    output += ", " + info[6]
                output += "\n"
            elif not info[6] == "":
                output += "> Unowned, **" + info[6] + "**\n"
            if not info[10] == "":
                output += "> Additional notes: " + info[10]
            await ctx.send(output)
            #await ctx.send(str(info))
        else:
            await ctx.send("Couldn't find cape!")
