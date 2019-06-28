# The bot interface for autocape
from discord.ext import commands
import discord
from autocape import cape, city

#Temporary test memory

class Autocape(commands.Cog):

    def __init__(self):
        self.records = {}

    @commands.command()
    async def newcity(self, ctx, *args):
        '''Generate a new autocape city
        '''
        if not self.records:
            self.records = {}
        await ctx.send("Creating city")
        self.records['city'] = city.City('Testville', 100000, 5)
        await ctx.send(self.records['city'].name + " created.")

    @commands.command()
    async def gen(self, ctx, *args):
        '''Generate a cape for the autocape city
        '''
        x = cape.Cape()
        await ctx.send("```" + x.status() + "```")
        await ctx.send("Cape created.")


    @commands.command()
    async def checkup(self, ctx, *args):
        '''Checks up on your current cape
        '''
        # TODO Something happens
        await ctx.send("Displaying events since last checkup.")


    @commands.command()
    async def status(self, ctx, *args):
        '''Displays current status of your cape
        '''
        # TODO Something happens
        await ctx.author.send("```I haven't figured this out yet.```")
        await ctx.send("Displaying status in PM.")


    @commands.command()
    async def history(self, ctx, *args):
        '''Reveal prior experiences of your cape
        '''
        #  TODO Something happens
        await ctx.author.send("```This hasn't been implemented yet```")
        await ctx.send("Displaying history in PM.")
