# The bot interface for autocape
from discord.ext import commands
import discord, random, json
from autocape import cape, city, encounter

#Temporary test memory

async def loadcapes():
    with open('autocape/capes.json', 'r+') as capefile:
        if len(capefile.read()):
            capefile.seek(0)
            chars = json.load(capefile)
        else:
            chars = {}
    return chars

class Autocape(commands.Cog):

    def __init__(self):
        self.records = {}


    @commands.command()
    async def ac(self, ctx, cmd, *args):
        if cmd == 'newcity':
            await self.newcity(ctx, *args)
        elif cmd == 'show':
            await self.show(ctx, *args)
        elif cmd == 'gen':
            await self.gen(ctx, *args)
        elif cmd == 'checkup':
            await self.checkup(ctx, *args)
        elif cmd == 'status':
            await self.status(ctx, *args)
        elif cmd == 'history':
            await self.history(ctx, *args)
        elif cmd == 'update':
            await self.update(ctx, *args)
        elif cmd == 'log':
            await self.log(ctx, *args)
        elif cmd == 'clear':
            await self.clear(ctx, *args)
        elif cmd == 'delete':
            await self.delete(ctx, *args)
        elif cmd == 'addcape':
            await self.addcape(ctx, *args)
        elif cmd == 'load':
            await self.load(ctx, *args)


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


    async def gen(self, ctx, *args):
        '''Generate a cape for the autocape city
        '''
        id = str(ctx.author.id)
        capes = await loadcapes()
        if id in capes:
            await ctx.send("You already have a cape.")
            return
        x = cape.Cape(str(ctx.author.id),None)
        x.pc = True
        x.givePlayer(ctx.author.display_name)
        entry = x.jsonDict()
        capes[id] = entry
        with open('autocape/capes.json', 'w+') as capefile:
            json.dump(capes, capefile)
        await ctx.send("```" + x.status() + "```")
        await ctx.send("Cape created.")


    async def checkup(self, ctx, *args):
        '''Checks up on your current cape
        '''
        # TODO Something happens
        await ctx.send("Displaying events since last checkup.")


    async def status(self, ctx, *args):
        '''Displays current status of your cape
        '''
        id = str(ctx.author.id)
        capes = await loadcapes()
        if id not in capes:
            await ctx.send("You don't have a cape.")
            return
        x = cape.Cape(id,capes[id])
        await ctx.send("```" + x.status() + "```")


    async def history(self, ctx, *args):
        '''Reveal prior experiences of your cape
        '''
        id = str(ctx.author.id)
        capes = await loadcapes()
        if id not in capes:
            await ctx.send("You don't have a cape.")
            return
        x = cape.Cape(id,capes[id])
        await ctx.send("```" + x.history() + "```")


    async def update(self, ctx, *args):
        update = ''
        if self.records == {}:
            await ctx.send("Wheeeee!")
        elif 'city' in self.records:
            for team in self.records['city'].teams:
                for cape in team.capes:
                    cape.decide()
            for team in self.records['city'].teams:
                for cape in team.capes:
                    if cape.state == 0 or cape.state == 2:
                        num = random.randint(0,(len(self.records['city'].capes) - 1))
                        tarName = self.records['city'].capes[num]
                        target = self.records['city'].search(tarName)
                        if target.alias != cape.alias:
                            update += await encounter.fight(cape,target)

            if update == '':
                update = "Nothing happened."
            await ctx.send("```" + update + "```")
            self.records['logs'] += update
            await ctx.send("Update complete.")

        elif 'capes' in self.records:
            for fighter in self.records['capes']:
                fighter.decide()
            for cape in self.records['capes']:
                    if cape.state == 0 or cape.state == 2:
                        num = random.randint(0,(len(self.records['capes']) - 1))
                        target = self.records['capes'][num]
                        if target.alias != cape.alias:
                            update += await encounter.fight(cape,target)

            if update == '':
                update = "Nothing happened."
            await ctx.send("```" + update + "```")
            self.records['logs'] += update
            await ctx.send("Update complete.")


    async def log(self,ctx,*args):
        if not self.records or not self.records['logs'] or self.records['logs'] == '```':
            await ctx.send("0二二二二二二二)")
        else:
            await ctx.send(self.records['logs'] + '```')


    async def clear(self,ctx,*args):
        capes = {}
        with open('autocape/capes.json', 'w+') as capefile:
            json.dump(capes, capefile)
        await ctx.send("Data cleared.")


    async def delete(self,ctx,*args):
        capes = await loadcapes()
        if str(ctx.author.id) not in capes:
            await ctx.send("You have nothing to delete.")
            return
        del capes[str(ctx.author.id)]
        with open('autocape/capes.json', 'w+') as capefile:
            json.dump(capes, capefile)
        await ctx.send("Cape deleted.")


    async def addcape(self,ctx,*args):
        id = random.randint(0,10000)
        capes = await loadcapes()
        x = cape.Cape(id, None)
        x.pc = False
        x.givePlayer('None')
        entry = x.jsonDict()
        capes[id] = entry
        with open('autocape/capes.json', 'w+') as capefile:
            json.dump(capes, capefile)
        await ctx.send("```" + x.status() + "```")
        await ctx.send("Cape created.")


    async def load(self, ctx, *args):
        if args[0] == 'ring':
            self.records['capes'] = []
            capes = await loadcapes()
            for id in capes:
                x = cape.Cape(id, capes[id])
                self.records['capes'].append(x)
                self.records['logs'] = '```'
            await ctx.send("Loaded all genned capes.")
        elif args[0] == 'blank':
            self.records = {}
            await ctx.send("Cleared memory.")
        else:
            await ctx.send("Error.")