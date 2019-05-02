from discord.ext import commands
import random, asyncio

class WoundOption:
    '''A possible result from a Wound
    '''
    def __init__ (self, name, text):
        self.name = name
        self.text = text

class Wound:
    '''A class of wound (e.g. lesser cut) with lists of results
    '''
    def __init__ (self, type, severity, anyopt,
                        headopt, torsoopt, armopt, legopt):
        self.type = type
        # One of 'Cut', 'Bash', 'Pierce', 'Burn', 'Shock', 'Rend'

        self.severity = severity
        # One of 'Lesser', 'Moderate', 'Critical'

        self.any = anyopt
        self.head = headopt
        self.torso = torsoopt
        self.arm = armopt
        self.leg = legopt
        # Lists of WoundOptions for different locations

    async def roll (self, part = None):
        if not part:
            part = random.choice(['Leg','Torso','Torso','Torso','Arm','Head'])
            # Roll a random target location (based on old rulebook)
        else:
            part = part.capitalize()
            # Part was chosen/required
        if random.randint(1,4) == 4:
            pool = self.any
        # Use an 'any' result pool

        elif part == 'Torso':
            pool = self.torso
        elif part == 'Leg':
            pool = self.leg
        elif part == 'Arm':
            pool = self.arm
        elif part == 'Head':
            pool = self.head
        # Use a result pool specific to the part

        if pool == None or pool == []:
            pool = self.any
        # For wounds without part-specific options, always use 'any'

        res = random.choice(pool)

        resstring = f'{self.severity} {self.type} ({part}): ```{res.name}: {res.text}```'

        return resstring

woundd = {}

woundd['lesser'] = {}
woundd['moderate'] = {}
woundd['critical'] = {}

bleed = WoundOption('Bleed', 'Applies *Bleed*.')
slashed = WoundOption('Slashed', 'Inflicts *Scar*.')
gashed = WoundOption('Gashed','Counts as two minor wounds, one of these goes away on its own after a turn.')
blinded = WoundOption('Blinded','*Blinded* by blood in eyes.')
raked = WoundOption('Raked','Counts as two minor wounds, one of these goes away on its own after a turn.')
hindered = WoundOption('Hindered','*Pain*, one arm.')
hobbled = WoundOption('Hobbled','*Pain*, one leg.')
woundd['lesser']['cut'] = Wound('Cut','Lesser',[bleed,slashed,gashed],[blinded],[raked],[hindered],[hobbled])
# Lesser Cut

async def roll_wound(ctx, severity, wtype,):
    await ctx.send(await woundd[severity.lower()][wtype.lower()].roll())

class WoundCog(commands.Cog):
    '''For rolling wounds
    '''
    @commands.command()
    async def lesser(self, ctx, wtype):
        await roll_wound(ctx, 'lesser', wtype)
    @commands.command()
    async def moderate(self, ctx, type):
        await roll_wound(ctx, 'moderate', wtype)
    @commands.command()
    async def critical(self, ctx, type):
        await roll_wound(ctx, 'critical', wtype)

    @commands.command()
    async def cut(self, ctx, sev):
        pass
    @commands.command()
    async def pierce(self, ctx, sev):
        pass
    @commands.command()
    async def bash(self, ctx, sev):
        pass
    @commands.command()
    async def burn(self, ctx, sev):
        pass
    @commands.command()
    async def shock(self, ctx, sev):
        pass
    @commands.command()
    async def rend(self, ctx, sev):
        pass
