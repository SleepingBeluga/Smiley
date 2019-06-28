import random, draft, time

class Other:

    name = ''
    wants = ['puissance', 'longevity', 'access', 'executions', 'research',
                     'schools', 'priority', 'family']
    values = []
    type = 0
    gen = random.Random()

    def __init__(self, mem):
        self.type = len(mem['bots'])

        if self.type == 0:
            self.name = 'Bogeyman'  # Scary, targets things and doesn't back down
            self.gen = random.Random(3475382911)
            self.values = [3,2,3,1,1,1,1,2]
            self.values[self.gen.randint(0,7)] += 2
        elif self.type == 1:
            self.name = 'Goblin'  # Annoying, tries to make as many conflicts as possible, win or lose
            self.gen = random.Random(68392756812)
            self.values = [3,2,1,2,1,1,1,1]
            self.values[self.gen.randint(0,7)] += 1
            self.values[self.gen.randint(0,7)] += 1
            self.values[self.gen.randint(0,7)] += 1
        elif self.type == 2:
            self.name = 'Ghost'  # Obsessive, Pleads and trades for one cat or the next best things
            self.gen = random.Random(123456789123)
            self.values = [1,1,2,1,1,1,1,3]
            temp = self.gen.randint(0,7)
            self.values[temp] += 5
            if temp != 0:
                self.values[temp-1] += 3
            if temp != 7:
                self.values[temp+1] += 3
        elif self.type == 3:
            self.name = 'Fae'  # Tricky, works around players
            self.gen = random.Random(8968589441234)
            self.values = [1,1,2,2,2,2,1,1]
            self.values[self.gen.randint(0,7)] += 1
            self.values[self.gen.randint(0,7)] += 1
            self.values[self.gen.randint(0,7)] += 1
        elif self.type == 4:
            self.name = 'Spirit'  # Tries to avoid conflict above all else
            self.gen = random.Random(66532577912345)
            self.values = [1,1,1,1,1,2,2,1]
            self.values[self.gen.randint(0,7)] += 1
        elif self.type == 5:
            self.name = 'Angel'  # Tries to make as much positive karma as possible
            self.gen = random.Random(737373737123456)
            self.values = [3,3,3,3,3,3,3,3]

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

            print(rank)


            for cats in mem['cats']:
                if self.name in mem[cats]:
                    bannedNums.append(check3)
                check3 += 1

            for vals in self.values:
                rando = self.gen.randint(1,6)
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

            print(returning)

            return returning

    def auto_clash(self):
        if (self.type == 0) or (self.type == 1) or (self.type == 2):
            return True
        else:
            return False
