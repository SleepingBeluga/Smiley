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

    async def roll (self, part=None):
        if part:
            part = part.capitalize()
            if not part in ['Leg','Torso','Arm','Head']:
                return "I don't know that body part."
        if not part:
            part = random.choice(['Leg','Torso','Torso','Torso','Arm','Head'])
            # Roll a random target location (based on old rulebook)
        else:
            part = part.capitalize()
            # Part was chosen/required
        if not random.randint(1,4) == 4:
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
        # For wounds without part-specific options, use 'any'

        while pool == None or pool == []:
            pool = random.choice([self.head,self.torso,self.arm,self.leg])
        # If 'any' is chosen and is empty, randomly choose another

        res = random.choice(pool)

        resstring = f'{self.severity} {self.type} ({part}): ```{res.name}: {res.text}```'

        if res.name == 'Demolished':
            if part == 'Torso':
                pool = self.torso
            elif part == 'Leg':
                pool = self.leg
            elif part == 'Arm':
                pool = self.arm
            elif part == 'Head':
                pool = self.head
            for spec in pool:
                resstring += '\n' + f'```{spec.name}: {spec.text}```'
        # Specific extras

        return resstring

woundd = {}

woundd['lesser'] = {}
woundd['moderate'] = {}
woundd['critical'] = {}

any1 = WoundOption('Bleed', 'Applies *Bleed*.')
any2 = WoundOption('Slashed', 'Inflicts *Scar*.')
any3 = WoundOption('Gashed','Counts as two minor wounds, one of these goes away on its own after a turn.')
head1 = WoundOption('Blinded','*Blinded* by blood in eyes.')
torso1 = WoundOption('Raked','Counts as two minor wounds, one of these goes away on its own after a turn.')
arm1 = WoundOption('Hindered','*Pain*, one arm.')
leg1 = WoundOption('Hobbled','*Pain*, one leg.')
woundd['lesser']['cut'] = Wound('Cut','Lesser',[any1,any2,any3],[head1],[torso1],[arm1],[leg1])
# Lesser Cut

any1 = WoundOption('Hacked', 'If the struck part is already wounded, roll brawn again, aiming for a 4+, if successful, foe suffers an additional moderate wound (no associated effect).')
any2 = WoundOption('Butchered', 'Counts as moderate plus minor wound, inflicts *scarring*.')
any3 = WoundOption('Slice','Subject provokes an attack of opportunity from those nearby/from assailant.')
head1 = WoundOption('Dice','Subject provokes an attack of opportunity from those nearby/from assailant.')
torso1 = WoundOption('Tear','Guts reduced by 1. Does not impact maximum wounds, does impact rolls.')
arm1 = WoundOption('Lacerated','Limb *disabled*. *Disarmed*.')
leg1 = WoundOption('Hamstrung','*Disabled* leg.')
woundd['moderate']['cut'] = Wound('Cut','Moderate',[any1,any2,any3],[head1],[torso1],[arm1],[leg1])
# Moderate Cut

head1 = WoundOption('Decapitation','Death.')
torso1 = WoundOption('Bisection','Counts as one critical wound and 1 moderate wound for every difference in attack roll vs. the defense roll.')
arm1 = WoundOption('Dismembered','Loss of arm.')
leg1 = WoundOption('Dismembered','Loss of leg.')
woundd['critical']['cut'] = Wound('Cut','Critical',[],[head1],[torso1],[arm1],[leg1])
# Critical Cut

any1 = WoundOption('Smashed', 'Knocked to the ground. This minor wound is temporary and goes away at the end of the target’s next turn.')
any2 = WoundOption('Bashed', 'Knocked 10’ away and back, *staggered*.')
any3 = WoundOption('Crushed','Damage becomes two temporary minor wounds, can bypass one layer of armor with the first to deliver the second. The target heals one of the temporary wounds at the end of the next round and the round following it.')
head1 = WoundOption('Dazed','*Confused* for one round. Duration extends to three rounds if already been confused in last 24 hours.')
torso1 = WoundOption('Winded','All minor abilities with need for refreshers or a stamina cost are put on cooldown.')
arm1 = WoundOption('Disarmed','*Disarmed*.')
leg1 = WoundOption('Tripped','Knocked to the ground. This minor wound is temporary and goes away at the end of the target’s next turn.')
woundd['lesser']['bash'] = Wound('Bash','Lesser',[any1,any2,any3],[head1],[torso1],[arm1],[leg1])
# Lesser Bash

any1 = WoundOption('Demolished', 'If struck body part is unarmored, target suffers both type-specific consequences below.')
any2 = WoundOption('Walloped', 'Thrown 10’ back or to one side and knocked down, staggered on the ensuing turn. If the individual cannot be thrown at least 5’ due to intervening obstacles, they instead suffer an added, temporary moderate bash instead (no associated effect, fades after one round).')
head1 = WoundOption('Skull Crack','Mildly *confused* for long duration, need to roll only 2+ to get bearings. Roll vs. Guts at end of encounter to shrug off, on failure, wait 1 day before rolling again, then wait 2.')
head2 = WoundOption('K.O.','Target must make additional Guts check or have all remaining wound slots filled with minor wounds.  Minor wounds disappear at end of next turn if cape remains conscious. (No added effect)')
torso1 = WoundOption('Broken Rib','*Pain*, torso.')
torso2 = WoundOption('Internally Injured','-1 to the two lowest of the following: Brawn, Athletics, or Guts. If equal, apply in that order (Brawn first…)')
arm1 = WoundOption('Fracture Arm','Arm disabled. Roll Guts post-combat to see if it\'s broken.')
arm2 = WoundOption('Sent Flying','Thrown to one side and knocked down, *staggered* on the ensuing turn.')
leg1 = WoundOption('Fracture Leg','Leg disabled. Roll Guts post-combat to see if it\'s broken.')
leg2 = WoundOption('Sent Flying','Thrown to one side and knocked down, *staggered* on the ensuing turn.')
woundd['moderate']['bash'] = Wound('Bash','Moderate',[any1,any2],[head1,head2],[torso1,torso2],[arm1,arm2],[leg1,leg2])
# Moderate Bash


async def roll_wound(ctx, severity, wtype, part=None):
    await ctx.send(await woundd[severity.lower()][wtype.lower()].roll(part))

class WoundCog(commands.Cog):
    '''For rolling wounds
    '''
    @commands.command()
    async def lesser(self, ctx, wtype, part=None):
        await roll_wound(ctx, 'lesser', wtype, part)
    @commands.command()
    async def moderate(self, ctx, wtype, part=None):
        await roll_wound(ctx, 'moderate', wtype, part)
    @commands.command()
    async def critical(self, ctx, wtype, part=None):
        await roll_wound(ctx, 'critical', wtype, part)

    @commands.command()
    async def cut(self, ctx, sev, part=None):
        await roll_wound(ctx, sev, 'cut', part)
    @commands.command()
    async def pierce(self, ctx, sev, part=None):
        await roll_wound(ctx, sev, 'pierce', part)
    @commands.command()
    async def bash(self, ctx, sev, part=None):
        await roll_wound(ctx, sev, 'bash', part)
    @commands.command()
    async def burn(self, ctx, sev, part=None):
        await roll_wound(ctx, sev, 'burn', part)
    @commands.command()
    async def shock(self, ctx, sev, part=None):
        await roll_wound(ctx, sev, 'shock', part)
    @commands.command()
    async def rend(self, ctx, sev, part=None):
        await roll_wound(ctx, sev, 'rend', part)
