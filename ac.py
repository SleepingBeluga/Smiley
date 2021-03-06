# The bot interface for autocape
from discord.ext import commands
import discord, random, json, asyncio, io
from autocape import cape, city, encounter


async def ac_loop(b):
    await b.wait_until_ready()
    while True:
        await asyncio.sleep(3600)
        update = ''
        #if 'city' in thing.records:
            #for team in thing.records['city'].teams:
                #for cape in team.capes:
                    #cape.decide()
            #for team in thing.records['city'].teams:
                #for cape in team.capes:
                    #if cape.state == 0 or cape.state == 2:
                        #num = random.randint(0, (len(thing.records['city'].capes) - 1))
                        #tarName = thing.records['city'].capes[num]
                        #target = thing.records['city'].search(tarName)
                        #if target.alias != cape.alias:
                            #update += await encounter.fight(cape, target)

            #if update == '':
                #update = "Nothing happened."
            #thing.records['logs'] += update

        #elif 'capes' in thing.records:
        chars = await loadcons()
        for fighter in chars:
            fighter.decide(False)
        for cape in chars:
            if cape.state == 0 or cape.state == 2:
                num = random.randint(0, (len(chars) - 1))
                target = chars[num]
                if target.alias != cape.alias:
                    update += await encounter.fight(cape, target)


async def loadcapes():
    with open('autocape/capes.json', 'r+') as capefile:
        if len(capefile.read()):
            capefile.seek(0)
            chars = json.load(capefile)
        else:
            chars = {}
    return chars

async def loadcons():
    thing = []
    capes = await loadcapes()
    for id in capes:
        x = cape.Cape(id, capes[id])
        thing.append(x)
    return thing


