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
        info = (await sheets.cape(name))
        if info:
            output = "**" + info[0] + "**"
            if len(info) > 5 and not info[5] == "":
                output += " (" + info[5] + ")"
            output += "\n"
            if len(info) > 9 and not info[9] == "":
                output += "> Status: **" + info[9] + "**\n"
            if len(info) > 1 and not info[1] == "":
                output += "> Civilian identity: ||" + info[1] + "||\n"
            if (len(info) > 3 and not info[3] == "") or (len(info) > 4 and not info[4] == ""):
                output += "> Affiliation: " + info[3]
                if len(info) > 4 and (not info[3] == "" and not info[4] == ""):
                    output += ", "
                output += info[4] + "\n"
            if len(info) > 2 and not info[2] == "":
                output += "> Power: " + info[2] + "\n"
            if len(info) > 7 and not info[7] == "":
                output += "> Campaign: **" + info[7] + "**\n"
            if len(info) > 8 and not info[8] == "":
                output += "> Owner: **" + info[8] + "**"
                if len(info) > 6 and not info[6] == "":
                    output += ", " + info[6]
                output += "\n"
            elif len(info) > 6 and not info[6] == "":
                output += "> Unowned, **" + info[6] + "**\n"
            if len(info) > 10 and not info[10] == "":
                output += "> Additional notes: " + info[10]
            await ctx.send(output)
            #await ctx.send(str(info))
        else:
            await ctx.send("Couldn't find cape!")
