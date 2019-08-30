# Class to represent a power and the aspects that allow it to function
import random


class Power():

    def __init__(self, dict):
        if dict == None:
            # Power will have random elements
            # For now, we will fix this
            selection = random.randrange(0, 10)
            choose = random.randrange(0,107)
            self.category = categories[selection]
            self.aspects = [Aspect(None), Aspect(None)]
            # The aspect will decide how the power functions and some generation
            # should go here
        else:
            self.category = categories[dict['cat']]
            self.aspects = []
            for thing in dict['asp']:
                self.aspects.append(Aspect(thing))

    def powJsonDict(self):
        thing = []
        for asp in self.aspects:
            thing.append(asp.aspJsonDict())
        return {'cat':self.category.num,'asp':thing}


# The base definition for a human, all power categories are derived from this
class Core():
    def __init__(self):
        # There is no category for this
        self.category = "Powerless"

    # Strikes return damage loss
    def meleeStrike(self):
        return 1.0

    def rangeStrike(self):
        # This requires some sort of weaponry, can assume they are throwing
        # rubble or something in that vein otherwise
        return 0.3

    # Talking has a few options: may try to wear down, negotiate or surrender
    def scare(self):
        # A baseline human ain't gonna be that scary
        return 0.2

    def negotiate(self):
        return 1.0

    # Returns affect to morale
    def surrender(self):
        return -0.4


# Now for all of the different possible categories
class Mover(Core):
    def __init__(self):
        self.categoryName = "Mover"
        self.num = 0


class Shaker(Core):
    def __init__(self):
        self.categoryName = "Shaker"
        self.num = 1


class Brute(Core):
    def __init__(self):
        self.categoryName = "Brute"
        self.num = 2


class Breaker(Core):
    def __init__(self):
        self.categoryName = "Breaker"
        self.num = 3


class Master(Core):
    def __init__(self):
        self.categoryName = "Master"
        self.num = 4


class Tinker(Core):
    def __init__(self):
        self.categoryName = "Tinker"
        self.num = 5


class Blaster(Core):
    def __init__(self):
        self.categoryName = "Blaster"
        self.num = 6


class Thinker(Core):
    def __init__(self):
        self.categoryName = "Thinker"
        self.num = 7


class Striker(Core):
    def __init__(self):
        self.categoryName = "Striker"
        self.num = 8


class Changer(Core):
    def __init__(self):
        self.categoryName = "Changer"
        self.num = 9


class Stranger(Core):
    def __init__(self):
        self.categoryName = "Stranger"
        self.num = 10


class Aspect():

    def __init__(self, name):
        potAspect = ['Space', 'Spark', 'Static', 'Warp', 'Transpose', 'Poison', 'Plague', 'Parasite',
                     'Puff', 'Chill', 'Metal', 'Splash', 'Glass', 'Sand', 'Flame', 'Magma', 'Lightning',
                     'Magnet', 'Push', 'Gust', 'Snow', 'Ice', 'Splash', 'Dark', 'Light', 'Plant', 'Dragon',
                     'Spout', 'Tidal', 'Glass', 'Crystal', 'Diamond', 'Rubble', 'Fissure', 'Skewer', 'Blade',
                     'Arms', 'Petal', 'Splinter', 'Wood', 'Smoke', 'Steam', 'Veil', 'Flash', 'Radiation',
                     'Ghost', 'Zombie', 'Slow', 'Rewind', 'Stop', 'Shrink', 'Acid', 'Silence', 'Babble',
                     'Sonic', 'Dazzling', 'Hologram', 'Madness', 'Explosion', 'Storm', 'Winter', 'Slick',
                     'Reflect', 'Spire', 'Spite', 'Chain', 'Forge', 'Crescent', 'Horns', 'Cross', 'Symphony',
                     'Armor', 'Heart', 'Claw', 'Blood', 'Bio', 'Dissolve', 'Arrow', 'Song', 'Sealing', 'Suffocation',
                     'Latent', 'Gravity', 'Guts', 'Switch', 'Phase', 'Rush', 'Bone', 'Machine', 'Grace', 'Remote',
                     'Black Hole', 'Disintegration', 'Lasers', 'Napalm', 'Bullet', 'Missile', 'Gun', 'Bomb',
                     'Minion', 'Friend', 'Enforcer', 'Gold', 'Silver', 'Mind', 'Sight', 'Touch', 'Scream']
        choose = random.randrange(0,107)
        if name == None:
            self.aspectName = potAspect[choose]
        else:
            self.aspectName = name

    def aspJsonDict(self):
        return self.aspectName

    # Define distance that human can cover per Ath point
    def move(self): return 10

    # Define jump height per brawn point
    def jump(self): return 1.0

    # Damage that can be caused by a given damage type
    def bash(self):   return 1.0

    def burn(self):   return 0.0

    def cut(self):    return 0.3

    def rend(self):   return 0.0

    def shock(self):  return 0.0

    def pierce(self): return 0.1

    # Damage modifier for variable range attacks
    def melee(self):        return 1.0

    def midrangehit(self):  return 1.0

    def longrangehit(self): return 0.0

    # The ability to slam enemies into the ground
    def slam(self): return 0.0

    # The ability to fly
    def fly(self): return 0.0


class Knife(Aspect):
    def __init__(self):
        # This is a tool!
        self.aspectName = "Knife"

    def cut(self):    return 1.0

    def pierce(self): return 0.8


categories = {
    0: Mover(),
    1: Shaker(),
    2: Brute(),
    3: Breaker(),
    4: Master(),
    5: Tinker(),
    6: Blaster(),
    7: Thinker(),
    8: Striker(),
    9: Changer(),
    10: Stranger()
}  # No Trump as of now

aspects = [
    "Dodge",  # Mover
    "Thorn",  # Shaker
    "Tar",  # Shaker
    "Harden",  # Brute
    "Recharge",  # Brute
    "Shift",  # Breaker
    "Duplicate",  # Master
    "Electric",  # Tinker - making this up as an item they must have
    "Shrapnel",  # Blaster
    "Ruin",  # Thinker
    "Annihilate",  # Striker
    "Repair",  # Changer
    "Gouge",  # Changer
    "Cling",  # Changer
    "Consume",  # Changer - speak to shout attack that confuses
    "Demoralise",  # Stranger
    "Nullify"  # Stranger
]