class Autocape(commands.Cog):

    @commands.command()
    async def ac(self, ctx, cmd, *args):
        if cmd == 'newcity':
            await self.newcity(ctx, *args)
        elif cmd == 'gen':
            await self.gen(ctx, *args)
        elif cmd == 'status':
            await self.status(ctx, *args)
        elif cmd == 'history':
            await self.history(ctx, *args)
        elif cmd == 'fullhistory':
            await self.fullhistory(ctx,*args)
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
        elif cmd == 'fight':
            await self.fight(ctx, *args)
        elif cmd == 'talk':
            await self.talk(ctx, *args)
        elif cmd == 'rename':
            await self.rename(ctx, *args)
        elif cmd == 'help':
            await self.help(ctx, *args)


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

    #
    # async def show(self,ctx,*args):
    #     '''Navigate through the city
    #     '''
    #     if not self.records or not self.records['city']:
    #         await ctx.send("There's nothing to show.")
    #     else:
    #         capeName = ''
    #         for word in args:
    #             capeName += word + ' '
    #         capeName = capeName[:-1]
    #         check = False
    #         if args[0] == 'city':
    #             await ctx.send(self.records['city'].info())
    #             check = True
    #         for district in self.records['city'].districts:
    #             if args[0] == district.name:
    #                 await ctx.send(district.info())
    #                 check = True
    #         for team in self.records['city'].teams:
    #             if args[0] == team.name:
    #                 await ctx.send(team.info())
    #                 check = True
    #             for cape in team.capes:
    #                 if capeName == cape.alias:
    #                     await ctx.send('```' + cape.status() + '```')
    #                     check = True
    #         if check == False:
    #             await ctx.send("Nothing found.")


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


    async def history(self,ctx,*args):
        id = str(ctx.author.id)
        capes = await loadcapes()
        if id not in capes:
            await ctx.send("You don't have a cape.")
            return
        x = cape.Cape(id,capes[id])
        final = ''
        shorten = x.history()
        shorten = shorten.splitlines()
        if len(shorten) >= 5:
            for z in range(0,5):
                final += shorten[len(shorten) - z - 1]
                final += "\n"
            await ctx.send("```" + final + "```")
        else:
            await ctx.send("```" + x.history() + "```")


    async def fullhistory(self, ctx, *args):
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
        # if self.records == {}:
        #      await ctx.send("Wheeeee!")
        # elif 'city' in self.records:
        #     for team in self.records['city'].teams:
        #         for cape in team.capes:
        #             cape.decide()
        #     for team in self.records['city'].teams:
        #         for cape in team.capes:
        #             if cape.state == 0 or cape.state == 2:
        #                 num = random.randint(0,(len(self.records['city'].capes) - 1))
        #                 tarName = self.records['city'].capes[num]
        #                 target = self.records['city'].search(tarName)
        #                 if target.alias != cape.alias:
        #                     update += await encounter.fight(cape,target)
        #
        #     if update == '':
        #         update = "Nothing happened."
        #     await ctx.send("```" + update + "```")
        #     self.records['logs'] += update
        #     await ctx.send("Update complete.")
        #
        # elif 'capes' in self.records:
        chars = await loadcons()
        for fighter in chars:
            fighter.decide(False)
        for cape in chars:
                if cape.state != 1:
                    num = random.randint(0,(len(chars) - 1))
                    target = chars[num]
                    if target.alias != cape.alias and cape.state != 3:
                        update += await encounter.fight(cape,target)
                    elif target.alias != cape.alias and cape.state == 3:
                        update += await encounter.talk(cape,target)


        if update == '':
           update = "Nothing happened."
        await ctx.send("```" + update + "```")
        await ctx.send("Update complete.")


    async def log(self,ctx,*args):
        await ctx.send("0?????????????????????)")


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

    #
    # async def load(self, ctx, *args):
    #     if args[0] == 'ring':
    #         self.records['capes'] = []
    #         capes = await loadcapes()
    #         for id in capes:
    #             x = cape.Cape(id, capes[id])
    #             self.records['capes'].append(x)
    #             self.records['logs'] = '```'
    #         await ctx.send("Loaded all genned capes.")
    #     elif args[0] == 'blank':
    #         self.records = {}
    #         await ctx.send("Cleared memory.")
    #     else:
    #         await ctx.send("Error.")

    async def fight(self, ctx, *args):
        update = ''
        capes = await loadcons()
        userCape = None
        for dude in capes:
            if str(dude.id) == str(ctx.author.id):
                userCape = dude
        if userCape == None:
            await ctx.send("You don't have anyone to fight with.")
        else:
            targetName = ''
            for arg in args:
                targetName += arg + ' '
            targetName = targetName[:-1]
            target = None
            for dude in capes:
                if dude.alias.lower() == targetName.lower():
                    target = dude
                elif dude.playerName.lower() == targetName.lower():
                    target = dude
            if target == None:
                await ctx.send("Target not found.")
            else:
                if userCape == target:
                    await ctx.send('Why are you hitting yourself?')
                    return
                userCape.decide(True)
                target.decide(True)
                update += await encounter.fight(userCape, target)
                if update == '':
                    update += "They both defended. Nothing happened."
                await ctx.send("```" + update + "```")

    async def talk(self, ctx, *args):
        update = ''
        capes = await loadcons()
        userCape = None
        for dude in capes:
            if str(dude.id) == str(ctx.author.id):
                userCape = dude
        if userCape == None:
            await ctx.send("You don't have anyone to talk with.")
        else:
            targetName = ''
            for arg in args:
                targetName += arg + ' '
            targetName = targetName[:-1]
            target = None
            for dude in capes:
                if dude.alias.lower() == targetName.lower():
                    target = dude
                elif dude.playerName.lower() == targetName.lower():
                    target = dude
            if target == None:
                await ctx.send("Target not found.")
            else:
                if userCape == target:
                    await ctx.send(str(userCape.alias) + " babbles to themselves. *Alone*.")
                    return
                update += await encounter.talk(userCape, target)
                await ctx.send("```" + update + "```")


    async def rename(self, ctx, *args):
        thing = str(ctx.author.id)
        capes = await loadcapes()
        if thing not in capes:
            await ctx.send("You don't have anyone to rename.")
            return
        x = cape.Cape(thing, capes[thing])
        newAlias = ''
        for arg in args:
            newAlias += arg + ' '
        newAlias = newAlias[:-1]
        x.alias = newAlias
        await x.updateCape()
        await ctx.send("Your cape is now named " + newAlias + ".")
    #
    # async def loop(self):
    #     while True:
    #         await asyncio.sleep(3600)
    #         update = ''
    #         if 'city' in self.records:
    #             for team in self.records['city'].teams:
    #                 for cape in team.capes:
    #                     cape.decide()
    #             for team in self.records['city'].teams:
    #                 for cape in team.capes:
    #                     if cape.state == 0 or cape.state == 2:
    #                         num = random.randint(0, (len(self.records['city'].capes) - 1))
    #                         tarName = self.records['city'].capes[num]
    #                         target = self.records['city'].search(tarName)
    #                         if target.alias != cape.alias:
    #                             update += await encounter.fight(cape, target)
    #
    #             if update == '':
    #                 update = "Nothing happened."
    #             self.records['logs'] += update
    #
    #         elif 'capes' in self.records:
    #             for fighter in self.records['capes']:
    #                 fighter.decide()
    #             for cape in self.records['capes']:
    #                 if cape.state == 0 or cape.state == 2:
    #                     num = random.randint(0, (len(self.records['capes']) - 1))
    #                     target = self.records['capes'][num]
    #                     if target.alias != cape.alias:
    #                         update += await encounter.fight(cape, target)
    #
    #             if update == '':
    #                 update = "Nothing happened."
    #             self.records['logs'] += update
    #

    async def help(self, ctx, *args):
        thingy = "```%ac Commands:\n" \
                 "\tgen\tCreates a cape for you.\n" \
                 "\tstatus\tShows your cape's status.\n" \
                 "\thistory\tShows your cape's most recent history.\n" \
                 "\tfullhistory\tShows your cape's entire history.\n" \
                 "\tdelete\tPermanently deletes your cape from existence.\n" \
                 "\tfight\tMakes your cape attack another. Type an alias or their shard's name to target.\n" \
                 "\ttalk\tMakes your cape talk to another. Type an alias or their shard's name to target.\n" \
                 "\thelp\tDisplays this." \
                 "```"
        await ctx.send(thingy)