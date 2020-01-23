from discord.ext import commands
import random

class Snacks(commands.Cog):
    '''For snacks
    '''
    def __init__(self):
        self.snacks = {}
        self.contributors = {}
        self.snackers = {}
        self.eatings = [
            "chows down on some",
            "gorges themself on",
            "can't get enough of",
            "chomps on",
            "guzzles down some",
            "delicately partakes in some",
            "loudly masticates",
            "eats a whole"
        ]
        self.offers = {}

    async def total_snacks(self):
        count = 0
        for i in self.snacks:
            count += self.snacks[i]
        return count

    async def output_consumption(self, ctx, snack, snacker):
        await ctx.send("{} {} {}".format(ctx.author.name, random.choice(self.eatings), snack))

    async def consume(self, ctx, snack, snacker):
        if snack not in self.snacks:
            await ctx.send("There are no {} in the pile".format(snack))
        else:
            if self.snacks[snack] == 1:
                del self.snacks[snack]
            else:
                self.snacks[snack] -= 1
            if snacker not in self.snackers:
                self.snackers[snacker] = {}
            if snack not in self.snackers[snacker]:
                self.snackers[snacker][snack] = 0
            
            self.snackers[snacker][snack] += 1
            await self.output_consumption(ctx,snack,snacker)

    async def add(self, snack, contributor, count=1):
        if snack not in self.snacks:
            self.snacks[snack] = 0
        self.snacks[snack] += count
        if contributor not in self.contributors:
            self.contributors[contributor] = {}
        if snack not in self.contributors[contributor]:
            self.contributors[contributor][snack] = 0
        self.contributors[contributor][snack] += count

    async def list_snacks(self, ctx):
        if len(self.snacks) == 0:
            await ctx.send("There are no snacks in the pile!")
            return
        snacks = ""
        for i in self.snacks:
            snacks += "{} {}, ".format(self.snacks[i], i)
        snacks = snacks[:-2]
        await ctx.send("In the pile there is\n```{}```".format(snacks))

    @commands.command()
    async def snack(self, ctx, *args):
        '''Add snacks to the pile, or eat em up.
        
        Usage:  %snack add [snack name][*number of snacks]  - Add some snacks to the pile
                %snack [snack name]                         - Eat a snack
                %snack [eat] [snack name]                   - Eat a snack ([eat] is optional)
                %snack search                               - Search the snack pile
                %snack offer @<player> [snack name]         - Offer someone some snacks (reserves the snack)
                %snack accept [snack name]                  - Accept a specific snack, takes first offer
                %snack reject [snack name]                  - Reject a specific snack, rejects first offer
                %snack offers [mine/all]                    - Produces a list of offers and reserved snacks
        '''
        if len(args) == 0 or (len(args) == 1 and args[0] == "eat"):
            # Eat a snack!
            if len(self.snacks) == 0:
                await ctx.send("Sorry all the snacks are gone!")
            else:
                snack = random.choice(list(self.snacks.keys()))
                await self.consume(ctx, snack, ctx.author)
        elif args[0] == "add":
            if len(args) == 1:
                await ctx.send("Please specify a snack to add to the pile")
            else:
                snack = args[1]
                for i in args[2:]:
                    snack += " " + i
                if "*" in snack:
                    snack, count = snack.split("*")
                    count = int(count.strip())
                else:
                    count = 1
                await self.add(snack, ctx.author, count)
        elif args[0] == "search":
            await self.list_snacks(ctx)
        elif args[0] == "offer":
            await ctx.send("Not yet implemented")
        elif args[0] == "accept":
            await ctx.send("Not yet implemented")
        elif args[0] == "reject":
            await ctx.send("Not yet implemented")
        elif args[0] == "offers":
            await ctx.send("Not yet implemented")
        else:
            index = 0
            if args[index] == "eat":
                index += 1
            snack = args[index]
            for i in args[index+1:]:
                snack += " " + i
            await self.consume(ctx, snack, ctx.author)
