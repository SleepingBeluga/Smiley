from card import Card
import random

class Battle:
    def __init__(self, teams, stats, cap=None, channel=None):
        self.teams = {}
        for player in teams:
            self.teams[player] = Team(self, teams[player], stats, cap)
        self.stats = stats
        self.started = False
        self.channel = channel

    def start(self):
        self.started = True

    def ready(self):
        ready = True
        for i in self.teams:
            ready &= self.teams[i].ready
        return ready

    def do_turn(self):
        do_turn = True
        for team in self.teams:
            do_turn &= self.teams[team].move in ["Attack", "Defend", "Flee", "Ambush"]
        return do_turn


class Team:
    def __init__(self, battle, capes: [Card], stats, cap):
        self.pool = []
        self.team = []
        for cape in capes:
            self.team += [ BattleCape(cape, stats["classes"]) ]
        self.attack_multiplier = 1.0
        self.move = "Base"
        self.classes = stats["classes"]
        self.multipliers = stats["multipliers"]
        self.fled = False
        self.ready = False
        self.cap = cap
        self.forcing = False
        self.damage_taken = False

    def info_string(self):
        t_info = "Team strength "
        if self.cap != None:
            t_info += f"({self.quota()}/{self.cap})\n"
        else:
            t_info += f"(No Cap)\n"
        t_info += f"> Attack: {self.attack()}\n"
        t_info += f"> Defense: {self.defend()}\n"
        t_info += f"> Wits: {self.wits()}\n"
        t_info += f"> Flee: {self.flee()}\n"
        t_info += f"> Ambush: {self.ambush()}\n"
        if self.attack_multiplier > 1.0:
            t_info += f"Your ambush was successful and your next round has a **{self.attack_multiplier} attack multiplier**"
        return t_info

    def quota(self):
        # How many places have been taken on the team, weighted by tier
        quota = 0
        for i in self.team:
            tier = i.cape.tier
            if tier == "S":
                quota += 25
            elif tier == "A":
                quota += 10
            elif tier == "B":
                quota += 5
            elif tier == "C":
                quota += 1
        return quota

    def add_cape(self, cape: Card):
        bc = BattleCape(cape, self.classes)
        self.team += [ bc ]
        if self.quota() > self.cap:
            self.team.remove(bc)
            return False
        return True

    def set_move(self, move):
        self.move = move

    def new_round(self):
        self.damage_taken = False
        self.move = "Base"

    # Methods to get the current strength of various moves
    def attack(self):
        attack = 0
        for cape in self.team:
            attack += cape.attack
        return attack * self.multipliers[self.move]["Attack"] * self.attack_multiplier

    def defend(self):
        defend = 0
        for cape in self.team:
            defend += cape.defend
        return defend * self.multipliers[self.move]["Defend"]

    def wits(self):
        wits = 0
        for cape in self.team:
            wits += cape.wits
        return wits * self.multipliers[self.move]["Wits"]

    def flee(self):
        flee = 0
        for cape in self.team:
            flee += cape.flee
        return flee

    def ambush(self):
        ambush = 0
        for cape in self.team:
            ambush += cape.ambush
        return ambush

    def inflict(self, damage):
        if damage <= 0:
            return
        while damage > 3:
            damage -= 3
            cape = random.choice(self.team)
            cape.hurt(3)
            if cape.dead():
                self.pool += [ cape ]
                self.team.remove(cape)
                if len(self.team) == 0:
                    return
        cape = random.choice(self.team)
        cape.hurt(damage)
        if cape.dead():
            self.pool += [ cape ]
            self.team.remove(cape)
        self.damage_taken = True

    def make_move(self, enemy):
        # Do the regular attack!
        enemy.inflict(self.attack()-enemy.defend())

        if self.move == "Flee":

            if random.randrange(-1, int(enemy.attack())) < self.flee():
                self.fled = True
        if self.move == "Ambush":
            self.attack_multiplier = self.ambush()/enemy.wits()
            if self.attack_multiplier < 1.0:
                # Clamp it!
                self.attack_multiplier = 1.0
        else:
            self.attack_multiplier = 1.0

class BattleCape:
    def __init__(self, cape: Card, stats):
        self.cape = cape
        classes = cape.classification.split("/")

        self.defend = 0
        self.attack = 0
        self.flee = 0
        self.ambush = 0
        self.health = 0
        self.wits = 0
        multiplier = 1/len(classes)
        for i in classes:
            self.defend += stats[i]["Defend"] * multiplier
            self.attack += stats[i]["Attack"] * multiplier
            self.flee += stats[i]["Flee"] * multiplier
            self.ambush += stats[i]["Ambush"] * multiplier
            self.health += stats[i]["Health"] * multiplier
            self.wits += stats[i]["Wits"] * multiplier
        if cape.tier == "S":
            tier_multiplier = 25
        elif cape.tier == "A":
            tier_multiplier = 10
        elif cape.tier == "B":
            tier_multiplier = 5
        elif cape.tier == "C":
            tier_multiplier = 1
        self.defend *= tier_multiplier
        self.attack *= tier_multiplier
        self.flee *= tier_multiplier
        self.ambush *= tier_multiplier
        self.health *= tier_multiplier
        self.wits *= tier_multiplier

    def hurt(self, amount):
        self.health -= amount

    def dead(self):
        return self.health <= 0

