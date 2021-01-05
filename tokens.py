# The bot interface for analytics
from discord.ext import commands
import discord
import random

class Bag:
    def __init__(self, text):
        positive = 0
        negative = 0
        last_index = 0
        for i in range(0, len(text)):
            if text[i] == "p":
                positive += int(text[last_index:i])
                last_index = i + 1
            elif text[i] == "n":
                negative += int(text[last_index:i])
                last_index = i + 1
            elif text[i] == "r":
                rand_val = int(text[last_index:i])
                p = random.randint(0, rand_val)
                n = rand_val - p
                positive += p
                negative += n
                last_index = i + 1
        self.bag = []
        self.bag += [True] * positive
        self.bag += [False] * negative
        self.extracted = []

    def collect(self, count):
        if count > len(self.bag):
            count = len(self.bag)
        sample = random.sample(self.bag, count)
        for i in sample:
            self.bag.remove(i)
        self.extracted += sample
        return self.extracted

    def risk(self):
        # Keep going until you've got 5 tokens
        if len(self.extracted) >= 5:
            # Can't take any more
            return self.extracted
        to_take = 5 - len(self.extracted)
        return self.collect(to_take)


class Tokens(commands.Cog):
    def __init__(self):
        self.bags = {}

    async def format_extracted(self, ctx, collected):
        positive = 0
        negative = 0
        for i in collected:
            if i:
                positive += 1
            else:
                negative += 1
        await ctx.send(f"You have collected {positive} positive tokens and {negative} negative tokens")

    @commands.command()
    async def token(self, ctx, command="", amount=""):
        """Fill a bag with tokens and extract from it! Each token is unique to the channel it is in.
            %token i XpYnZr - make the bag; X, Y and Z are replaced with the number of positive, negative and random tokens.
            %token e X - extract from the bag X tokens.
            %token r - Risk it after extracting until you have 5 tokens total
            %token empty - Empties the bag. This is also done before any insertion
        """
        if command == "":
            await ctx.send(f"```{ctx.command.help}```")
        elif command == "i":
            try:
                self.bags[ctx.channel] = Bag(amount.strip())
                await ctx.send("Bag created")
            except:
                await ctx.send("Failed to make bag correctly, make sure that it's created using XpYnZr where X, Y and Z are all numbers")
        elif command == "e":
            if ctx.channel not in self.bags:
                await ctx.send("There is no bag available")
                return
            
            try:
                amount = int(amount)
                if self.bags[ctx.channel].extracted != []:
                    if len(self.bags[ctx.channel].extracted) < 5:
                        await ctx.send("Can't extract more from the bag, but you can `%token r` to risk it!")
                    else:
                        await ctx.send("Can't extract more from the bag!")
                else:
                    if amount < -1 or amount > 4:
                        await ctx.send("Amount must be between 1 and 4 tokens!")
                    else:
                        extracted = self.bags[ctx.channel].collect(amount)
                        await self.format_extracted(ctx, extracted)
            except:
                await ctx.send("Failed to collect from the bag, make sure your value was a number")
        elif command == "r":
            if ctx.channel not in self.bags:
                await ctx.send("There is no bag available")
                return

            extracted = self.bags[ctx.channel].risk()
            await self.format_extracted(ctx, extracted)
        elif command == "empty":
            if ctx.channel in self.bags:
                del self.bags[ctx.channel]
                await ctx.send("Bag emptied")
            else:
                await ctx.send("Couldn't find a bag!")
        else:
            await ctx.send(f"Didn't recognise the command {command}")
        