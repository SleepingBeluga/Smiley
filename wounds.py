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
            # Part was chosen/required
        else:
            part = random.choice(['Leg','Torso','Torso','Torso','Arm','Head'])
            # Roll a random target location (based on old rulebook)
        if self.any and len(self.any) and random.randint(1,4) != 4:
            pool = self.any
        # Use an 'any' result pool if you roll below a 4, if possible
        elif part == 'Torso':
            pool = self.torso
        elif part == 'Leg':
            pool = self.leg
        elif part == 'Arm':
            pool = self.arm
        elif part == 'Head':
            pool = self.head
        # Else, use a result pool specific to the part

        if pool == None or pool == []:
            pool = self.any
        # For wounds without part-specific options, use 'any'

        res = random.choice(pool)

        resstring = f'{self.severity} {self.type} ({part}) - {res.name}: {res.text}'

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
                resstring += '\n' + f'{spec.name}: {spec.text}'
        elif res.name == 'Scalded':
            resstring += '\n' + await woundd['moderate']['rend'].roll(part)
        elif res.name == 'Disintegrated':
            resstring += '\n' + await woundd['moderate'][self.type.lower()].roll(part)
            while random.randint(0,1) == 1:
                resstring += f'\nHeads. ' + await woundd['moderate'][self.type.lower()].roll(part)
            resstring += '\nTails.'
        # Specific extras

        return resstring

class AlternateWound:
    def __init__ (self, type, severity, effects):
        self.type = type
        self.severity = severity
        self.effects = effects

    async def roll(self):
        res = random.choice(self.effects)
        return f'{self.severity} {self.type} (Alt.) - {res}'

altwoundd = {}

altwoundd['lesser'] = {}
altwoundd['moderate'] = {}
altwoundd['critical'] = {}

no_eff = 'No effect.'
bleed = 'Inflict *Bleeding*.'
mangle = 'Inflict *Mangled*.'
bloody_eyes = 'Inflict *Bleeding* and *Blinded* with blood in the eyes.'
ouch_cut = 'Inflict *Pain* and *Bleeding*.'
altwoundd['lesser']['cut'] = AlternateWound('Cut', 'Lesser', (no_eff, no_eff, bleed, mangle, bloody_eyes, ouch_cut))

dis_arm = 'Arm *Disabled*.'
dis_leg = 'Leg *Disabled*, halves movement.'
bad_bleed = 'Inflict *Bleeding*, -1 Brawn until bleeding is stopped.'
drained = 'Inflict *Death Sentence* via. bleeding.'
altwoundd['moderate']['cut'] = AlternateWound('Cut', 'Moderate', (bleed, bleed, dis_arm, dis_leg, bad_bleed, drained))

lose_arm = 'Lose an arm, reattachable with surgery in a five minute window. Spent effort doubles time, multiplicative.'
lose_leg = 'Lose a leg, reattachable with surgery in a five minute window. Spent effort doubles time, multiplicative.'
bisect = 'Make a Guts roll, DC 7+. Die, bisected on failue. Spend effort for a +1 on roll.'
altwoundd['critical']['cut'] = AlternateWound('Cut', 'Critical', (lose_arm, lose_arm, lose_leg, lose_leg, bisect, bisect))

kb_five = 'Knocks back target 5\'.'
kb_ten = 'Knocks back target 10\'.'
kd = 'Knocked down, wound fades on the next rest.'
disarm = 'Target is *Disarmed*.'
delay = 'Inflict *Delay* 1 focus loss.'
altwoundd['lesser']['bash'] = AlternateWound('Bash', 'Lesser', (kb_five, kb_ten, kd, kd, disarm, delay))

kb_kd = 'Target is knocked back 10\' and knocked down.'
ouch_stat = 'Inflict *Pain*, -1 to Brawn, Athletics, or Guts, whichever is highest.'
broken = f'Broken: {ouch_stat} Inflict *Mangled*. Each time a check is failed, double duration.'
altwoundd['moderate']['bash'] = AlternateWound('Bash', 'Moderate', (kb_kd, kb_kd, kb_kd, ouch_stat, ouch_stat, broken))

