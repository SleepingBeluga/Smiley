# The bot interface for autocape
from discord.ext import commands
import discord, random, json
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
        await ctx.send("Creating city...")
        self.records['city'] = city.City('Testville', 100000, 5)
        self.records['logs'] = '```'
        await ctx.send(self.records['city'].name + " created.")
        await ctx.send(self.records['city'].info())

    @commands.command()
    async def show(self,ctx,*args):
        '''Navigate through the city
        '''
        if not self.records or not self.records['city']:
            await ctx.send("There's nothing to show.")
        else:
            capeName = ''
            for word in args:
                capeName += word + ' '
            capeName = capeName[:-1]
            check = False
            if args[0] == 'city':
                await ctx.send(self.records['city'].info())
                check = True
            for district in self.records['city'].districts:
                if args[0] == district.name:
                    await ctx.send(district.info())
                    check = True
            for team in self.records['city'].teams:
                if args[0] == team.name:
                    await ctx.send(team.info())
                    check = True
                for cape in team.capes:
                    if capeName == cape.alias:
                        await ctx.send('```' + cape.status() + '```')
                        check = True
            if check == False:
                await ctx.send("Nothing found.")



    @commands.command()
    async def gen(self, ctx, *args):
        '''Generate a cape for the autocape city
        '''
        id = str(ctx.author.id)
        capes = await self.loadcapes()
        if id in capes:
            await ctx.send("You already have a cape.")
            return
        x = cape.Cape(str(ctx.author.id),None)
        x.pc = True
        x.givePlayer(ctx.author.display_name)
        entry = x.jsonDict()
        capes[id] = entry
        with open('capes.json', 'w+') as capefile:
            json.dump(capes, capefile)
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

        id = str(ctx.author.id)
        capes = await self.loadcapes()
        if id not in capes:
            await ctx.send("You don't have a cape.")
            return
        x = cape.Cape(id,capes[id])
        await ctx.send("```" + x.status() + "```")



    @commands.command()
    async def history(self, ctx, *args):
        '''Reveal prior experiences of your cape
        '''
        #  TODO Something happens
        await ctx.author.send("```This hasn't been implemented yet```")
        await ctx.send("Displaying history in PM.")

    @commands.command()
    async def round(self, ctx, *args):
        update = ''
        if not self.records or not self.records['city']:
            await ctx.send("Wheeeee!")
        else:
            for team in self.records['city'].teams:
                for cape in team.capes:
                    cape.decide()
            for team in self.records['city'].teams:
                for cape in team.capes:
                    if cape.state == 0 or cape.state == 2:
                        num = random.randint(0,(len(self.records['city'].capes) - 1))
                        tarName = self.records['city'].capes[num]
                        target = self.records['city'].search(tarName)
                        if cape.state == 2:
                            update += str(cape.alias) + " attacked " + str(target.alias) + "!\n"
                            if target.state == 2:
                                update += str(target.alias) + " fought " + str(cape.alias) + " off\n"
                            elif target.state == 1:
                                update += str(target.alias) + " beat them up!\n"
                            elif target.state == 0:
                                update += str(cape.alias) + " beat them up!\n"
                        elif cape.state == 0:
                            update += str(cape.alias) + " plotted against " + str(target.alias) + "\n"
                            if target.state == 2:
                                update += str(target.alias) + " beat them up!\n"
                            elif target.state == 1:
                               update += str(cape.alias) + " has a plan\n"
                            elif target.state == 0:
                                update += str(target.alias) + " found " + str(cape.alias) + " out!\n"

            await ctx.send("```" + update + "```")
            self.records['logs'] += update
            await ctx.send("Update complete.")

    @commands.command()
    async def log(self,ctx,*args):
        if not self.records or not self.records['logs'] or self.records['logs'] == '```':
            await ctx.send("0二二二二二二二)")
        else:
            await ctx.send(self.records['logs'] + '```')

    async def loadcapes(self):
        with open('capes.json', 'r+') as capefile:
            if len(capefile.read()):
                capefile.seek(0)
                chars = json.load(capefile)
            else:
                chars = {}
        return chars

    @commands.command()
    async def clear(self,ctx,*args):
        capes = {}
        with open('capes.json', 'w+') as capefile:
            json.dump(capes, capefile)
        await ctx.send("Data cleared.")

    @commands.command()
    async def delete(self,ctx,*args):
        capes = await self.loadcapes()
        if str(ctx.author.id) not in capes:
            await ctx.send("You have nothing to delete.")
            return
        del capes[str(ctx.author.id)]
        with open('capes.json', 'w+') as capefile:
            json.dump(capes, capefile)
        await ctx.send("Cape deleted.")