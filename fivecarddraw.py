from functools import reduce
from itertools import groupby
from math import inf
from random import choice, shuffle


class Card(object):
    def __init__(self, value, suit):
        try:
            value %= 13
            suit %= 4
        except TypeError:
            raise Exception("Card objects only allow integers as arguments.")

        self.VALUES = (
            "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
        self.SUITS = ("♠","♡","♢","♣")
        
        self.MASK = "xxxAKQJT98765432♣♢♡♠RRRRxxPPPPPP" 
        self.PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
        
        self._prime = self.PRIMES[value]
        self._rank = value << 8
        self._suit = (2 ** suit) << 12
        self._value = (2 ** value) << 16
        
        self.b = self._prime + self._rank + self._suit + self._value
    
        self.value_i, self.suit_i = value, suit
        self.value_r, self.suit_r = self.VALUES[value], self.SUITS[suit]
        self.r = self.value_r + self.suit_r
    
    def __repr__(self):
        return self.r
    

class Deck(object):
    def __init__(self):
        self.state = [Card(v, s) for v in range(13) for s in range(4)]
        self.t = 0

    def __repr__(self):
        return str(self.state[self.t:])

    def __iter__(self):
        return self.state

    def __next__(self):
        try:
            top_card = self.state[self.t]
        except IndexError:
            raise StopIteration()

        self.t += 1
        return top_card

    def Shuffle(self, reset=True):
        shuffle(self.state)
        if reset:
            self.t = 0
        return self

    def CountRemaining(self):
        return 52 - self.t

    def RestartIterator(self):
        self.t = 0
        return self


class HandTracker(object):
    def __init__(self):
        self.DV = {char : 2 ** i for i, char in enumerate("23456789TJQKA")}
        self.DP = {char : p for p, char in zip(Card(0,0).PRIMES, "23456789TJQKA")}

        self.LoadLookupTables()

        self.CLASSES = (
            "High card", 
            "pair", 
            "two pair", 
            "three of a kind", 
            "straight", 
            "flush", 
            "full house",
            "four of a kind" 
            "straight flush", 
            "royal flush")

        self.BOUNDARIES = (6186, 3326, 2468, 1610, 1600, 323, 167, 11, 2, 1)

        self.DECK = Deck()
        self.DECK.Shuffle()

        self.hands = {}

    def DealHands(self, names):
        self.hands = {name : {"cards" : []} for name in names}
        for _ in range(5):
            for name in names:
                self.hands[name]["cards"].append(next(self.DECK))
        return self.hands

    def ApproveDiscards(self, name, discards):
        cards = self.hands[name]["cards"]
        remaining = [card for card in cards if card not in discards]
        if len(discards) == 5:
            return False
        if len(discards) == 4 and self.ExtractProduct(remaining) % 41:
            return False
        return True

    def EditHand(self, name, discards):
        self.hands[name]["cards"] = list(filter(lambda x : x not in discards, self.hands[name]["cards"]))
        while len(self.hands[name]["cards"]) < 5:
            self.hands[name]["cards"].append(next(self.DECK))
        return self.hands[name]["cards"]
    
    def CollectHands(self):
        self.hands = {}
        self.DECK.Shuffle()
        return self.DECK

    def LoadLookupTables(self):
        self.FLUSH_RANKS = {}
        with open("lookup-tables/flush lookup.txt", "r") as file:
            for line in file:
                load_v = reduce(lambda x, y : x+y, map(lambda x : self.DV[line[int(x)]], "45678"))
                self.FLUSH_RANKS[load_v] = int(str(line)[11:])

        self.UNIQUE5_RANKS = {}
        with open("lookup-tables/unique five lookup.txt", "r") as file:
            for line in file:
                load_v = reduce(lambda x, y : x+y, map(lambda x : self.DV[line[int(x)]], "45678"))
                self.UNIQUE5_RANKS[load_v] = int(str(line)[11:])

        self.DUPE_RANKS = {}
        with open("lookup-tables/dupe lookup.txt", "r") as file:
            for line in file:
                load_p = reduce(lambda x, y : x*y, map(lambda x : self.DP[line[int(x)]], "45678"))
                self.DUPE_RANKS[load_p] = int(str(line)[11:])

    def CheckFlush(self, cards):
        suit_mask = 15 << 12
        has_flush = reduce(lambda x, y : x&y, map(lambda x : x.b, cards)) & suit_mask
        return bool(has_flush)

    def CheckUnique5(self, cards):
        values = reduce(lambda x, y : x|y, map(lambda x : x.b, cards)) >> 16
        has_unique5 = bin(values).count("1") == 5
        return has_unique5

    def ExtractSum(self, cards):
        return reduce(lambda x, y : x|y, map(lambda x : x.b, cards)) >> 16

    def ExtractProduct(self, cards):
        return reduce(lambda x, y : x*y, map(lambda x : x.b & 255, cards))

    def EvaluateHand(self, name):
        if self.CheckFlush(self.hands[name]["cards"]):
            key = self.ExtractSum(self.hands[name]["cards"])
            self.hands[name]["rank_n"] = self.FLUSH_RANKS[key]
        elif self.CheckUnique5(self.hands[name]["cards"]):
            key = self.ExtractSum(self.hands[name]["cards"])
            self.hands[name]["rank_n"] = self.UNIQUE5_RANKS[key]
        else:
            key = self.ExtractProduct(self.hands[name]["cards"])
            self.hands[name]["rank_n"] = self.DUPE_RANKS[key]

        c = 10 - len(list(filter(lambda x : self.hands[name]["rank_n"] >= x, self.BOUNDARIES)))
        self.hands[name]["rank_c"] = self.CLASSES[c]
        return self.hands[name]

    def EvaluateHands(self):
        for name in self.hands.keys():
            self.EvaluateHand(name)
        return self.hands

    def DemoEvaluate(self, cards):
        if self.CheckFlush(cards):
            key = reduce(lambda x, y : x|y, map(lambda x : x.b, cards)) >> 16
            rank_n = self.FLUSH_RANKS[key]
        elif self.CheckUnique5(cards):
            key = reduce(lambda x, y : x|y, map(lambda x : x.b, cards)) >> 16
            rank_n = self.UNIQUE5_RANKS[key]
        else:
            key = reduce(lambda x, y : x*y, map(lambda x : x.b & 255, cards))
            rank_n = self.DUPE_RANKS[key]

        c = 10 - len(list(filter(lambda x : rank_n >= x, self.BOUNDARIES)))
        rank_c = self.CLASSES[c]

        return {"rank_c": rank_c, "rank_n": rank_n}

    def DemoDeal(self):
        hand = []
        for _ in range(5):
            hand.append(next(self.DECK))
        self.DECK.Shuffle()
        return hand    


class SeatTracker(object):
    def __init__(self, amount_seats):
        self.seats = ["" for _ in range(amount_seats)]
        self.players = {}

        self.action = {"seat" : -1, "player" : "", "queue" : self.seats}
        self.button = {"seat" : -1, "player" : "", "queue" : self.seats}

        self.count = amount_seats

    def AddPlayer(self, name, seat):
        self.seats[seat] = name
        self.players[name] = {}
        self.players[name]["seat"] = seat
        self.UpdateDealingOrder()
        return self.players

    def KickPlayer(self, name):
        seat = self.players[name]["seat"]
        self.seats[seat] = ""
        del self.players[name]
        self.UpdateDealingOrder()
        return self.players

    def AddPlayers(self, players):
        for assignment in zip(players, self.AvailableSeats()):
            name = assignment[0]
            empty_seat = assignment[1]
            self.AddPlayer(name, empty_seat)
        return self.players

    def NextButtonPlayer(self):
        while True:
            seat = self.button["seat"]
            seat += 1
            seat %= self.count
            self.button["seat"] = seat
            if self.seats[seat] or not self.DealingOrder():
                self.UpdateDealingOrder() 
                break
        return self.button 

    def UpdateDealingOrder(self):
        seat = self.button["seat"]
        self.button["player"] = self.seats[seat]
        self.button["queue"] = [name for name in self.seats[seat+1:] + self.seats[:seat+1] if name]
        return self.button

    def DealingOrder(self):
        return self.button["queue"] 

    def ActionOrder(self):
        name = self.DealingOrder()[4 % len(self.Names())]
        seat = self.players[name]["seat"]
        self.action["player"] = name
        self.action["seat"] = seat
        self.action["queue"] = [name for name in self.seats[seat+1:] + self.seats[:seat+1] if name]
        return self.action["queue"]

    def Names(self):
        return [occupant for occupant in self.seats if occupant]

    def AvailableSeats(self):
        return [i for i, occupant in enumerate(self.seats) if not occupant]


class ChipTracker(object):
    def __init__(self):
        self.gameinfo = {"smallblind" : 0, "bigblind" : 0, "ante" : 0}

        self.players = {}

    def AddChipsPlayer(self, name, amount):
        self.players.setdefault(name, {"stack" : 0, "contribution" : 0})
        self.players[name]["stack"] += amount
        return self.players

    def WithdrawChipsPlayer(self, name):
        del self.players[name]
        return self.players

    def BetChipsPlayer(self, name, amount):
        self.players[name]["stack"] -= amount
        self.players[name]["contribution"] += amount
        return self.players

    def RewardChipsPlayer(self, name, amount):
        self.players[name]["stack"] += amount
        return self.players

    def ApproveBet(self, name, amount):
        return True if amount <= self.players[name]["stack"] else False

    def FeeStatus(self, name, amount):
        has_enough = True if amount <= self.players[name]["stack"] else False
        has_allin = True if amount >= self.players[name]["stack"] else False
        has_passed = True if amount == 0 else False
        return {"has_enough" : has_enough, "has_allin" : has_allin, "has_passed" : has_passed}

    def AmountToCall(self, name):
        contributions = [self.players[name]["contribution"] for name in self.players.keys()]
        return max(contributions) - self.players[name]["contribution"]

    def BetStatus(self, name, amount):
        min_to_call = self.AmountToCall(name)
        has_raised = True if amount > min_to_call else False
        has_allin = True if amount == self.players[name]["stack"] else False
        has_mincalled = True if amount >= min_to_call else False
        has_folded = True if min_to_call and not amount else False
        return{"has_raised" : has_raised, "has_allin" : has_allin, "has_mincalled" : has_mincalled, "has_folded" : has_folded}

    def CalculateRewards(self, player_info):
        rewards = {}
        candidates = [name for name in player_info.keys() if not player_info[name]["status"]["has_folded"]]
        candidates.sort(key = lambda x : (player_info[x]["hand"]["rank_n"], player_info[x]["chips"]["contribution"]))
        candidate_splits = groupby(candidates, key = lambda x : player_info[x]["hand"]["rank_n"])
        for rank_n, group in candidate_splits:
            candidates = list(group)
            reward_to_split = 0
            for i, candidate in enumerate(candidates):
                contributors = [name for name in player_info.keys()]
                contributors.sort(key = lambda x : player_info[x]["chips"]["contribution"], reverse=True)
                for contributor in contributors:
                    if not player_info[contributor]["chips"]["contribution"]:
                        break
                    if contributor == candidate:
                        continue
                    if player_info[contributor]["chips"]["contribution"] > player_info[candidate]["chips"]["contribution"]:
                        reward_to_split += player_info[candidate]["chips"]["contribution"]
                        player_info[contributor]["chips"]["contribution"] -= player_info[candidate]["chips"]["contribution"]
                    else:
                        reward_to_split += player_info[contributor]["chips"]["contribution"]
                        player_info[contributor]["chips"]["contribution"] = 0
                reward_to_split += player_info[candidate]["chips"]["contribution"]
                player_info[candidate]["chips"]["contribution"] = 0
                candidate_reward = reward_to_split // (len(candidates) - i)
                rewards[candidate] = candidate_reward
                reward_to_split -= candidate_reward
        return rewards

    def ClearPot(self):
        for name in self.players.keys():
            self.players[name]["contribution"] = 0
        return self.players

    def PotTotal(self):
        return sum([self.players[name]["contribution"] for name in self.players.keys()])

    def ChipStacks(self):
        return {name : self.players[name]["stack"] for name in self.players}
            

class ActionTracker(object):
    def __init__(self):
        self.players = {}
        self.beings = {"humans" : [], "bots" : []}

    def NewRound(self, names):
        for name in names:
            self.players[name] = {"has_allin" : False, "has_mincalled" : False, "has_folded" : False}
        return True

    def ExtendRound(self):
        for name in self.players.keys():
            self.players[name]["has_mincalled"] = False
        return True

    def PlayerHasActed(self, name):
        return any(self.players[name].values())

    def ShowdownPlayers(self, dealing_order):
        return [name for name in dealing_order if not self.players[name]["has_folded"]]

    def ActingPlayers(self, action_order):
        return [name for name in action_order if not self.players[name]["has_folded"] and not self.players[name]["has_allin"]]

    def AddHuman(self, name):
        self.beings["humans"].append(name)
        return True
    
    def AddBots(self, names):
        for name in names:
            self.beings["bots"].append(name)
        return True

    def KickBot(self, name):
        self.beings["bots"].remove(name)
        del self.players[name]
        return True

    def Human(self):
        if self.beings["humans"]:
            return self.beings["humans"][0]
        return "NO_HUMANS"

    def SelectAmount(self, name, info):
        if name in self.beings["humans"]:
            print(f"[INFO] Your cards are {info['self']['hand']['cards']}")
            print(f"[INFO] There are {info['game']['pot']} chips in the pot.")
            print(f"[INFO] You have {info['self']['chips']['stack']} chips remaining.")
            print(f"[INFO] The amount to call is {info['game']['call']} chips.")
            amount = int(input("How much would you like to put in the pot?"))
        else:
            amount = choice([0, info['self']['chips']['stack'], info['game']['call'], info['game']['pot'], 2*info['game']['pot'], 2*info['game']['call']])
        return amount

    def SelectDiscards(self, name, info):
        if name in self.beings["humans"]:
            print(f"[INFO] Your cards are {info['self']['hand']['cards']}")
            mask = input("Which cards would you like to swap? (00000 for none, 11111 for all)").split("")
            discards =  [info['self']['hand']['cards'][i] for i, v in enumerate(mask) if int(v)]
        else:
            discards = [info['self']['hand']['cards'][i] for i in range(5) if choice([True,False])]
        return discards


class Dealer(object):
    def __init__(self):
        self.cards = HandTracker()
        self.seats = SeatTracker(6)
        self.chips = ChipTracker()
        self.action = ActionTracker()
        
    def MoveButton(self):
        self.seats.NextButtonPlayer()
        player = self.seats.button["player"]
        seat = self.seats.button["seat"]
        if player:
            print(f"[BUTTON] The button was given to {player}.")
            return True
        else:
            print(f"[BUTTON] The button was moved to seat {seat}.")
            return False
        
    def DealHands(self):
        names = self.seats.DealingOrder()
        self.cards.DealHands(names)
        self.cards.EvaluateHands()
        self.action.NewRound(names)
        print(f"[CARDS] Hands have been dealt.")
        return True
    
    def EditHand(self, name, discards):
        if self.cards.ApproveDiscards(name, discards):
            self.cards.EditHand(name, discards)
            self.cards.EvaluateHand(name)
            if discards:
                print(f"[CARDS] {name} swapped {len(discards)} cards.")
            else:
                print(f"[CARDS] {name} didn't swap any cards.")
            return True
        return False
        
    def CollectCards(self):
        self.cards.CollectHands()
        print(f"[CARDS] Hands have been collected.")
        print(f"[CARDS] The deck has been shuffled.")
        return True
        
    def TakeAnte(self):
        for name in self.seats.DealingOrder():
            amount = self.chips.gameinfo["ante"] 
            status = self.chips.FeeStatus(name, amount)
            if status["has_passed"]:
                continue
            if not status["has_enough"]:
                amount = self.chips.players[name]["status"]
            if status["has_allin"]:
                self.action.players[name]["has_allin"] = True 
                print(f"[ANTE] The ante forced {name} to go all-in with {amount} chips!")
            else:
                print(f"[ANTE] {name} paid {amount} chips for the ante.")
            self.chips.BetChipsPlayer(name, amount)
    
    def TakeBet(self, name, amount):
        if self.chips.ApproveBet(name, amount):
            status = self.chips.BetStatus(name, amount)
            print(f"[DEBUG] amount {amount}")
            print(f"[DEBUG] status {status}")
            if not any([status["has_mincalled"], status["has_allin"], status["has_folded"]]):
                return False
            if status["has_raised"] and status["has_allin"]:
                self.action.ExtendRound()
                self.action.players[name]["has_allin"] = True
                surplass = amount - self.chips.AmountToCall(name) 
                print(f"[ACTION] {name} has raised by {surplass} and gone all-in!")
            elif status["has_raised"] and status["has_mincalled"]:
                self.action.ExtendRound()
                self.action.players[name]["has_mincalled"] = True
                surplass = amount - self.chips.AmountToCall(name) 
                print(f"[ACTION] {name} has raised by {surplass}.")
            elif status["has_allin"] and status["has_mincalled"]:
                self.action.players[name]["has_allin"] = True
                print(f"[ACTION] {name} has gone all-in to call!")
            elif status["has_mincalled"] and amount == 0:
                self.action.players[name]["has_mincalled"] = True
                print(f"[ACTION] {name} has checked.")
            elif status["has_mincalled"]:
                self.action.players[name]["has_allin"] = True
                print(f"[ACTION] {name} has called.")
            elif status["has_folded"]:
                self.action.players[name]["has_folded"] = True
                print(f"[ACTION] {name} has folded.")
            elif status["has_allin"]:
                self.action.players[name]["has_allin"] = True
                print(f"[ACTION] {name} couldn't call but has gone all-in.")
            self.chips.BetChipsPlayer(name, amount)
            return True
        else:
            return False

    def PlayerInfo(self):
        info = {}
        for name in self.seats.Names():
            info[name] = {}
            info[name]["hand"] = self.cards.hands[name]
            info[name]["seat"] = self.seats.players[name]
            info[name]["chips"] = self.chips.players[name]
            info[name]["status"] = self.action.players[name]
        return info

    def TableView(self, viewer):
        info = {"self" : {}, "others" : {}, "game" : {}}
        for name in self.seats.Names():
            if viewer == name:
                info["self"]["seat"] = self.seats.players[name]
                info["self"]["chips"] = self.chips.players[name]
                info["self"]["status"] = self.action.players[name]
                info["self"]["hand"] = self.cards.hands[name]
            else:
                info["others"][name] = {}
                info["others"][name]["seat"] = self.seats.players[name]
                info["others"][name]["chips"] = self.chips.players[name]
                info["others"][name]["status"] = self.action.players[name]
                info["others"][name]["hand"] = self.cards.hands[name]
        info["game"]["call"] = self.chips.AmountToCall(viewer)
        info["game"]["pot"] = self.chips.PotTotal()
        return info

    def KickPlayer(self, name):
        self.seats.KickPlayer(name)
        self.chips.WithdrawChipsPlayer(name)
        self.action.KickBot(name)
        print(f"[PLAYER] {name} is leaving the table.")
        return True
         
    def Payout(self):
        info = self.PlayerInfo()
        rewards = self.chips.CalculateRewards(info)
        showdown = self.action.ShowdownPlayers(self.seats.DealingOrder())
        
        if len(rewards) < 2:
            winner = showdown[0]
            print(f"[SHOWDOWN] {winner} won {rewards[winner]} chips.")
            return True
        
        i, rank_n = 0, inf
        for name in showdown:
            if self.cards.hands[name]["rank_n"] <= rank_n:
                hand = self.cards.hands[name]["cards"]
                print(f"[SHOWDOWN] {name} is holding {hand}")
            else:
                print(f"[SHOWDOWN] {name} mucked.")

        for name in showdown:
            reward = rewards[name]
            if reward:
                hand = self.cards.hands[name]["rank_c"]
                print(f"[REWARDS] {name} won {reward} with a {hand}")
                self.chips.RewardChipsPlayer(name, reward)

        self.chips.ClearPot()
        return True

    def StartingChips(self, amount):
        for name in self.seats.Names():
            self.chips.AddChipsPlayer(name, amount)
        print(f"[SETUP] All players have been given {amount} chips.")
        return True

    def Ante(self, amount):
        self.chips.gameinfo["ante"] = amount
        print(f"[SETUP] The ante has been set to {amount} chips.")
        return True

    def Summary(self):
        for name in self.seats.Names():
            print(f"[STANDINGS] {name} has got {self.chips.players[name]['stack']} chips remaining.")
        return True


class PlayGame(object):
    def __init__(self):
        self.OPPONENTS = ["Phil Ivey", "Gus Hanson", "Dan Negreanu", "Phil Hellmuth"]
        self.CHIPS = 500
        self.ANTE = 5
        self.dealer = Dealer()

        self.Configuration()

        while self.NewHand():
            self.BettingPhase()
            self.SwitchingPhase()
            self.BettingPhase()
            self.EvaluationPhase()
        else:
            self.EndGame()

    def Configuration(self):
        player = input("What's your name?")
        names = [player] + self.OPPONENTS
        shuffle(names)
        self.dealer.seats.AddPlayers(names)
        self.dealer.action.AddHuman(player)
        self.dealer.action.AddBots(self.OPPONENTS)
        print("\n")
        self.dealer.StartingChips(self.CHIPS)
        self.dealer.Ante(self.ANTE)

    def NewHand(self):
        human = self.dealer.action.Human()
        if not self.dealer.chips.players[human]["stack"]:
            print(f"[END] Game over {human}, better luck next time.")
            return False

        for name in self.dealer.seats.Names():
            if not self.dealer.chips.players[name]["stack"]:
                self.dealer.KickPlayer(name)

        if len(self.dealer.seats.Names()) < 2:
            print(f"[END] {human} has won!")

        print(f"\n[NEW ROUND]")
        self.dealer.MoveButton()
        self.dealer.TakeAnte()
        self.dealer.DealHands()
        return True

    def BettingPhase(self):
        action_order = self.dealer.seats.ActionOrder()
        if len(self.dealer.action.ActingPlayers(action_order)) < 2:
            return True

        unfinished = True
        while unfinished:
            for name in action_order:
                if self.dealer.action.PlayerHasActed(name):
                    continue
                info = self.dealer.TableView(name)
                while True:
                    amount = self.dealer.action.SelectAmount(name, info)
                    if self.dealer.TakeBet(name, amount):
                        break
            
            players_are_done = [self.dealer.action.PlayerHasActed(name) for name in action_order]
            unfinished = not all(players_are_done)

        self.dealer.action.ExtendRound()
        return True

    def SwitchingPhase(self):
        dealing_order = self.dealer.seats.ActionOrder()
        if len(self.dealer.action.ActingPlayers(dealing_order)) < 2:
            return True
        for name in dealing_order:
            if self.dealer.action.players[name]["has_folded"]:
                continue
            info = self.dealer.TableView(name)
            while True:
                discards = self.dealer.action.SelectDiscards(name, info)
                if self.dealer.EditHand(name, discards):
                    if name == self.dealer.action.Human() and discards:
                        print(f"[CARDS] Your new hand is {self.dealer.cards.hands[name]['cards']}")
                    break
        return True

    def EvaluationPhase(self):
        self.dealer.Payout()
        self.dealer.CollectCards()
        self.dealer.Summary()
    
    def EndGame(self):
        print("[END] Thanks for playing!")


class SpectateGame(PlayGame):
    def __init__(self):
        super().__init__()
    
    def Configuration(self):
        self.dealer.seats.AddPlayers(self.OPPONENTS)
        self.dealer.action.AddBots(self.OPPONENTS)
        print("\n")
        self.dealer.StartingChips(self.CHIPS)
        self.dealer.Ante(self.ANTE)
    
    def NewHand(self):
        for name in self.dealer.seats.Names():
            if not self.dealer.chips.players[name]["stack"]:
                self.dealer.KickPlayer(name)

        if len(self.dealer.seats.Names()) < 2:
            print(f"[END] {self.dealer.seats.Names()[0]} has won!")
            return False
        
        print(f"\n[NEW ROUND]")
        self.dealer.MoveButton()
        self.dealer.TakeAnte()
        self.dealer.DealHands()
        return True

if __name__ == "__main__":
    prompt = "Press 1 to play, or 0 to spectate."
    answer = input(prompt)
    if int(answer):
        PlayGame()
    else:
        SpectateGame()