pulv = 'Pulverized: Choose to lose 2 stat points or pick an intact limb/your head and lose all functionality of that part. Then roll 1d6 and repeat the process on a 2+. In advance, the target may spend effort to raise the DC by 1. (1 effort = a 3+)'
altwoundd['critical']['bash'] = AlternateWound('Bash', 'Critical', (pulv, pulv, pulv, pulv, pulv, pulv))


woundd = {}

woundd['lesser'] = {}
woundd['moderate'] = {}
woundd['critical'] = {}

any1 = WoundOption('Bleed', 'Applies *Bleed*.')
any2 = WoundOption('Slashed', 'Inflicts *Scar*.')
any3 = WoundOption('Gashed','Counts as two lesser wounds, one of these goes away on its own after a turn.')
head1 = WoundOption('Blinded','*Blinded* by blood in eyes.')
torso1 = WoundOption('Raked','Counts as two lesser wounds, one of these goes away on its own after a turn.')
arm1 = WoundOption('Hindered','*Pain*, one arm.')
leg1 = WoundOption('Hobbled','*Pain*, one leg.')
woundd['lesser']['cut'] = Wound('Cut','Lesser',[any1,any2,any3],[head1],[torso1],[arm1],[leg1])
# Lesser Cut

any1 = WoundOption('Hacked', 'If the struck part is already wounded, roll brawn again, aiming for a 4+, if successful, foe suffers an additional moderate wound (no associated effect).')
any2 = WoundOption('Butchered', 'Counts as moderate plus lesser wound, inflicts *scarring*.')
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

any1 = WoundOption('Smashed', 'Knocked to the ground. This lesser wound is temporary and goes away at the end of the target’s next turn.')
any2 = WoundOption('Bashed', 'Knocked 10’ away and back, *staggered*.')
any3 = WoundOption('Crushed','Damage becomes two temporary lesser wounds, can bypass one layer of armor with the first to deliver the second. The target heals one of the temporary wounds at the end of the next round and the round following it.')
head1 = WoundOption('Dazed','*Confused* for one round. Duration extends to three rounds if already been confused in last 24 hours.')
torso1 = WoundOption('Winded','All minor abilities with need for refreshers or a stamina cost are put on cooldown.')
arm1 = WoundOption('Disarmed','*Disarmed*.')
leg1 = WoundOption('Tripped','Knocked to the ground. This lesser wound is temporary and goes away at the end of the target’s next turn.')
woundd['lesser']['bash'] = Wound('Bash','Lesser',[any1,any2,any3],[head1],[torso1],[arm1],[leg1])
# Lesser Bash

any1 = WoundOption('Demolished', 'If struck body part is unarmored, target suffers both type-specific consequences below.')
any2 = WoundOption('Walloped', 'Thrown 10’ back or to one side and knocked down, staggered on the ensuing turn. If the individual cannot be thrown at least 5’ due to intervening obstacles, they instead suffer an added, temporary moderate bash instead (no associated effect, fades after one round).')
head1 = WoundOption('Skull Crack','Mildly *confused* for long duration, need to roll only 2+ to get bearings. Roll vs. Guts at end of encounter to shrug off, on failure, wait 1 day before rolling again, then wait 2.')
head2 = WoundOption('K.O.','Target must make additional Guts check or have all remaining wound slots filled with lesser wounds. Lesser wounds disappear at end of next turn if cape remains conscious. (No added effect)')
torso1 = WoundOption('Broken Rib','*Pain*, torso.')
torso2 = WoundOption('Internally Injured','-1 to the two lowest of the following: Brawn, Athletics, or Guts. If equal, apply in that order (Brawn first…)')
arm1 = WoundOption('Fracture Arm','Arm disabled. Roll Guts post-combat to see if it\'s broken.')
arm2 = WoundOption('Sent Flying','Thrown to one side and knocked down, *staggered* on the ensuing turn.')
leg1 = WoundOption('Fracture Leg','Leg disabled. Roll Guts post-combat to see if it\'s broken.')
leg2 = WoundOption('Sent Flying','Thrown to one side and knocked down, *staggered* on the ensuing turn.')
woundd['moderate']['bash'] = Wound('Bash','Moderate',[any1,any2],[head1,head2],[torso1,torso2],[arm1,arm2],[leg1,leg2])
# Moderate Bash

