from discord.ext import commands
import discord, sheets
import random, datetime, difflib, asyncio
from card import Card
from battle import Battle

async def longpm(ctx, content):
    if len(content) > 1990:
        found_too_long = True
        i = content.find('```')
        if i >= 0:
            msgs = content[:i].split('\n') + [content[i:]]
        else:
            msgs = content.split()
        while found_too_long:
            found_too_long = False
            for i, msg in enumerate(msgs):
                if len(msg) > 1990:
                    found_too_long = True
                    msgs[i] = msg[:1990]
                    msgs.insert(i+1,msg[1990:])
    else:
        msgs = [content]
    for msg in msgs:
        await ctx.author.send(msg)

class Capes(commands.Cog):

    def __init__(self):
        self.capelist = []
        self.trading = {}
        self.claims = {}
        self.bonus_claim = {}
        self.trades = {}
        self.triggers = {} # Completed reviews
        self.reviewing = {} # Reviews in progress
        self.battle_stats = {}
        self.battles = {}
        self.cached = False
        self.pause = False
        self.lock = asyncio.Lock()

    async def set_local_cache(self):
        await self.load_capes()
        await self.load_owners()
        await self.load_triggers()
        await self.load_battle_stats()
        self.battles = {}
        self.cached = True

    async def load_capes(self):
        capes = (await sheets.trading_capes())
        for cape in capes:
            new_cape = Card(*cape)
            self.capelist += [ new_cape ]

    async def load_owners(self):
        card_owns = (await sheets.owned_cards())
        for card in card_owns:
            if not card[0] in self.trading:
                self.trading[card[0]] = []
            self.trading[card[0]] += [self.capelist[int(card[1])]]

    async def load_triggers(self):
        self.triggers = (await sheets.waiting_triggers())

    async def load_battle_stats(self):
        self.battle_stats = (await sheets.get_battle_stats())

    async def random_claim(self, ctx, claimer_id):
        # Check if this person has already claimed today
        day = datetime.datetime.now().day
        if not day in self.claims:
            self.claims = {day: []}

        if claimer_id in self.claims[day] and claimer_id not in self.bonus_claim:
            if datetime.datetime.now().hour == 23:
                timeleft = "{} minutes".format(60-datetime.datetime.now().minute)
            else:
                timeleft = "{} hours".format(24-datetime.datetime.now().hour)
            await ctx.send("You have already made your daily claim! Next claim available in {}".format(timeleft))
            return

        amount = 0
        if claimer_id in self.bonus_claim:
            await ctx.send("Claiming {} bonus cards".format(self.bonus_claim[claimer_id]))
            amount += self.bonus_claim[claimer_id]
        if not claimer_id in self.claims[day]:
            amount += 1

        total = 0
        for i in self.capelist:
            if i.tier == "C":
                total += 27
            elif i.tier == "B":
                total += 9
            elif i.tier == "A":
                total += 3
            elif i.tier == "S":
                total += 1
        selectedValues = []
        for i in range(0, amount):
            selectedValues += [ random.randrange(0,total) ]
        collected = ""
        cards = []
        for selectedValue in selectedValues:
            counting = 0
            cape = None
            for i in self.capelist:
                if i.tier == "C":
                    val_to_add = 27
                elif i.tier == "B":
                    val_to_add = 9
                elif i.tier == "A":
                    val_to_add = 3
                elif i.tier == "S":
                    val_to_add = 1
                if selectedValue >= counting and selectedValue < counting + val_to_add:
                    cape = i
                    break
                else:
                    counting += val_to_add
            # If we didn't find a cape, make it the last one!
            if cape == None:
                cape = self.capelist[-1]
            if not claimer_id in self.trading:
                self.trading[claimer_id] = []
            self.trading[claimer_id] += [cape]
            cards += [self.capelist.index(cape)]
            collected += cape.name + ", "
        await sheets.gain_cards(claimer_id, cards)
        await ctx.send("You gained the card for {}".format(collected[:-2]))
        if not claimer_id in self.claims[day]:
            self.claims[day] += [ claimer_id ]
        if claimer_id in self.bonus_claim:
            del self.bonus_claim[claimer_id]

    async def view_card(self, ctx, cape):
        message =   "**{}** ({})\n".format(cape.name, cape.classification)
        if cape.tagline != "":
            message += "> ***{}***\n".format(cape.tagline)
        message +=  "> Tier: **{}**\n".format(cape.tier)
        if cape.civ != "Unknown":
            message +=  "> Civilian Identity: ||{}||\n".format(cape.civ)
        else:
            message +=  "> Civilian Identity: {}\n".format(cape.civ)
        message +=  "> Power: {}\n".format(cape.power)
        message +=  "> Campaign: **{}**, {}\n".format(cape.campaign, cape.pc)
        message +=  "> Affiliation: {}, {}".format(cape.affiliation, cape.alignment)
        await ctx.send(message)

    async def messagify_ownership(self, user, c_list, c_filter = ""):
        if c_filter != "":
            c_filter = " **{}** ".format(c_filter)
        owned_cards = 0
        owned = {}
        if user in self.trading:
            for i in self.trading[user]:
                if i in c_list:
                    owned_cards += 1
                    if not i.name in owned:
                        owned[i.name] = 0
                    owned[i.name] += 1
        initial = "You own {}{} cards\n".format(owned_cards,c_filter[:-1])
        m_index = 0
        messages = ["> "]
        for i in owned:
            messages[m_index] += i
            if owned[i] > 1:
                messages[m_index] += "x{}".format(owned[i])
            messages[m_index] += ", "
            if len(messages[m_index]) > 1800: # Don't let it get too long
                messages[m_index] = messages[m_index][:-1]
                m_index += 1
                messages += ["> "]
        messages[m_index] = messages[m_index][:-2]

        messages[0] = "{}{}Cards collected {}/{}\n{}".format(initial, c_filter,len(owned),len(c_list),messages[0])
        return messages

    async def view(self, ctx, owner, *args):
        if not owner in self.trading:
            await ctx.send("You own no cards")
            return
        if len(args) == 0:
            # Let's display all cards
            messages = (await self.messagify_ownership(owner, self.capelist))
            for i in messages:
                await ctx.send(i)
        else:
            name = ""
            for i in args:
                name += "{} ".format(i)
            name = name[:-1]
            capes_owned = []
            for i in self.trading[owner]:
                if i.name.lower() == name.lower():
                    return await self.view_card(ctx, i)
                if not i.name in capes_owned:
                    capes_owned += [ i.name ]

            closestCapes = difflib.get_close_matches(name, capes_owned)
            if len(closestCapes) > 1:
                await ctx.send("That cape could not be found, did you mean one of: " + closestCapes)
            elif len(closestCapes) == 1:
                await ctx.send("That cape could not be found, did you mean " + closestCapes[0])
            else:
                await ctx.send("You don't own that that card!")

    async def get_cape(self, name):
        for i in self.capelist:
            if i.name.lower() == name.lower():
                return i

    async def at_to_id(self, at):
        at = at.replace("<", "")
        at = at.replace("@", "")
        at = at.replace("!", "")
        at = at.replace(">", "")
        return at.strip()

    async def has_cards(self, user, cards):
        # Cards comes in as an array of strings
        if len(cards) == 0:
            # You always have some of nothing!
            return True
        if user not in self.trading:
            # Can't have the required cards if they have nothing
            return False
        card_dict = {}
        for i in self.trading[user]:
            if not i.name.lower() in card_dict:
                card_dict[i.name.lower()] = 0
            card_dict[i.name.lower()] += 1
        for i in cards:
            if i.lower() in card_dict and card_dict[i.lower()] > 0:
                card_dict[i.lower()] -= 1
            else:
                return False

        return True


    async def trade(self, ctx, user, subaction, *args):
        if len(args) > 0 and (await self.at_to_id(args[0])) == user:
            await ctx.send("Trading with yourself just don't make sense...")
            return
        if subaction ==  "help":
            message = "**Trading commands:**\n```"
            message += "%tc trade offer @username [Card you have, Another card you have] [Card they have, another card they have] - Make an offer to someone\n"
            message += "%tc trade view - View all open trades you have\n"
            message += "%tc trade view @username - View an offer someone has made/you have made to them\n"
            message += "%tc trade cancel @username - Cancel a trade you have with someone\n"
            message += "%tc trade reject @username - Reject a trade someone has made to you\n"
            message += "%tc trade accept @username - Accept an open trade you have with someone\n"
            message += "```"
            await ctx.send(message)
        elif subaction == "offer":
            if args[0] == "help":
                message = "Specify who you want to trade with, your offer in parenthesis, then what you want back\n"
                message += "`    %tc trade offer @someperson [My Card, My Other Card] [Their Card, Another of their cards, a third card of theirs]`"
                await ctx.send(message)
                return

            # First arg will be a person
            request_to_id = (await self.at_to_id(args[0]))
            # Make sure an existing offer with them doesn't already exist
            if (user in self.trades and request_to_id in self.trades[user]) or (request_to_id in self.trades and user in self.trades[request_to_id]):
                await ctx.send("Already have a trade proposed with them! Will have to cancel or reject trade to start a new one.")
                await self.trade(ctx, user, "view", *args[0:1])
                return
            offers = ""
            for i in args[1:]:
                offers += i + " "

            offer, desire, nil = offers.split("]")
            nil, offer = offer.split("[")
            offer = offer.split(",")
            nil, desire = desire.split("[")
            desire = desire.split(",")

            if len(offer) == 1 and offer[0] == "":
                offer = []
            if len(desire) == 1 and desire[0] == "":
                desire = []
            if len(offer) == 0 and len(desire) == 0:
                await ctx.send("You can't trade nothing for nothing, that's just silly")
                return

            for i in range(0, len(offer)):
                offer[i] = offer[i].strip()

            for i in range(0, len(desire)):
                desire[i] = desire[i].strip()

            # Check whether they even both have the required cards
            if not (await self.has_cards(user, offer)):
                await ctx.send("You do not have the cards required to trade!")
            elif not (await self.has_cards(request_to_id, desire)):
                await ctx.send("They don't have the cards you want!")
            else:
                if not user in self.trades:
                    self.trades[user] = {}
                self.trades[user][request_to_id] = [offer, desire]
                await ctx.send("Offer made")
        elif subaction == "view":
            if len(args) == 0:
                open_offers = ""
                for i in self.trades:
                    if user == i:
                        for j in self.trades[i]:
                            open_offers += "<@!{}>, ".format(j)
                    elif user in self.trades[i]:
                        open_offers += "<@!{}>, ".format(i)
                if open_offers == "":
                    await ctx.send("Don't have any open trades")
                else:
                    await ctx.send("Have open trades with {}".format(open_offers[:-2]))
                return
            request_to_id = (await self.at_to_id(args[0]))
            if user in self.trades and request_to_id in self.trades[user]:
                offer = self.trades[user][request_to_id][0]
                o = "["
                for i in offer:
                    o += i + ", "
                o = o[:-2] + "]"
                if len(offer) == 0:
                    o = "nothing"

                desire = self.trades[user][request_to_id][1]
                d = "["
                for i in desire:
                    d += i + ", "
                d = d[:-2] + "]"
                if len(desire) == 0:
                    d = "nothing"

                message = "You offered to trade {} for their {}\nYou can cancel this trade with `%tc trade cancel @username`".format(o, d)
                await ctx.send(message)
            elif request_to_id in self.trades and user in self.trades[request_to_id]:
                offer = self.trades[request_to_id][user][0]
                o = "["
                for i in offer:
                    o += i + ", "
                o = o[:-2] + "]"
                if len(offer) == 0:
                    o = "nothing"

                desire = self.trades[request_to_id][user][1]
                d = "["
                for i in desire:
                    d += i + ", "
                d = d[:-2] + "]"
                if len(desire) == 0:
                    d = "nothing"

                message = "They offered to trade {} for your {}\nYou can reject this trade with `%tc trade reject @username`".format(o, d)
                await ctx.send(message)
            else:
                await ctx.send("Found no trade offer between the two of you")
        elif subaction == "accept":
            request_to_id = (await self.at_to_id(args[0]))
            if request_to_id in self.trades and user in self.trades[request_to_id]:
                offer = self.trades[request_to_id][user][0]
                desire = self.trades[request_to_id][user][1]
                if not (await self.has_cards(request_to_id, offer)):
                    await ctx.send("They no longer have the required cards! Trade cancelled")
                    del self.trades[request_to_id][user]
                elif not (await self.has_cards(user, desire)):
                    await ctx.send("You no longer have the required cards! Trade cancelled")
                    del self.trades[request_to_id][user]
                else:
                    offer_indexes = []
                    for i in offer:
                        cape = await self.get_cape(i)
                        self.trading[request_to_id].remove(cape)
                        self.trading[user] += [cape]
                        offer_indexes += [ self.capelist.index(cape) ]

                    await sheets.move_card_owner(request_to_id, user, offer_indexes)

                    desire_indexes = []
                    for i in desire:
                        cape = await self.get_cape(i)
                        self.trading[user].remove(cape)
                        self.trading[request_to_id] += [cape]
                        desire_indexes += [ self.capelist.index(cape) ]

                    await sheets.move_card_owner(user, request_to_id, desire_indexes)

                    await ctx.send("Trade made!")
                    del self.trades[request_to_id][user]
                    return
            else:
                await ctx.send("They haven't sent you a trade")
        elif subaction == "reject" or subaction == "cancel":
            request_to_id = (await self.at_to_id(args[0]))
            if user in self.trades and request_to_id in self.trades[user]:
                del self.trades[user][request_to_id]
                await ctx.send("Trade cancelled")
            elif request_to_id in self.trades and user in self.trades[request_to_id]:
                del self.trades[request_to_id][user]
                await ctx.send("Trade rejected")
            else:
                await ctx.send("Found no trade offer between the two of you")

    async def filter(self, ctx, user, *args):
        s = ""
        for i in args:
            s += i + " "
        s = s[:-1]
        categories = [
            "mover", "shaker", "brute", "breaker", "master", "tinker",
            "blaster", "thinker", "striker", "changer", "trump", "stranger"
        ]
        relevant = []
        if s.lower() in ["s", "a", "b", "c"]:
            for i in self.capelist:
                if i.tier.lower() == s.lower():
                    relevant += [i]
            messages = (await self.messagify_ownership(user, relevant, "{} Tier".format(s.upper())))

        elif s.lower() in categories:
            for i in self.capelist:
                if s.lower() in i.classification.lower():
                    relevant += [i]
            messages = (await self.messagify_ownership(user, relevant, "{} Capes".format(s)))
        elif s.lower() in ["pc", "npc"]:
            for i in self.capelist:
                if i.pc.lower() == s.lower():
                    relevant += [i]
            messages = (await self.messagify_ownership(user, relevant, "{} Capes".format(s)))
        elif s.lower() in ["hero", "villain", "rogue"]:
            for i in self.capelist:
                if i.alignment.lower() == s.lower():
                    relevant += [i]
            messages = (await self.messagify_ownership(user, relevant, "{} Aligned".format(s)))
        else:
            # We're filtering by affiliation or campaign
            for i in self.capelist:
                if i.affiliation.lower() == s.lower():
                    relevant += [i]
            if len(relevant) > 0:
                messages = (await self.messagify_ownership(user, relevant, "{} Affiliates".format(s)))
            else:
                for i in self.capelist:
                    if i.campaign.lower() == s.lower():
                        relevant += [i]
                if len(relevant) > 0:
                    messages = (await self.messagify_ownership(user, relevant, "{} Campaign".format(s)))
                else:
                    for i in self.capelist:
                        if s.lower() in i.name.lower():
                            relevant += [i]
                    if len(relevant) > 0:
                        messages = (await self.messagify_ownership(user, relevant, "{} Cape".format(s)))
                    else:
                        messages = ["Could not find any cards that matched the **{}** filter".format(s)]
        for i in messages:
            await ctx.send(i)

    async def grant(self, who, amount):
        if not who in self.bonus_claim:
            self.bonus_claim[who] = 0
        self.bonus_claim[who] += amount

    async def craft(self, ctx, who, *args):
        s = ""
        for i in args:
            s += i + " "
        s = s[:-1]
        if s == "help":
            message = "Pass in three cards you own to craft one of a higher tier. "
            message += "Mixing card tiers spreads your probability of getting an upgraded tier "
            message += "(ie [Tier A, Tier A, Tier C] = 66% chance of Tier S, 33% chance of Tier B).\n"
            message += "`%tc craft [Card 1, Card 2, Card 3]`"
            await ctx.send(message)
            return
        nil,s = s.split("[")
        s,nil = s.split("]")
        c1,c2,c3 = s.split(",")
        c1 = c1.strip()
        c2 = c2.strip()
        c3 = c3.strip()
        my_cards = [c1,c2,c3]
        if not await self.has_cards(who, my_cards):
            await ctx.send("You don't have all those cards available to craft with!")
            return
        upgrade = {"C": "B", "B": "A", "A": "S"}
        roll = []
        cards_to_remove = []
        for i in range(0,len(my_cards)):
            for j in self.capelist:
                if my_cards[i] == j.name:
                    if j.tier == "S":
                        await ctx.send("Can't upgrade from S tier cards")
                        return
                    roll += [upgrade[j.tier]]
                    cards_to_remove += [j]
                    break

        target = roll[random.randrange(0,3)]
        if target == "A":
            await ctx.send("Crafting an **{} Tier** card".format(target))
        else:
            await ctx.send("Crafting a **{} Tier** card".format(target))
        relevant = []
        for i in self.capelist:
            if i.tier == target:
                relevant += [i]
        selection = relevant[random.randrange(0,len(relevant))]
        r_card_index = []
        for i in cards_to_remove:
            self.trading[who].remove(i)
            r_card_index += [self.capelist.index(i)]
        await sheets.remove_cards(who, r_card_index)
        self.trading[who] += [selection]
        await sheets.gain_cards(who, [self.capelist.index(selection)])
        await ctx.send("Crafted **{}** card".format(selection.name))

    async def autocraft(self, ctx, who):
        owned = {}
        for i in self.trading[who]:
            if i.tier == "S":
                # We can't upgrade S tier cards!
                continue
            if i.tier not in owned:
                owned[i.tier] = {}
            if i not in owned[i.tier]:
                owned[i.tier][i] = 0
            owned[i.tier][i] += 1

        crafted = False

        upgrade = {"C": "B", "B": "A", "A": "S"}
        tier_sorted = {}
        gained = {}
        r_card_index = []

        for i in self.capelist:
            if i.tier not in tier_sorted:
                tier_sorted[i.tier] = []
            tier_sorted[i.tier] += [i]

        for tier in owned:
            # We're looking for a collection of three things!
            group = []
            for card in owned[tier]:
                while owned[tier][card] > 1:
                    owned[tier][card] -= 1
                    group += [card]
                    if len(group) == 3:
                        crafted_card = random.choice(tier_sorted[upgrade[tier]])
                        if upgrade[tier] not in gained:
                            gained[upgrade[tier]] = []
                        gained[upgrade[tier]] += [crafted_card]
                        for i in group:
                            r_card_index += [self.capelist.index(i)]
                            self.trading[who].remove(i)
                        crafted = True
                        group = []

        if not crafted:
            await ctx.send("Couldn't find enough duplicate cards to craft together")
        else:
            string = "Auto-crafting complete! Here is what's gotten made: \n"
            for tier in gained:
                r_string = f"**{tier}**:\n> "
                for i in gained[tier]:
                    r_string += f"{i.name}, "
                r_string = r_string[:-2] + "\n"
                if len(string + r_string) > 1999:
                    await ctx.send(string)
                    string = r_string
                else:
                    string += r_string
            await ctx.send(string)
            await sheets.remove_cards(who, r_card_index)
            gain_list = []
            for i in gained:
                self.trading[who] += gained[i]
                for card in gained[i]:
                    gain_list += [self.capelist.index(card)]
            await sheets.gain_cards(who, gain_list)

    async def collection(self, ctx, who, coll="help"):
        collections = ["Tier", "Affiliation", "Alignment", "Campaign", "Classification"]
        if coll.lower() == "help" or coll.capitalize() not in collections:
            await ctx.send(f"Possible collections you can specify are [{', '.join(collections)}]")
            return
        elif coll.lower() == "tier":
            coll_all = { "S": [], "A": [], "B": [], "C": [] }
            for i in self.capelist:
                coll_all[i.tier] += [i]
            owned = { "S": [], "A": [], "B": [], "C": [] }
            for i in self.trading[who]:
                if i not in owned[i.tier]:
                    owned[i.tier] += [i]
        elif coll.lower() == "affiliation":
            coll_all = {}
            owned = {}
            for i in self.capelist:
                if i.affiliation not in coll_all:
                    coll_all[i.affiliation] = []
                    owned[i.affiliation] = []
                coll_all[i.affiliation] += [i]
            for i in self.trading[who]:
                if i not in owned[i.affiliation]:
                    owned[i.affiliation] += [i]
        elif coll.lower() == "alignment":
            coll_all = {}
            owned = {}
            for i in self.capelist:
                if i.alignment not in coll_all:
                    coll_all[i.alignment] = []
                    owned[i.alignment] = []
                coll_all[i.alignment] += [i]
            for i in self.trading[who]:
                if i not in owned[i.alignment]:
                    owned[i.alignment] += [i]
        elif coll.lower() == "campaign":
            coll_all = {}
            owned = {}
            for i in self.capelist:
                if i.campaign not in coll_all:
                    coll_all[i.campaign] = []
                    owned[i.campaign] = []
                coll_all[i.campaign] += [i]
            for i in self.trading[who]:
                if i not in owned[i.campaign]:
                    owned[i.campaign] += [i]
        elif coll.lower() == "classification":
            coll_all = {
                "Mover": [], "Shaker": [], "Brute": [], "Breaker": [],
                "Master": [], "Tinker": [], "Blaster": [], "Thinker": [],
                "Striker": [], "Changer": [], "Trump": [], "Stranger": []
            }
            owned = {
                "Mover": [], "Shaker": [], "Brute": [], "Breaker": [],
                "Master": [], "Tinker": [], "Blaster": [], "Thinker": [],
                "Striker": [], "Changer": [], "Trump": [], "Stranger": []
            }
            for classification in coll_all:
                for i in self.capelist:
                    if classification in i.classification:
                        coll_all[classification] += [i]
                for i in self.trading[who]:
                    if i not in owned[classification] and classification in i.classification:
                        owned[classification] += [i]

        coll_string = []
        for i in sorted(coll_all.keys()):
            if len(owned[i]) != 0:
                coll_string += [ f"**{i}** ({len(owned[i])}/{len(coll_all[i])})"]
        printouts = [f"**{coll.capitalize()}** Collections: \n> {coll_string[0]}"]
        counter = 0
        for i in coll_string[1:]:
            if len(f"{printouts[counter]}, {i}") > 2000:
                counter += 1
                printouts += [f"> {i}"]
            else:
                printouts[counter] += f", {i}"
        for printout in printouts:
            await ctx.send(printout)

    @commands.command()
    async def tc(self, ctx, action, *args):
        '''Do things for the Parahumans server trading card game.
            %tc claim - Claim your daily free card
            %tc view [Card] - View all the cards you own
            %tc filter PC/Campaign/Affiliation/Tier etc. - Filter your cards by some type of card element
            %tc collection help - View the various collections you can view
            %tc submit - Get the link to submit new cards for review
            %tc masterlist - View the existing cape masterlist
            %tc trade [offer/view/accept/reject/cancel/help] @username - Make a trade
            %tc craft [Card 1, Card 2, Card 3] - Craft three cards together into a new one
            %tc autocraft - Automatically craft away duplicates (as long as you have 3 or more in a specific rarity)
        '''
        async with self.lock:
            if action == "unpause" and str(ctx.author.id) == "227834498019098624":
                self.pause = False
                return
            if self.pause:
                # For when developing on a secondary bot
                return
            if not self.cached:
                await ctx.send("Caching things on first run")
                await self.set_local_cache()
            if action == "claim":
                #await ctx.send("Claiming paused while Wellwick experiments with things")
                await self.random_claim(ctx, str(ctx.author.id))
            elif action == "recache" and str(ctx.author.id) == "227834498019098624":
                self.capelist = []
                self.trading = {}
                self.triggers = {}
                self.reviewing = {}
                await self.set_local_cache()
            elif action == "view" or action == "list" or action == "check":
                await self.view(ctx, str(ctx.author.id), *args)
            elif action == "submit":
                await ctx.send("<https://docs.google.com/forms/d/e/1FAIpQLSdntX_uPBSttXxuYlHh_lLszN1YYk248xSBLbuFXiGAQ3PdIA/viewform>")
            elif action == "masterlist":
                await ctx.send("<https://docs.google.com/spreadsheets/d/1PcMDs_zm8xg22IdXl8hoHS8IPF5skX-_GK3djUZSlBw/edit#gid=0>")
            elif action == "trade":
                if len(args) == 0:
                    await ctx.send("Missing trade subcommand (ie offer, accept, reject, view, cancel)")
                else:
                    await self.trade(ctx, str(ctx.author.id), args[0], *args[1:])
            elif action == "offer" and len(args) > 0 and args[1] == "trade":
                await self.trade(ctx, str(ctx.author.id), "offer", *args[1:])
            elif action == "filter":
                await self.filter(ctx, str(ctx.author.id), *args)
            elif action == "pause" and str(ctx.author.id) == "227834498019098624":
                self.pause = True
            elif action == "grant" and str(ctx.author.id) == "227834498019098624":
                who = await self.at_to_id(args[0])
                amount = int(args[1])
                await self.grant(who, amount)
            elif action == "craft":
                await self.craft(ctx, str(ctx.author.id), *args)
            elif action == "autocraft":
                await self.autocraft(ctx, str(ctx.author.id))
            elif action == "collection":
                await self.collection(ctx, str(ctx.author.id), *args)

    async def start_battle(self, battle: Battle):
        for i in battle.teams:
            team = [cape.cape.name for cape in battle.teams[i].team]
            for cape in battle.teams[i].team:
                self.trading[i] += [ cape.cape ]
            await battle.channel.send(f"<@{i}> has brought their team: {', '.join(team)}")
        await battle.channel.send("It's time to fight! PM your strategy for the first round `%battle attack/defend/ambush/flee/stats`")

    async def do_battle_round(self, battle: Battle):
        starting_pools = {}
        gameover = False
        for i in battle.teams:
            starting_pools[i] = battle.teams[i].pool.copy()
        for i in battle.teams:
            for j in battle.teams:
                if j is not i:
                    enemy = battle.teams[j]
            battle.teams[i].make_move(enemy)
        for i in battle.teams:
            new_losses = [x.cape.name for x in battle.teams[i].pool if x not in starting_pools[i]]
            if len(new_losses) > 0:
                await battle.channel.send(f"<@{i}> has lost the capes {', '.join(new_losses)}")
            elif battle.teams[i].damage_taken:
                await battle.channel.send(f"<@{i}> has lost no units this round, but did take damage!")
            else:
                await battle.channel.send(f"<@{i}> has lost no units this round and took no damage!")
            battle.teams[i].new_round()
            if len(battle.teams[i].team) == 0:
                await battle.channel.send(f"<@{i}>'s team has been defeated!")
                gameover = True
            elif battle.teams[i].fled:
                await battle.channel.send(f"<@{i}>'s team has fled!")
                gameover = True

        if gameover:
            await battle.channel.send("That's it, gameover! Thanks for playing.")
            for i in starting_pools:
                del self.battles[i]
        else:
            await battle.channel.send("Time for a new round! PM your strategy `%battle attack/defend/ambush/flee/stats` (check stats for ambush success)")


    @commands.command()
    async def battle(self, ctx, *, args=""):
        '''Begin a battle against another player. Can specify size of game as well.'''
        if not self.cached:
            await ctx.send("Caching things on first run")
            await self.set_local_cache()

        player = str(ctx.author.id)
        if not player in self.battles:
            args = args.split()
            if len(args) == 0:
                args = [""]
            enemy = await self.at_to_id(args[0].strip())
            if len(args) > 1:
                cap = int(args[1])
            else:
                cap = 10
            if not enemy in self.trading:
                await ctx.send("Player not recognised!\nFor now, starting a testing battle")
                self.battles[player] = Battle({player: [], "test": self.capelist[:2]},self.battle_stats, cap=cap, channel=ctx.channel)
                self.battles[player].teams["test"].ready = True
                self.battles[player].teams["test"].move = "Defend"
                return
            else:
                await ctx.send("Starting a battle. Both go add your cards as fighting capes in PMs using `%battle add capename, capename, capename`!")
                self.battles[player] = Battle({player: [], enemy: []}, self.battle_stats, cap=cap, channel=ctx.channel)
                self.battles[enemy] = self.battles[player]
        elif not self.battles[player].started:
            if args.split()[0] == "add":
                splittup = args[4:].split(",")
                capes = []
                for i in splittup:
                    capes += [i.strip()]
                if await self.has_cards(player, capes):
                    for card in capes:
                        cape = await self.get_cape(card)
                        self.trading[player].remove(cape)
                        if not self.battles[player].teams[player].add_cape(cape):
                            await ctx.send(f"Adding {card} exceeds the quota for the team")
                else:
                    await ctx.send(f"You don't have all of those cards!")

                await ctx.send(self.battles[player].teams[player].info_string())
            elif args.split()[0].lower() == "quit" or args.split()[0].lower() == "cancel":
                # Quitting before the game starts!
                await ctx.send("Quitting the game")
                for i in self.battles[player].teams:
                    if i != player:
                        enemy = i
                await self.battles[player].channel.send(f"<@{enemy}>, <@{player}> has cancelled the battle!")
                for bc in self.battles[player].teams[player].team:
                    self.trading[player] += [bc.cape]
                del self.battles[player]
                if enemy in self.battles:
                    for bc in self.battles[enemy].teams[enemy].team:
                        self.trading[enemy] += [bc.cape]
                    del self.battles[enemy]
            elif args.split()[0].lower() == "start" or args.split()[0].lower() == "ready":
                p_team = self.battles[player].teams[player]
                if p_team.cap is not None and p_team.quota() < p_team.cap and not p_team.forcing:
                    p_team.forcing = True
                    await ctx.send("You haven't filled your team to the cap, are you sure you want to start? Resend the command if so!")
                    return
                p_team.ready = True
                if self.battles[player].ready():
                    self.battles[player].started = True
                    await ctx.send("Other player is ready. Game starting!")
                    await self.start_battle(self.battles[player])
                else:
                    await ctx.send("Waiting for other player!")
        elif self.battles[player].started:
            strategy = args.split()[0].lower()
            p_team = self.battles[player].teams[player]
            if strategy == "attack":
                p_team.move = "Attack"
            elif strategy == "defend":
                p_team.move = "Defend"
            elif strategy == "ambush":
                p_team.move = "Ambush"
            elif strategy == "flee":
                p_team.move = "Flee"
            elif strategy == "stats":
                await ctx.send(self.battles[player].teams[player].info_string())
                return
            else:
                await ctx.send("Strategy is not recognised")
                return

            if self.battles[player].do_turn():
                await ctx.send("Starting the new round!")
                await self.do_battle_round(self.battles[player])
            else:
                await ctx.send("Waiting for other player to decide strategy")


    @commands.command()
    async def submit(self, ctx, *, args):
        '''Submit a trigger to the sheet and gain a few cards. Please only submit if putting in actual effort or this feature will be removed/you will be blacklisted.
        If a mistake is made (ie spelling, trigger longer than a discord message can contain) PM Wellwick
        '''
        if not self.cached:
            await ctx.send("Caching things on first run")
            await self.set_local_cache()
        s = args.strip()
        if len(s) == 0:
            await ctx.send("Can't submit an empty trigger")
            return
        elif len(s) > 1850:
            await ctx.send(f"Your trigger is {1850 - len(s)} characters too long!")
            return
        if s in self.triggers:
            await ctx.send("This trigger already exists!")
            return
        self.triggers[s] = [str(ctx.author.id)]
        await sheets.submit_trigger(s, str(ctx.author.id), ctx.author.name)
        await self.grant(str(ctx.author.id),3)
        await ctx.send("Thanks for submitting a trigger. You've earned some bonus cards that you can `%tc claim`")

    @commands.command()
    async def r(self, ctx, subaction, *args):
        '''Do some reviewing of submitted triggers and earn some cards. Is done in PMs!
        %r get - Get a trigger to review
        %r approve - Approve the trigger you are reviewing
        %r critique [criticism] - Add a critique for the trigger
        %r skip - Skip the trigger you are currently reviewing'''
        if not self.cached:
            await ctx.send("Caching things on first run")
            await self.set_local_cache()
        user = str(ctx.author.id)
        if subaction == "get":
            message = ""
            if user in self.reviewing:
                message += "You are already reviewing a trigger\n"
                message += self.reviewing[user]
            else:
                # Randomly select from one they haven't already reviewed
                triggers = []
                for i in self.triggers:
                    if not user in self.triggers[i]:
                        triggers += [i]
                if len(triggers) == 0:
                    await ctx.author.send("You've already reviewed all the triggers available. Great job!")
                    return
                selected = triggers[random.randrange(0,len(triggers))]
                self.reviewing[user] = selected
                message += selected + "\n"
            message += "```%r approve comments - Approve the trigger. Comments optional\n"
            message += "%r critique comments - Critique the trigger\n"
            message += "%r skip - Skip reviewing this trigger```"
            await longpm(ctx, message)
        elif subaction == "approve":
            if not user in self.reviewing:
                await ctx.author.send("You aren't reviewing anything")
                return
            comments = ""
            for i in args:
                comments += i + " "
            comments[:-1]
            trigger = self.reviewing[user]
            self.triggers[trigger] += [user]
            try:
                await sheets.approve_trigger(trigger, user, ctx.author.name, comments)
            except:
                await ctx.send("Looks like this trigger may have changed remotely! Please ping Wellwick to ask for a recache. Skipping trigger")
                self.triggers[self.reviewing[user]] += [user]
                del self.reviewing[user]
                return
            del self.reviewing[user]
            await self.grant(user,1)
            await ctx.author.send("Thanks for reviewing a trigger. You've earned a bonus card that you can `%tc claim`")
        elif subaction == "critique":
            if not user in self.reviewing:
                await ctx.author.send("You aren't reviewing anything")
                return
            comments = ""
            if len(args) == 0:
                await ctx.author.send("You have provided no comments")
                return
            for i in args:
                comments += i + " "
            comments[:-1]
            trigger = self.reviewing[user]
            self.triggers[trigger] += [user]
            try:
                await sheets.critique_trigger(trigger, user, ctx.author.name, comments)
            except:
                await ctx.send("Looks like this trigger may have changed remotely so you can't review it right now, sorry! Please ping Wellwick to ask for a recache. Skipping trigger")
                self.triggers[self.reviewing[user]] += [user]
                del self.reviewing[user]
                return
            del self.reviewing[user]
            await self.grant(user,1)
            await ctx.author.send("Thanks for reviewing a trigger. You've earned a bonus card that you can `%tc claim`")
        elif subaction == "skip":
            if not user in self.reviewing:
                await ctx.author.send("You aren't reviewing anything")
                return
            self.triggers[self.reviewing[user]] += [user]
            del self.reviewing[user]


    @commands.command()
    async def cape(self, ctx, *args):
        '''Provide information on Weaverdice capes in the database.

        Can access the google sheets at https://docs.google.com/spreadsheets/d/1_syrsmptzWG0u3xdY3qzutYToY1t3I8s6yaryIpfckU/edit#gid=1668315016
        '''
        # Search for the cape name
        name = ""
        for arg in args:
            name += arg + " "

        name = name[:-1]
        info = (await sheets.cape(name))
        if info:
            output = "**" + info[0] + "**"
            if len(info) > 5 and not info[5] == "":
                output += " (" + info[5] + ")"
            output += "\n"
            if len(info) > 9 and not info[9] == "":
                output += "> Status: **" + info[9] + "**\n"
            if len(info) > 1 and not info[1] == "":
                output += "> Civilian identity: ||" + info[1] + "||\n"
            if (len(info) > 3 and not info[3] == "") or (len(info) > 4 and not info[4] == ""):
                output += "> Affiliation: " + info[3]
                if len(info) > 4 and (not info[3] == "" and not info[4] == ""):
                    output += ", "
                output += info[4] + "\n"
            if len(info) > 2 and not info[2] == "":
                output += "> Power: " + info[2] + "\n"
            if len(info) > 7 and not info[7] == "":
                output += "> Campaign: **" + info[7] + "**\n"
            if len(info) > 8 and not info[8] == "":
                output += "> Owner: **" + info[8] + "**"
                if len(info) > 6 and not info[6] == "":
                    output += ", " + info[6]
                output += "\n"
            elif len(info) > 6 and not info[6] == "":
                output += "> Unowned, **" + info[6] + "**\n"
            if len(info) > 10 and not info[10] == "":
                output += "> Additional notes: " + info[10]
            await ctx.send(output)
            #await ctx.send(str(info))
        else:
            await ctx.send("Couldn't find cape!")
