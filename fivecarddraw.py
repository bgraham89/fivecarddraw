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

    def AmountRemaining(self):
        return 52 - self.t

    def RestartIterator(self):
        self.t = 0
        return self


class Player(object):
    def __init__(self, name):
        self.name = name
        
        self.chips = 0
        self.hand = None
        
        self.has_allin = False
        self.has_folded = False
        self.has_mincalled = False
    
    def __repr__(self):
        return self.name
    

class Human(Player):
    def __init__(self, name):
        super().__init__(name)
    
    def SelectCards(self):
        print(f"\nYou have {self.hand}.")
        
        selections = []
        for card in self.hand:
            selection = input(
                f"Select {card} to switch? Enter Y/N.").strip().lower()
            if selection == "y":
                selections.append(card)
        
        if len(selections) <= 3:
            return selections
        
        kept_ace = any([
            card for card in self.hand if 
            card not in selections and card.value_r == "A"])
         
        if len(selections) <= 4 and kept_ace:
            return selections
        
        print("Please select again.")
        return self.SelectCards()
    
    def SelectAction(self, options, min_to_call, pot):
        print(f"\nThere are {sum(pot.values())} chips in the pot.")
        print(f"The amount to call is {min_to_call}.")
        print(f"You have {self.chips} chips.")
        print(f"You have {self.hand}.")
        
        prompt = ""
        for i, option in enumerate(options):
            prompt += f"Enter {i+1} to {option}. "
        
        try:
            selection = input(prompt + "\n").strip()
            return options[int(selection) - 1]
        except:
            print("Please select again.")
            return self.SelectAction(options, min_to_call, pot)
    
    def SelectRaise(self, ante, min_to_call, pot):
        print(f"\nThere are {sum(pot.values())} chips in the pot.")
        print(f"The amount to call is {min_to_call}.")
        print(f"You have {self.chips} chips.")
        print(f"You have {self.hand}.")
        
        try:
            amount = input("Select how much to raise by. \n").strip()
            amount = int(amount)
            
            assert(not amount % ante or amount == self.chips - min_to_call)
            assert(amount >= 0 and amount <= self.chips - min_to_call)
            
            return amount
        except:
            print("Please select again.")
            return self.SelectRaise(ante, min_to_call, pot)
    

class Table(list):
    def __init__(self, players):
        self.extend(players)
        
        self.deck = Deck()
        self.pot = {} 

  
