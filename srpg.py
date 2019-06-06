from discord.ext import commands
import random

class SRPG(commands.Cog):
    '''Implements tables from Wildbow's SRPG document.
    '''
    def __init__(self):
        self.person_list = ['Angry (Aggressive x Conflict Driven)', 'Wild (Aggressive x Explore/Mobility Driven)', 'Impulsive (Aggressive x Activity/Creation Driven)', 'Critical (Aggressive x Perception Driven)', 'Harsh (Aggressive x People Focused)', 'Driven (Aggressive x Plan/Dream Focused)', 'Tough (Aggressive x Response Driven)', 'Brave (Assertive x Conflict Driven)', 'Adventurous (Assertive x Explore/Mobility)', 'Creative (Assertive x Activity/Creation Driven)', 'Stubborn (Assertive x Perception Driven)', 'Confident (Assertive x People Focused)', 'Contemplative (Assertive x Plan/Dream Focused)', 'Serious (Assertive x Response Driven)', 'Vicious (Indirect x Conflict Driven)', 'Distant (Indirect x Explore/Mobility Driven)', 'Unpredictable (Indirect x Activity/Creation Driven)', 'Wary (Indirect x Perception Driven)', 'Joking (Indirect x People Focused)', 'Devious (Indirect x Plan/Dream Focused)', 'Guarded (Indirect x Response Driven)', 'Cold (Passive x Conflict Driven)', 'Detached (Passive x Explore/Mobility Driven)', 'Ambitious (Passive x Activity/Creation Driven)', 'Diligent (Passive x Perception Driven)', 'Quiet (Passive x People Focused)', 'Introspective (Passive x Plan/Dream Focused)', 'Morose (Passive x Response Driven)']

        self.lean_list = ['Left', 'Right', 'Lower', 'Upper', 'Race', 'Faith']

        self.dispo_list = ['Hero (Heroic x Heroic)', 'AntiVillain (Heroic x Villain)', 'Freelance Hero (Hero x Merc)', 'Corporate Hero (Hero x Sponsor)', 'Activist ({random.choice(lean_list)}) (Hero x Believer)', 'Vigilante (Hero x Violent)', 'Underdog (Hero x F-List)', 'Shining Star (Hero x Solo)', 'AntiVillain (Villain x Hero)', 'Villain (Villain x Villain)', 'Blackguard (Villain x Merc)', 'Blacklist (Villain x Sponsor)', 'Malcontent ({random.choice(lean_list)}) (Villain x Believer)', 'Monster (Villain x Violent)', 'Vermin (Villain x F-List)', 'Dark Star (Villain x Solo)', 'Freelance Hero (Merc x Hero)', 'Blackguard (Merc x Villain)', 'Merc (Merc x Merc)', 'Soldier of Fortune (Merc x Sponsor)', 'Leggionaire ({random.choice(lean_list)}) (Merc x Believer)', 'Marauder (Merc x Violent)', 'Money Grubber (Merc x F-List)', 'Solo Operator (Merc x Solo)', 'Activist ({random.choice(lean_list)}) (Believer x Hero)', 'Malcontent ({random.choice(lean_list)}) (Believer x Villain)', 'Legionnaire ({random.choice(lean_list)}) (Believer x Merc)', 'Supplicant ({random.choice(lean_list)}) (Believer x Sponsor)', 'True Believer ({random.choice(lean_list)}) (Believer x Believer)', 'Maniac ({random.choice(lean_list)}) (Believer x Violent)', 'Loon ({random.choice(lean_list)}) (Believer x F-List)', 'Solitary Voice ({random.choice(lean_list)}) (Believer x Solo)', 'Vigilante (Violent x Heroic)', 'Monster (Violent x Villain)', 'Marauder (Violent x Merc)', 'Hatchet Man (Violent x Sponsor)', 'Maniac ({random.choice(lean_list)}) (Violent x Believer)', 'Killer (Violent x Violent)', 'Feral (Violent x F-List)', 'Lone-Wolf (Violent x Solo)', 'Underdog (F-List x Heroic)', 'Vermin (F-List x Villain)', 'Money Grubber (F-List x Merc)', 'Thrall (F-List x Sponsor)', 'Loon ({random.choice(lean_list)}) (F-List x Believer)', 'Feral (F-List x Violent)', 'Scum (F-List x F-List)', 'Pariah (F-List x Solo)', 'Shining Star (Solo x Heroic)', 'Dark Star (Solo x Villain)', 'Solo Operator (Solo x Merc)', 'Agent (Solo x Sponsor)', 'Solitary Voice ({random.choice(lean_list)}) (Solo x Believer)', 'Lone Wolf (Solo x Violent)', 'Pariah (Solo x F-List)', 'Independent (Solo x Solo)']

        self.arche_list = ['Champion', 'Lancer', 'Fury', 'Gladiator', 'Bully', 'Master', 'Titan', 'Raider', 'Athlete', 'Hunter', 'Stalker', 'Wayfarer', 'Explorer', 'Interceptor', 'Assassin', 'Scoundrel', 'Ace', 'Marksman', 'Broker', 'Craftsman', 'Packrat', 'Guard', 'Lookout', 'Monitor', 'Scout', 'Handler', 'Investigator', 'Sentinel', 'Boss', 'Lead', 'Playboy', 'Psychologist', 'Politician', 'Manipulator', 'Holdout', 'Expert', 'Pioneer', 'Polymath', 'Schemer', 'Tactician', 'Genius', 'Architect', 'Juggernaut', 'Horse', 'Tough', 'Survivor', 'Icon', 'Pillar', 'Indomitable']

    @commands.command()
    async def gensrpg(self, ctx):
        to_send = f"**Disposition**: {random.choice(self.dispo_list)}, **Personality/Archetype**: {random.choice(self.person_list)}, {random.choice(self.arche_list)}"

        while '{random.choice(lean_list)}' in to_send:
            to_send = to_send.replace('{random.choice(lean_list)}',random.choice(self.lean_list),1)
        # Hacky, sorry!

        await ctx.send(to_send)
