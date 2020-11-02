import random, draft, time

class Other:

    name = ''
    wants = ['puissance', 'longevity', 'access', 'executions', 'research',
                     'schools', 'priority', 'family']
    values = []
    type = 0

    def __init__(self, mem):
        self.type = len(mem['bots'])

        if self.type == 0:
            self.name = 'Bogeyman'  # Scary, targets things and doesn't back down
            self.values = [3,2,3,1,1,1,1,2]
            self.values[random.randint(0,7)] += 2
        elif self.type == 1:
            self.name = 'Goblin'  # Annoying, tries to make as many conflicts as possible, win or lose
            self.values = [3,2,1,2,1,1,1,1]
            self.values[random.randint(0,7)] += 1
            self.values[random.randint(0,7)] += 1
            self.values[random.randint(0,7)] += 1
        elif self.type == 2:
            self.name = 'Ghost'  # Obsessive, Pleads and trades for one cat or the next best things
            self.values = [1,1,2,1,1,1,1,3]
            temp = random.randint(0,7)
            self.values[temp] += 5
            if temp != 0:
                self.values[temp-1] += 3
            if temp != 7:
                self.values[temp+1] += 3
        elif self.type == 3:
            self.name = 'Fae'  # Tricky, works around players
            self.values = [1,1,2,2,2,2,1,1]
            self.values[random.randint(0,7)] += 1
            self.values[random.randint(0,7)] += 1
            self.values[random.randint(0,7)] += 1
        elif self.type == 4:
            self.name = 'Spirit'  # Tries to avoid conflict above all else
            self.values = [1,1,1,1,1,2,2,1]
            self.values[random.randint(0,7)] += 1
        elif self.type == 5:
            self.name = 'Angel'  # Tries to make as much positive karma as possible
            self.values = [3,3,3,3,3,3,3,3]
        elif self.type == 6:
            self.name = 'Lost'  # Tries to make as much positive karma as possible
            self.values = [1,1,1,1,1,1,1,1]
            self.values[random.randint(0,7)] += 1
            self.values[random.randint(0,7)] += 2
            self.values[random.randint(0,7)] += 3


    def auto_bid(self, mem):
        if (mem['to resolve'] == mem['players']) or self.name in mem['to resolve']:
            self.okay = True
            returning = []
            rank = 1
            if mem['limits'][self.name] != 0:
                rank = mem['limits'][self.name]
            check1 = 0
            check2 = 0
            check3 = 0
            check4 = 1
            choice = -1
            comp = -1
            bannedNums = []

            for cats in mem['cats']:
                if self.name in mem[cats]:
                    bannedNums.append(check3)
                check3 += 1

            for vals in self.values:
                rando = random.randint(1,6)
                temp = vals + rando
                if (temp > comp) and (check1 not in bannedNums):
                    comp = temp
                    choice = check1
                check1 += 1

            for cats in self.wants:
                if check2 == choice:
                    returning.append(cats)
                    for slot in mem[cats]:
                        if check4 == rank:
                            if slot != '':
                                rank += 1
                        check4 += 1
                    returning.append(rank)
                    break
                else:
                    check2 += 1

            return returning

    def auto_clash(self):
        if (self.type == 0) or (self.type == 1) or (self.type == 2):
            stay = True if random.random() < 0.75 else False
            return stay
        else:
            stay = True if random.random() < 0.25 else False
            return stay
