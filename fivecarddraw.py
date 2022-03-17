from functools import reduce
from itertools import groupby
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
        if len(discards) > 3 and self.ExtractProduct(remaining) % 41:
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

class Player(object):
    def __init__(self, name):
        self.name = name
        
        self.chips = 0
        
        self.has_allin = False
        self.has_folded = False
        self.has_mincalled = False
    
    def __repr__(self):
        return self.name
    

class Human(Player):
    def __init__(self, name):
        super().__init__(name)
    
    def SelectCards(self, hand):
        print(f"\nYou have {hand}.")
        
        selections = []
        for card in hand:
            selection = input(
                f"Select {card} to switch? Enter Y/N.").strip().lower()
            if selection == "y":
                selections.append(card)
        
        if len(selections) <= 3:
            return selections
        
        kept_ace = any([
            card for card in hand if 
            card not in selections and card.value_r == "A"])
         
        if len(selections) <= 4 and kept_ace:
            return selections
        
        print("Please select again.")
        return self.SelectCards(hand)
    
    def SelectAction(self, options, min_to_call, pot):   # input state, output hand
        print(f"\nThere are {sum(pot.values())} chips in the pot.")
        print(f"The amount to call is {min_to_call}.")
        print(f"You have {self.chips} chips.")
        
        prompt = ""
        for i, option in enumerate(options):
            prompt += f"Enter {i+1} to {option}. "
        
        try:
            selection = input(prompt + "\n").strip()
            return options[int(selection) - 1]
        except:
            print("Please select again.")
            return self.SelectAction(options, min_to_call, pot)
    
    def SelectRaise(self, ante, min_to_call, pot): # input state, output hand
        print(f"\nThere are {sum(pot.values())} chips in the pot.")
        print(f"The amount to call is {min_to_call}.")
        print(f"You have {self.chips} chips.")
        
        try:
            amount = input("Select how much to raise by. \n").strip()
            amount = int(amount)
            
            assert(not amount % ante or amount == self.chips - min_to_call)
            assert(amount >= 0 and amount <= self.chips - min_to_call)
            
            return amount
        except:
            print("Please select again.")
            return self.SelectRaise(ante, min_to_call, pot)
    

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

    def UpdateDealingOrder(self):
        seat = self.button["seat"]
        self.button["player"] = self.seats[seat]
        self.button["queue"] = [name for name in self.seats[seat+1:] + self.seats[:seat+1] if name]
        return self.button

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

    def NextActionPlayer(self):
        pass

    def DealingOrder(self):
        return self.button["queue"] 

    def AvailableSeats(self):
        return [i for i, occupant in enumerate(self.seats) if not occupant]

  