head1 = WoundOption('Brained','Target’s head cracked open. Wits, Social & Know set to 0, can’t act of own volition, *Death Sentence*.')
torso1 = WoundOption('Caved In','Chest crushed or spine broken.  Athletics, Brawn, Dex set to 0. Can think/act/communicate in limited way, but can’t move. *Death Sentence*.')
arm1 = WoundOption('Pulverized','Limb is pulverized and pinned/mashed to ground. Can’t move without losing hope of recovering limb.')
leg1 = WoundOption('Pulverized','Limb is pulverized and pinned/mashed to ground. Can’t move without losing hope of recovering limb.')
woundd['critical']['bash'] = Wound('Bash','Critical',[],[head1],[torso1],[arm1],[leg1])
# Critical Bash

any1 = WoundOption('Pricked', 'No special effect. Lesser wound fades after one round.')
any2 = WoundOption('Pierced', 'No special effect.')
any3 = WoundOption('Stuck','Attached to stabbing point. Can’t break free without being released/weapon being dropped or passing Brawn check. Loose objects must be pulled free with minor action.')
head1 = WoundOption('Blinded','*Blinded*. Lasts until attention is given.')
torso1 = WoundOption('Gouge','Counts as moderate wound, two moderate wounds if attack roll was 2 or more higher than the block/dodge. (No added effect)')
arm1 = WoundOption('Pinned','Attached to stabbing point. Can’t break free without being released/weapon being dropped or passing Brawn check. Loose objects must be pulled free with minor action.')
leg1 = WoundOption('Pinned','Attached to stabbing point. Can’t break free without being released/weapon being dropped or passing Brawn check. Loose objects must be pulled free with minor action.')
woundd['lesser']['pierce'] = Wound('Pierce','Lesser',[any1,any2,any3],[head1],[torso1],[arm1],[leg1])
# Lesser Pierce

any1 = WoundOption('Graze', 'No special effect. Treat as lesser wound.')
any2 = WoundOption('Missed Vitals', 'No other effect besides that of moderate wound.')
any3 = WoundOption('Through and Through','Take an added moderate wound. (No associated effect)')
head1 = WoundOption('Hit Head','50% chance of a ‘headshot’ that reduces Guts by 3, is otherwise an ordinary moderate wound. Helmets (armor costume feature or partial armor: head costume feature) will block a ‘headshot’ once, but will not protect the head thereafter. Pierce resistance costume feature, having one’s total health and armor exceed 5, and having large size reduce chance of the ‘headshot’ by 25% each. This reduction is additive.')
torso1 = WoundOption('Hit Vitals','Active physical stats (Brawn, Athletics, Dex) drop by 2, Guts drops by 1.')
arm1 = WoundOption('Debilitated','Limb disabled, *pain*.')
leg1 = WoundOption('Debilitated','Limb disabled, *pain*.')
woundd['moderate']['pierce'] = Wound('Pierce','Moderate',[any1,any2,any3],[head1],[torso1],[arm1],[leg1])
# Moderate Pierce

head1 = WoundOption('Headshot','Death, cannot be saved.')
torso1 = WoundOption('Heartshot','*Death Sentence*, all stats except Guts set to 0.')
arm1 = WoundOption('Limb Pierced','Limb disabled, *pain*, *scars*.')
leg1 = WoundOption('Limb Pierced','Limb disabled, *pain*, *scars*.')
woundd['critical']['pierce'] = Wound('Pierce','Critical',[],[head1],[torso1],[arm1],[leg1])
# Critical Pierce