class Dealer(Table):
    def __init__(self, players):
        super().__init__(players)
        self.VALUES = {char : 2 ** i for i, char in enumerate("23456789TJQKA")}
        self.PRIMES = {
            char : p for char, p in zip("23456789TJQKA", Card(0,0).PRIMES)}
        
        self.FLUSH_RANKS = {
            self.VALUES[line[4]] | self.VALUES[line[5]] | 
            self.VALUES[line[6]] | self.VALUES[line[7]] | 
            self.VALUES[line[8]] : int(str(line)[11:]) 
            for line in open("lookup-tables/flush lookup.txt", "r")}
        
        self.UNIQUE_FIVE_RANKS = {
            self.VALUES[line[4]] | self.VALUES[line[5]] | 
            self.VALUES[line[6]] | self.VALUES[line[7]] | 
            self.VALUES[line[8]] : int(str(line)[11:]) 
            for line in open("lookup-tables/unique five lookup.txt", "r")}
        
        self.DUPE_RANKS = {
            self.PRIMES[line[4]] * self.PRIMES[line[5]] * 
            self.PRIMES[line[6]] * self.PRIMES[line[7]] * 
            self.PRIMES[line[8]] : int(str(line)[11:]) 
            for line in open("lookup-tables/dupe lookup.txt", "r")}
        
        self.ante = 0
        
        self.button_next = []
        
    def MoveButton(self):
        if not self.button_next:
            self.button_next = self[0]
            
        if self.button_next == self[0]:
            self.append(self.pop(0))
            self.button_next = self[0]
        
    def DealHands(self):
        cards = {player.name : [] for player in self}
        for c in range(5):
            for player in self:
                cards[player.name].append(next(self.deck))
                if c == 4:
                    player.hand = Hand(cards[player.name])
                    
    def EvaluateHands(self):
        ranks = {}
        for player in self:
            flush = (
                player.hand[0].b & player.hand[1].b & player.hand[2].b &
                player.hand[3].b & player.hand[4].b & (15 << 12))
            
            if flush:
                key = (
                    player.hand[0].b | player.hand[1].b | player.hand[2].b | 
                    player.hand[3].b | player.hand[4].b) >> 16
                rank = self.FLUSH_RANKS[key]
                ranks[player.name] = rank
                continue
            
            unique5 = bin((
                player.hand[0].b | player.hand[1].b | player.hand[2].b |
                player.hand[3].b | player.hand[4].b) >> 16).count("1") == 5
            
            if unique5:
                key = (
                    player.hand[0].b | player.hand[1].b | player.hand[2].b | 
                    player.hand[3].b | player.hand[4].b) >> 16 
                rank = self.UNIQUE_FIVE_RANKS[key]
                ranks[player.name] = rank
                continue
           
            key = (
                (player.hand[0].b & 255) * (player.hand[1].b & 255) * 
                (player.hand[2].b & 255) * (player.hand[3].b & 255) * 
                (player.hand[4].b & 255))
            rank = self.DUPE_RANKS[key]
            ranks[player.name] = rank
        return ranks
            
    def CollectCards(self):
        for player in self:
            player.hand = None
                
    def ShuffleDeck(self):
        self.deck.Shuffle()
        
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
        
        rankings = self.EvaluateHands()
        
        players_rem = [player for player in self if not player.has_folded]
        players_rem.sort(
            key = lambda x: (rankings[x.name], self.pot[x.name]))
        
        splits =  [
            list(players) for _, players in groupby(
                iterable = players_rem, 
                key = lambda x : rankings[x.name])]       
        
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
            print(f"{players_rem[0]} won {winners[players_rem[0].name]} chips.")
            winners.clear()
        
        i, best_rank = 0, 10000
        while winners:
            rank = self.Lookup(rankings[self[i].name])
            if self[i].name in winners.keys():
                print(f"{self[i]} won {winners[self[i].name]} chips" + " " + 
                      f"with {self[i].hand} ({rank})")
                del winners[self[i].name]
            elif not self[i].has_folded:
                if rankings[self[i].name] <= best_rank:
                    best_rank = rankings[self[i].name]
                    print(f"{self[i]} mucked with {self[i].hand} ({rank})")
                else:
                    print(f"{self[i]} mucked.")   
            i += 1
        while i < len(self) and not len(players_rem) < 2:
            if not self[i].has_folded: 
                print(f"{self[i]} mucked.")
            i += 1
        
        self.pot.clear()
        
    def Lookup(self, ranking):
        if 6186 <= ranking:
            return "high card"
        elif 3326 <= ranking and ranking <= 6187:
            return "pair"
        elif 2468 <= ranking and ranking <= 3325:
            return "two pair"
        elif 1610 <= ranking and ranking <= 2467:
            return "three of a kind"
        elif 1600 <= ranking and ranking <= 1609:
            return "straight"
        elif 323 <= ranking and ranking <= 1599:
            return "flush"
        elif 167 <= ranking and ranking <= 322:
            return "full house"
        elif 11 <= ranking and ranking <= 166:
            return "four of a kind"
        elif 2 <= ranking and ranking <= 10:
            return "straigh flush"
        else:
            return "royal flush"
                    

class Hand(list):
    def __init__(self, cards):
        self.extend(cards)
        
        self.cards_r = " ".join([str(card) for card in self])
        
    def __repr__(self):
        return self.cards_r     
    
    
class BasicAI(Player):
    def __init__(self, name):
        super().__init__(name)
    
    def SelectCards(self):
        selections = []
        for card in self.hand:
            selection = choice([True, False])
            if selection:
                selections.append(card)
        
        if len(selections) <= 3:
            return selections
        
        kept_ace = any([
            card for card in self.hand if 
            card not in selections and card.value_r == "A"])
         
        if len(selections) <= 4 and kept_ace:
            return selections
        
        return self.SelectCards()
    
    def SelectAction(self, options, min_to_call, pot):
        return choice(options)

    def SelectRaise(self, ante, min_to_call, pot):
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
        self.ShuffleDeck()
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

            discarded_cards = player.SelectCards()
            kept_cards = [
                card for card in player.hand if card not in discarded_cards]
            
            if len(discarded_cards):
                print(f"{player} swapped {len(discarded_cards)} cards.")
            
            new_cards = []
            for _ in range(len(discarded_cards)):
                new_cards.append(next(self.deck))
                
            player.hand = Hand(kept_cards + new_cards)
            if type(player) == Human:
                print(f"You have {player.hand}.\n")

           
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