class Dealer(object):
    def __init__(self):
        self.cards = HandTracker()
        self.seats = SeatTracker()
        # self.tokens = TokenTracker()
        self.pot = {}
        self.ante = 0
        self.button_next = []
        
    def MoveButton(self):
        self.seats.NextButtonPlayer()
        return self.seats.button
        
    def DealHands(self):
        names = self.seats.DealingOrder()
        self.cards.DealHands(names)
        self.cards.EvaluateHands()
        return self.seats.action
    
    def EditHand(self, name, discards):
        if self.cards.ApproveDiscards(name, discards):
            self.cards.EditHand(name, discards)
            self.cards.EvaluateHand(name)
            return True
        return False
        
    def CollectCards(self):
        self.cards.CollectHands()
        
    def TakeAnte(self):
        for player in self:  
            if player.chips > self.ante:
                player.chips -= self.ante
                self.pot[player.name] = self.ante
                print(f"{player} paid {self.ante} chips for the ante.")
            elif player.chips == self.ante:
                player.chips -= self.ante
                self.pot[player.name] = self.ante
                print(f"The ante forced {player} to go all-in!")
            else:
                self.pot[player.name] = player.chips
                player.chips = 0
                print(f"The ante forced {player} to go all-in!")
                player.has_allin = True
        print("\n")
    
    def TakeBet(self, player, amount):
        min_to_call = max(self.pot.values()) - self.pot[player.name]
        
        if amount > min_to_call:
            for other_player in self:
                    other_player.has_mincalled = False
                    
            if amount == player.chips:
                print(f"{player} has raised by {amount - min_to_call} and gone allin!")
                player.has_allin = True
            else:
                print(f"{player} has raised by {amount - min_to_call}.")
                player.has_mincalled = True
                
        elif amount == min_to_call:
            if amount == 0:
                print(f"{player} has checked.")
                player.has_mincalled = True
            elif amount == player.chips:
                print(f"{player} has gone all in to call!")
                player.has_allin = True
            else:
                print(f"{player} has called.")
                player.has_mincalled = True
        
        else:
            if amount == 0:
                print(f"{player} has folded.")
                player.has_folded = True
            else:    
                print(f"{player} couldn't call but has gone all in with {amount} chips.")
                player.has_allin = True
        
        player.chips -= amount
        self.pot[player.name] += amount       
                
    def Payout(self):
        winners = {}
        
        hands = self.cards.hands
        
        players_rem = [player for player in self if not player.has_folded]
        players_rem.sort(
            key = lambda x: (hands[x.name]["rank_n"], self.pot[x.name]))
        
        splits =  [
            list(players) for _, players in groupby(
                iterable = players_rem, 
                key = lambda x : hands[x.name]["rank_n"])]       
        
        for split in splits:
            total = 0
            
            for i, winner in enumerate(split):
                if any(self.pot.values()):
                    contributers = sorted(self,
                        key = lambda x: self.pot[x.name], reverse = True)
                
                for contributer in contributers:
                    if not self.pot[contributer.name]:
                        break
                    if contributer == winner:
                        continue
                    
                    if self.pot[contributer.name] > self.pot[winner.name]:
                        total += self.pot[winner.name]
                        self.pot[contributer.name] -= self.pot[winner.name]
                    else:
                        total += self.pot[contributer.name]
                        self.pot[contributer.name] = 0
                
                total += self.pot[winner.name]
                self.pot[winner.name] = 0
                
                reward = total // (len(split) - i)
                winner.chips += reward
                total -= reward
                
                if reward:
                    winners[winner.name] = reward
        
        if len(players_rem) < 2:
            print(f"{players_rem[0]} won {winners[players_rem[0]]} chips.")
            winners.clear()
        
        i, best_rank = 0, 10000
        while winners:
            rank = hands[self[i].name]["rank_c"]
            if self[i].name in winners.keys():
                print(f"{self[i]} won {winners[self[i].name]} chips" + " " + 
                      f"with {self.cards.hands[self[i].name]['cards']} ({rank})")
                del winners[self[i].name]
            elif not self[i].has_folded:
                if hands[self[i].name]["rank_n"] <= best_rank:
                    best_rank = hands[self[i].name]["rank_n"]
                    print(f"{self[i]} mucked with {self.cards.hands[self[i].name]['cards']} ({rank})")
                else:
                    print(f"{self[i]} mucked.")   
            i += 1
        while i < len(self) and not len(players_rem) < 2:
            if not self[i].has_folded: 
                print(f"{self[i]} mucked.")
            i += 1
        
        self.pot.clear()
                        
    
class BasicAI(Player):
    def __init__(self, name):
        super().__init__(name)
    
    def SelectCards(self, hand):
        selections = []
        for card in hand:
            selection = choice([True, False])
            if selection:
                selections.append(card)
        
        if len(selections) <= 3:
            return selections
        
        kept_ace = any([
            card for card in hand if 
            card not in selections and card.value_r == "A"])
         
        if len(selections) <= 4 and kept_ace:
            return selections
        
        return self.SelectCards(hand)
    
    def SelectAction(self, options, min_to_call, pot): # state input
        return choice(options)

    def SelectRaise(self, ante, min_to_call, pot): #state input
        try:
            options = range(0, self.chips - min_to_call + 1, ante)
            return choice(options)
        except:
            print(ante, min_to_call, self.chips)

  