any1 = WoundOption('Tear', 'One quality granted by armor removed as costume damaged, easily repairable.')
any2 = WoundOption('Twisted', 'Subject is weakened, Brawn penalized by 2.')
any3 = WoundOption('Ruined','Wound *scars*.')
head1 = WoundOption('Defaced','Wound *scars*.')
torso1 = WoundOption('Savaged','Subject is weakened, Brawn penalized by 2.')
arm1 = WoundOption('Sprained Arm','Limb disabled.')
leg1 = WoundOption('Sprained Leg','Limb disabled.')
woundd['lesser']['rend'] = Wound('Rend','Lesser',[any1,any2,any3],[head1],[torso1],[arm1],[leg1])
# Lesser Rend

any1 = WoundOption('Destroyed', 'Two benefits of costume on hit part are stripped away.')
any2 = WoundOption('Mangled', '*Pain*, but affects all activity/parts. Wound *scars*.')
any3 = WoundOption('Mutilated','Long-term -1 to Brawn, Athletics, or Guts. Guts check after 2 weeks to see if this heals, requires 6+, but +1 to roll per week of expert medical care. 2nd chance after 1 month, but requires 8+. *Scars*, takes twice as long to recover from.')
head1 = WoundOption('Disfigured','Long term -1 to Dex, Wits or Social, obvious scars. Guts check after 2 weeks to see if this heals, requires 6+, but +1 to roll per week of expert medical care. 2nd chance after 1 month, but requires 8+.')
tal1 = WoundOption('Scourged','*Pain*, but affects all activity/parts. Wound *scars*.')
woundd['moderate']['rend'] = Wound('Rend','Moderate',[any1,any2,any3],[head1],[tal1],[tal1],[tal1])
# Moderate Rend

any1 = WoundOption('Annihilated', 'Roll 3d7 for stats, reduce each result by 2. Roll Guts vs. death for each stat reduced to 0. Guts checks per stat after 2 weeks to see if stat damage heals, requires 6+, but +1 to roll per week of expert medical care. 2nd chances after 1 month, but requires 8+.')
woundd['critical']['rend'] = Wound('Rend','Critical',[any1],[],[],[],[])
# Critical Rend

any1 = WoundOption('Smouldering', 'Deals no damage if target is covered up. Lesser wound.')
any2 = WoundOption('Singed', 'Deals no damage if target is covered up. Lesser wound.')
any3 = WoundOption('Blistered','Additional lesser wound if not covered up.')
any4 = WoundOption('Disfigured','Wound *scars*. Additional lesser wound if not covered up.')
woundd['lesser']['burn'] = Wound('Burn','Lesser',[any1,any2,any3,any4],[],[],[],[])
# Lesser Burn

any1 = WoundOption('Blackened', 'Removes one quality from worn gear as costume is damaged.')
any2 = WoundOption('Scalded', 'Is lesser wound if subject is covered up. Otherwise, apply effects of lesser wound and moderate rend.')
any3 = WoundOption('Screaming','Subject must make Guts (morale) roll to do more than scream and flail. Suffer *pain*, affecting all rolls, for two rounds.')
any4 = WoundOption('Oh God, It Burns!','Fire/chemical sets in and continues burning. Subject rolls for another moderate burn at end of next turn unless quenched/washed away (and continue to do so each round until problem is fixed). Suffer *pain*, affecting all rolls, while burning.')
woundd['moderate']['burn'] = Wound('Burn','Moderate',[any1,any2,any3,any4],[],[],[],[])
# Moderate Burn

any1 = WoundOption('Disintegrated', 'Critical wound, roll on moderate burn chart for effect, then flip coin. If heads, repeat this action.')
woundd['critical']['burn'] = Wound('Burn','Critical',[any1],[],[],[],[])
# Critical Burn

any1 = WoundOption('Disoriented', '-2 to Wits checks. If recently shocked, wounded is effectively blinded and deafened for one round.')
any2 = WoundOption('Dazed', '*Confused* for one round. Duration extends to three rounds if recently shocked.')
any3 = WoundOption('Thrown','Knocked away and back, *staggered*. Knocked down if recently shocked.')
any4 = WoundOption('Jolted','Suffer *pain*, affecting all physical (Brawn, Athletics, Dex) rolls, for next round. Two rounds if recently shocked.')
woundd['lesser']['shock'] = Wound('Shock','Lesser',[any1,any2,any3,any4],[],[],[],[])
# Lesser Shock

any1 = WoundOption('Blitzed', 'Can only take partial actions. Taking a full round action to recuperate removes this condition. If shocked by another source, taking a full round action to recuperate only allows a Guts check to remove this condition.')
any2 = WoundOption('Paralyzed', 'Roll Guts. Subtract result from 10. Spread remaining number evenly among Brawn, Athletics and Dex in -1 penalties. Recover two points a turn, as the character chooses.')
any3 = WoundOption('Scattered','Subject is knocked down and disarmed. If recently shocked, roll 2d4 Dex checks, with each failure casting an item aside (items land within 10’, 5’ for heavier items), starting with held items, then belt, then backpack. Requires 4+.')
any4 = WoundOption('Devastated','Nearby terrain and one piece of equipment are damaged. Suffer a lesser wound appropriate to the nature of the terrain, in addition to any other effects (falling objects, pinned, etc.). If recently shocked, get knocked down as well.')
woundd['moderate']['shock'] = Wound('Shock','Moderate',[any1,any2,any3,any4],[],[],[],[])
# Moderate Shock

any1 = WoundOption('Disintegrated', 'Critical wound, roll on moderate shock chart for effect, then flip coin. If heads, repeat this action.')
woundd['critical']['shock'] = Wound('Shock','Critical',[any1],[],[],[],[])
# Critical Shock

async def roll_wound(ctx, severity, wtype, part=None):
    await ctx.send(await woundd[severity.lower()][wtype.lower()].roll(part))

class Wounds(commands.Cog):
    '''For rolling wounds
    '''
    @commands.command()
    async def lesser(self, ctx, wtype, part=None):
        '''Roll a lesser wound. Must specify type.'''
        await roll_wound(ctx, 'lesser', wtype, part)
    @commands.command()
    async def moderate(self, ctx, wtype, part=None):
        '''Roll a moderate wound. Must specify type.'''
        await roll_wound(ctx, 'moderate', wtype, part)
    @commands.command()
    async def critical(self, ctx, wtype, part=None):
        '''Roll a critical wound. Must specify type.'''
        await roll_wound(ctx, 'critical', wtype, part)

    @commands.command()
    async def cut(self, ctx, sev, part=None):
        '''Roll a cut. Must specify severity'''
        await roll_wound(ctx, sev, 'cut', part)
    @commands.command()
    async def pierce(self, ctx, sev, part=None):
        '''Roll a pierce. Must specify severity'''
        await roll_wound(ctx, sev, 'pierce', part)
    @commands.command()
    async def bash(self, ctx, sev, part=None):
        '''Roll a bash. Must specify severity'''
        await roll_wound(ctx, sev, 'bash', part)
    @commands.command()
    async def burn(self, ctx, sev, part=None):
        '''Roll a burn. Must specify severity'''
        await roll_wound(ctx, sev, 'burn', part)
    @commands.command()
    async def shock(self, ctx, sev, part=None):
        '''Roll a shock. Must specify severity'''
        await roll_wound(ctx, sev, 'shock', part)
    @commands.command()
    async def rend(self, ctx, sev, part=None):
        '''Roll a rend. Must specify severity'''
        await roll_wound(ctx, sev, 'rend', part)

    @commands.command()
    async def altwound(self, ctx, sev, wtype):
        '''Roll an alternate (module) wound. Must specify severity and type, in that order.'''
        await ctx.send(await altwoundd[sev.lower()][wtype.lower()].roll())