class FiveCardDraw(Dealer):
    def __init__(self):
        players = self.Configuration()
        super().__init__(players)
        
        for player in self:
            player.chips = 500 
        
        self.ante = 5
    
        while self.NewHand():
            self.BettingPhase()
            self.SwitchingPhase()
            self.BettingPhase()
            self.EvaluationPhase()
        else:
            self.EndGame()
    
    def Configuration(self):
        players = []
        for name in ["Phil Ivey", "Gus Hanson", "Dan Negreanu", "Phil Hellmuth"]:
            players.append(BasicAI(name))
            
        player = Human(input("What's your name?"))
        players.append(player)
        return players
    
    def NewHand(self):
        human = [player for player in self if type(player) == Human]
        
        if any(human) and not human[0].chips:
            print(f"Game over {human[0]}, better luck next time.")
            return False
        
        for player in [player for player in self if not player.chips]:
            print(f"{player} is leaving the table.")
            self.remove(player)
            
        if not len(self) - 1:
            print(f"{self[0]} has done it. Well played.")
            return False
        
        print("\n------New Round------")
        
        self.MoveButton()
        print(f"{self[-1]} has got the button.")
        
        self.TakeAnte()

        self.DealHands()
        return True
    
    def BettingPhase(self):
        unfinished = True
        players_rem = [
            player for player in self if 
            not player.has_folded and not player.has_allin]
        
        if len(players_rem) < 2:
            print("Nobody needs to bet.\n")
            unfinished = False
        
        while unfinished:
            for player in self:
                if player.has_allin or player.has_folded or player.has_mincalled:
                    continue
                
                min_to_call = max(self.pot.values()) - self.pot[player.name]
                
                if not min_to_call:
                    options = ["check", "raise", "allin"]
                elif player.chips <= min_to_call:
                    options = ["fold", "allin"]
                else:
                    options = ["fold", "call", "raise", "allin"]
                    
                action = player.SelectAction(options, min_to_call, self.pot)
                
                if action == "allin":
                    self.TakeBet(player, player.chips)
                elif action == "call":
                    self.TakeBet(player, min_to_call)
                elif action == "raise":
                    amount = (
                        min_to_call + player.SelectRaise(self.ante, min_to_call, self.pot))
                    self.TakeBet(player,amount)
                else:
                    self.TakeBet(player, 0)
            
            players_are_done = []
            for player in self:
                players_are_done.append(
                    player.has_allin or player.has_folded or player.has_mincalled)
            
            unfinished = not all(players_are_done)
            
        for player in self:
            player.has_mincalled = False
            
    def SwitchingPhase(self):
        players_rem = [player for player in self if not player.has_folded]
        
        print("\n------Mid Round------")
        if len(players_rem) < 2:
            return
        print(f"The remaining players are {players_rem}.\n")
        
        for player in self:
            if player.has_folded:
                continue
            name = player.name
            hand = self.cards.hands[name]["cards"]
            discarded_cards = player.SelectCards(hand)
            
            if len(discarded_cards):
                print(f"{player} swapped {len(discarded_cards)} cards.")
            
            self.EditHand(name, discarded_cards)
                
            if type(player) == Human:
                print(f"You have {self.cards.hands[player.name]['cards']}.\n")

           
    def EvaluationPhase(self):
        self.Payout()
        self.CollectCards()
        print("\n------End of Round------")
        for player in self:
            player.has_allin = False
            player.has_folded = False
            player.has_mincalled = False
            print(f"{player} has got {player.chips} chips.")
    
    def EndGame(self):
        print("Thanks for playing!")
        

class Simulation(FiveCardDraw):
    def __init__(self):
        super().__init__()
    
    def Configuration(self):
        players = []
        for name in ["Phil Ivey", "Gus Hanson", "Dan Negreanu", "Phil Hellmuth", "Brad Graham"]:
            players.append(BasicAI(name))
            
        return players
    
    def NewHand(self):
        if len(self) < 2:
            print("Game Over!")
            return False
        
        return super().NewHand()

if __name__ == "__main__":
    prompt = "Press 1 to play, or 0 to spectate."
    answer = input(prompt)
    if answer:
        FiveCardDraw()
    else:
        Simulation()