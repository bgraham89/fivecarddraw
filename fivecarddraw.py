from functools import reduce
from itertools import groupby
from math import inf
from random import choice, shuffle


class Card(object):
    """
    A class to represent a card.

    Attributes
    ----------
        MASK : str
            a guide for intepreting the binary encoding of the card
        PRIMES : tuple
            a cipher for encoding the card value as a prime
        _prime : int
            the prime encoding of the card value
        _rank : int
            the decimal encoding of the card value
        _suit : int
            the binary, one hot encoding of the card suit
        _value : int
            the binary, one hot encoding of the card value
        b : int
            the binary encoding of the card that combines _prime, _rank, _suit and _value 
        value_r : str
            the str representation of card value
        suit_r : str
            thr str representation of card suit
        value_i : int
            a class parameter for the card value
        suit_i : int
            a class parameter for the card suit
    
    """

    def __init__(self, value, suit):
        """
        Constructs all the necessary attributes for the card object.

        Parameters
        ----------
            value : int
                card value
            suit : int
                card suit
        """
        # assert acceptable parameters 
        try:
            value %= 13
            suit %= 4
        except TypeError:
            raise TypeError("Card objects only allow integers as arguments.")

        # encode card as integer for fast hand ranking
        self.MASK = "xxxAKQJT98765432♣♢♡♠RRRRxxPPPPPP"
        self.PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
        
        self._prime = self.PRIMES[value]
        self._rank = value << 8
        self._suit = (2 ** suit) << 12
        self._value = (2 ** value) << 16
        
        self.b = self._prime + self._rank + self._suit + self._value
    
        # encode card as string for representation
        self.VALUES = ("2","3","4","5","6","7","8","9","10","J","Q","K","A")
        self.SUITS = "♠♡♢♣"

        self.value_r, self.suit_r = self.VALUES[value], self.SUITS[suit]
        self.r = self.value_r + self.suit_r

        # store input parameters
        self.value_i, self.suit_i = value, suit
    
    def __repr__(self):
        """Displays the card value and card suit when the card object is printed."""
        return self.r

    def __str__(self):
        """Converts the card object to a string dispalying the card value and card suit."""
        return self.r

    def __int__(self):
        """Converts the card object to an integer that encodes the card value and card suit."""
        return self.b

    def __hash__(self):
        """Creates a hash that's derived from the card value and card suit."""
        return hash((self.value_i, self.suit_i, self.b))

    def __eq__(self, other):
        """Compares the hash of the card object with others."""
        return hash(self) == hash(other)
    

class Deck(object):
    """
    A class to represent a deck of cards.

    Attributes
    ----------
        state : list[Card]
            the order of the cards in the deck
        t : int
            the amount of cards no longer in the deck

    Methods
    -------
        Shuffle():
            Shuffles order of remaining cards in deck.
        CollectCards():
            Set the amount of cards no longer in the deck to 0.
        DepartedCards():
            Get a list of the cards no longer in the deck.
        RemainingCards():
            Get a list of the cards remaining in the deck.
    """

    def __init__(self):
        """Constructs all the necessary attributes for the deck object."""
        # create list of 52 unique cards
        self.state = [Card(v, s) for v in range(13) for s in range(4)]
        # initialise tracking attribute for tracking remaining cards in deck
        self.t = 0

    def __repr__(self):
        """Displays the remaining cards in the deck when the deck object is printed."""
        return str(self.RemainingCards())

    def __str__(self):
        """Converts the deck object to a string displaying the remaining cards in the deck."""
        return str(self.RemainingCards())

    def __iter__(self):
        """Converts the deck object to an iterator providing each card of a 52-card deck."""
        return self.state

    def __next__(self):
        """Provides the top card of the deck."""
        # assert there is a remaining card in deck
        try:
            top_card = self.RemainingCards()[0]
        except IndexError:
            raise StopIteration("No more cards in the deck")

        # return first remaining card as top card and update tracker
        self.t += 1
        return top_card

    def __len__(self):
        """Provides the amount of cards remaining in deck."""
        return 52 - self.t

    def Shuffle(self):
        """
        Shuffles the order of remaining cards in deck.
        
        Side effects
        ------------
            state : list[Card]
                The state attribute is permutated.
        """
        departed_cards = self.DepartedCards()
        remaining_cards = self.RemainingCards()
        shuffle(remaining_cards)
        self.state = departed_cards + remaining_cards

    def CollectCards(self):
        """
        Set the amount of cards no longer in the deck to 0.
        
        Side effects
        ------------
            t : int
                The t attribute is set to 0.
        """
        self.t = 0

    def DepartedCards(self):
        """
        Get a list of the cards no longer in the deck.

        Return value
        ------------
            : list[Card]
        """
        return self.state[:self.t]

    def RemainingCards(self):
        """
        Get a list of the cards remaining in the deck.

        Return value
        ------------
            : list[Card]
        """
        return self.state[self.t:]


class HandTracker(object):
    """
    A class to handle card dynamics during a game of five card draw poker.

    Attributes
    ----------
        DECK : Deck
            a deck of cards
        hands : dict
            player hand data
        FLUSH_RANKS : dict
            ratings for flush hands
        UNIQUE_5_RANKS : dict
            ratings for hands with 5 unique-valued cards and different suits
        DUPE_RANKS : dict
            ratings for hands with at least one pair of cards with the same card value.

    Methods
    -------
        TrackPlayers(names):
            Begin tracking players.
        UntrackPlayers(names):
            Stop tracking players.
        AssignCards(name, cards):
            Associate cards with a player.
        UnassignCards(name, cards):
            Stop associating cards with a player.
        DealHand():
            Get top five cards of the deck.
        DealPlayersIn():
            Deal cards to each player being tracked.
        SwapCards(discards):
            Get a list of cards to replace some discarded cards.
        SwapPlayersCards(name, discards):
            Replace the discarded cards of a tracked player.
        AllowDiscards(name, hand, discards):
            Decide if discarding chosen cards is allowed.
        CollectCards():
            Remove cards from tracked players and return them to the deck.
        ShuffleDeck():
            Shuffles order of remaining cards in deck.
        LoadData():
            Load the ratings for each possible hand in five card draw poker.
        HasFlush():
            Load the ratings for each possible hand in five card draw poker.
    """

    def __init__(self):
        """Constructs all the necessary attributes for the handtracker object."""
        # create a deck
        self.DECK = Deck()
        # create a state for player hand data
        self.hands = {}
        # load data containing ratings of all possible five card hands
        self.LoadData()

    def TrackPlayers(self, names):
        """
        Inserts some names into the tracker so the tracker can begin storing data about them.
        
        Parameters
        ----------
            names : list[str]
                the names of players
        
        Side effects
        ------------
            hands : dict
                The hands attribute gets additional keys.
        """
        # assert player is not being tracked already
        for name in names:
            if name in self.hands:
                raise Exception(f"{name} is already being tracked.")
        # begin tracking players
        self.hands.update({name : {"cards" : []} for name in names})

    def UntrackPlayers(self, names):
        """
        Removes some names from the tracker.

        Parameters
        ----------
            names : list[str]
                the names of players
        
        Side effects
        ------------
            hands : dict
                The hands attribute loses some keys.
        """
        # check if all players can be untracked
        if names == self.TrackedPlayers():
            # stop tracking all players
            self.hands = {} 
        else:
            for i in range(len(names)):
                # assert each player was being tracked
                try:
                    # stop tracking player
                    del self.hands[names[i]]
                except KeyError:
                    raise KeyError(f"{names[i]} is not being tracked.")

    def AssignCards(self, name, cards):
        """
        Allocates cards to a player.

        Parameters
        ----------
            name : str
                the name of a player
            cards : list[Card]
                cards to assign to the player
        
        Side effects
        ------------
            hands : dict
                The hands attribute has some values updated.
        """
        # assert player is being tracked
        try:
            # allocate cards to player
            self.hands[name]["cards"].extend(cards)
        except KeyError:
            raise KeyError(f"{name} is not being tracked.")

    def UnassignCards(self, name, cards):
        """
        Unallocates cards from a player.

        Parameters
        ----------
            name : str
                the name of a player
            cards : list[Card]
                cards to unassign from the player
        
        Side effects
        ------------
            hands : dict
                The hands attribute has some values updated.
        """
        # assert player is holding all cards
        if set(cards).intersection(self.hands[name]["cards"]) != set(cards):
            raise Exception(f"{name} is not holding some of {cards}.")
        
        # assert player is being tracked
        try:
            # unallocate cards from player
            self.hands[name]["cards"] = [card for card in self.hands[name]["cards"] if card not in cards]
        except KeyError:
            raise KeyError(f"{name} is not being tracked.")

    def DealHand(self):
        """
        Provide five cards from the deck.
        
        Return value
        ------------
            hand : list[Card]
        
        Side effects
        ------------
            deck.t : int
                The t attribute is increased by five.
        """
        # assert enough cards are in the deck to deal
        if 5 > len(self.DECK):
            Exception("There are not enough cards remaining in the deck.")
        
        # return a five card hand
        hand = [next(self.DECK) for _ in range(5)]
        return hand

    def DealPlayersIn(self):
        """
        Provides five cards to all players being tracked.
        
        Side effects
        ------------
            hands : dict
                The hands attribute has some values updated.
        """
        # determine if enough cards are in the deck to deal everyone hands
        players = self.TrackedPlayers()
        if len(players) * 5 > len(self.DECK):
            Exception("There are not enough cards remaining to deal all players hands.")

        # deal hands to tracked players
        for player in players:
            hand = self.DealHand()
            self.AssignCards(player, hand)

    def SwapCards(self, discards):
        """
        Provides cards to replace some discarded cards.

        Parameters
        ----------
            discards : list[Card]
                cards to swap
        
        Return value
        ------------
            new_cards : list[Card]
        
        Side effects
        ------------
            deck.t : int
                The t attribute is increased by the amount of cards being discarded.
        """
        # assert enough cards in deck
        if len(self.DECK) < len(discards):
            raise Exception(f"Not enough cards in deck to swap {discards}.")

        # get new cards and return them
        new_cards = [next(self.DECK) for _ in range(len(discards))]
        return new_cards

    def SwapPlayersCards(self, name, discards):
        """
        Provides cards to replace some cards discarded by a tracked player.

        Parameters
        ----------
            name : str
                name of tracked player
            discards : list[Card]
                cards to swap
        
        Side effects
        ------------
            deck.t : int
                The t attribute is increased by the amount of cards being discarded.
            hands : dict
                The hands attribute has some values updated.
        """
        # assert enough cards in deck
        if len(self.DECK) < len(discards):
            raise Exception(f"Not enough cards in deck to swap {discards}.")

        # remove discards from hand
        self.UnassignCards(name, discards)

        # get new cards and assign to player
        new_cards = [next(self.DECK) for _ in range(len(discards))]
        self.AssignCards(name, new_cards)

    def AllowDiscards(self, hand, discards):
        """
        Decides if discarding a selection of cards from a hand is acceptible in five card draw.

        Parameters
        ----------
            hand : list[Card]
                the hand to discard from
            discards : list[Card]
                the selection of cards to discard
        
        Return value
        ------------
            : bool
        """
        # assert 5 card hands
        if len(hand) != 5 or len(discards) > 5:
            raise Exception("Unknown variant of poker.")
        # the whole hand cannot be discarded
        if len(discards) == 5:
            return False
        # if four cards are discarded the last card must be an ace
        remaining = [card for card in hand if card not in discards]
        # hand will be multiple of 41 if it has an ace, otherwise it will have a remainder 
        if len(discards) == 4 and self.PrimesEncoding(remaining) % 41: 
            return False
        # discard request approved
        return True
    
    def CollectCards(self):
        """
        Puts all cards back in the deck .
        
        Side effects
        ------------
            deck.t : int
                The t attribute is set to 0.
            hands : dict
                The hands attribute is cleared.
        """
        self.DECK.CollectCards()
        players = self.TrackedPlayers()
        self.UntrackPlayers(players)

    def ShuffleDeck(self):
        """
        Shuffles the remaining cards in the deck .
        
        Side effects
        ------------
            deck.state : list[Card]
                The state attribute is permutated.
        """
        self.DECK.Shuffle()

    def LoadData(self):
        """
        Constructs all the hand ranking attributes for the handtracker object.
        
        Side effects
        ------------
            FLUSH_RANKS : dict
                The FLUSH_RANKS attribute is created.
            UNIQUE5_RANKS : dict
                The UNIQUE5_RANKS attribute is created.
            DUPES_RANKS : dict
                The DUPES_RANKS attribute is created.
        """
        # create ciphers for reading and encoding hands for fast hand ranking
        PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
        DV = {char : 2 ** i for i, char in enumerate("23456789TJQKA")}
        DP = {char : PRIMES[i] for i, char in enumerate("23456789TJQKA")}
        CLASSES = {
            "HC" : "high card", 
            "1P" : "pair", 
            "2P" : "two pair", 
            "3K" : "three of a kind", 
            "SS" : "straight", 
            "FF" : "flush", 
            "FH" : "full house", 
            "4K" : "four of a kind", 
            "SF" : "straight flush",
            "RF" : "royal flush"}

        # store ratings of all hands with flushes
        self.FLUSH_RANKS = {}
        with open("data/flushes.txt", "r") as file:
            for line in file:
                hand = reduce(lambda x, y : x+y, map(lambda x : DV[line[int(x)]], "45678"))
                self.FLUSH_RANKS[hand] = []
                self.FLUSH_RANKS[hand].append(int(str(line)[11:]))
                self.FLUSH_RANKS[hand].append(CLASSES[str(line[:2])])

        # store ratings of all non-flush hands with 5 unique card values
        self.UNIQUE5_RANKS = {}
        with open("data/uniquefive.txt", "r") as file:
            for line in file:
                hand = reduce(lambda x, y : x+y, map(lambda x : DV[line[int(x)]], "45678"))
                self.UNIQUE5_RANKS[hand] = []
                self.UNIQUE5_RANKS[hand].append(int(str(line)[11:]))
                self.UNIQUE5_RANKS[hand].append(CLASSES[str(line[:2])])

        # store ratings of all hands with duplicate card values
        self.DUPE_RANKS = {}
        with open("data/dupes.txt", "r") as file:
            for line in file:
                hand = reduce(lambda x, y : x*y, map(lambda x : DP[line[int(x)]], "45678"))
                self.DUPE_RANKS[hand] = []
                self.DUPE_RANKS[hand].append(int(str(line)[11:]))
                self.DUPE_RANKS[hand].append(CLASSES[str(line[:2])])

    def HasFlush(self, cards):
        """
        Check if a hand contains a flush.

        Parameters
        ----------
            cards : list[Card]
                hand to check
        
        Return value
        ------------
            : bool
        """
        # look at suit bits of each card
        suit_mask = 15 << 12
        has_flush = reduce(lambda x, y : x&y, map(lambda x : int(x), cards)) & suit_mask
        return bool(has_flush)

    def HasUnique5(self, cards):
        """
        Check if a hand contains five unique cards.

        Parameters
        ----------
            cards : list[Card]
                hand to check
        
        Return value
        ------------
            has_unique5 : bool
        """
        # look at value bits of each card
        values = reduce(lambda x, y : x|y, map(lambda x : int(x), cards)) >> 16
        has_unique5 = bin(values).count("1") == 5
        return has_unique5

    def TwosEncoding(self, cards):
        """
        Convert hand to a sum of powers of two.

        Parameters
        ----------
            cards : list[Card]
                hand to convert
        
        Return value
        ------------
            : int
        """
        return reduce(lambda x, y : x|y, map(lambda x : int(x), cards)) >> 16

    def PrimesEncoding(self, cards):
        """
        Convert hand to a product of primes.

        Parameters
        ----------
            cards : list[Card]
                hand to convert
        
        Return value
        ------------
            : int
        """
        return reduce(lambda x, y : x*y, map(lambda x : int(x) & 255, cards))

    def EvaluateHand(self, hand):
        """
        Evaluates a hand.

        Parameters
        ----------
            hand : list[Card]
                hand to evaluate
        
        Return value
        ------------
            : tuple[int, str]
        """
        # assert 5 card hands
        if len(hand) != 5 :
            raise Exception("Unknown variant of poker.")

        # encode hand as int and use as key to get rank
        if self.HasFlush(hand):
            key = self.TwosEncoding(hand)
            return self.FLUSH_RANKS[key]
        elif self.HasUnique5(hand):
            key = self.TwosEncoding(hand)
            return self.UNIQUE5_RANKS[key]
        else:
            key = self.PrimesEncoding(hand)
            return self.DUPE_RANKS[key]

    def EvaluatePlayersIn(self):
        """
        Evaluates the hands of tracked players.
        
        Side effects
        ------------
            hands : dict
                The hands attribute has some values updated.
        """
        # evaluate hands of players being tracked and store the info
        for player in self.TrackedPlayers():
            hand = self.hands[player]["cards"]
            rank_n, rank_c = self.EvaluateHand(hand)
            self.hands[player]["rank_n"] = rank_n
            self.hands[player]["rank_c"] = rank_c

    def TrackedPlayers(self):
        """
        Provides the names of players being tracked.
        
        Return value
        ------------
            : dict_keys[str]
        """
        return self.hands.keys()

    def TrackedHand(self, name):
        """
        Provides the hand of a player being tracked.
        
        Return value
        ------------
            : list[Card]
        """
        # assert player is being tracked and return hand
        try:
            return self.hands[name]["cards"]
        except KeyError:
            raise KeyError(f"{name} is not being tracked.")


class SeatTracker(object):
    def __init__(self, amount_seats):
        # initialise seat tracking
        self.seats = ["" for _ in range(amount_seats)]
        # initialise player and button tracking
        self.players = {}
        self.button = {"seat" : -1, "player" : ""}
        # store input parameters
        self.l = amount_seats

    def __iter__(self):
        # seats with button seat last
        b_seat = self.button["seat"]
        return self.seats[b_seat+1:] + self.seats[:b_seat+1]

    def __len__(self):
        return self.l

    def OccupySeat(self, name, seat):
        # assert name is unique
        if name in self.seats:
            raise Exception(f"{name} is already occupying a seat.")
        # assert seat at table
        if seat >= len(self) or seat < 0:
            raise IndexError(f"No seat with index {seat}.") 
        # assert seat is empty
        if self.seats:
            raise Exception(f"The seat is already occupied by {self.seats[seat]}.")
        # occupy seat
        self.seats[seat] = name

    def EmptySeat(self, seat):
        # assert seat at table
        if seat >= len(self) or seat < 0:
            raise IndexError(f"No seat with index {seat}.")
        # assert seat is occupied
        if self.seats:
            raise Exception(f"The seat {seat} wasn't occupied.")
        # empty seat
        self.seats[seat] = ""
        
    def TrackPlayers(self, names):
        # initialise player tracking
        try:
            self.players = {name : {"seat" : self.seats.index(name)} for name in names}
        except ValueError:
            raise ValueError("Can't track players who aren't seated.")

    def UntrackPlayers(self, names):
        # stop tracking players
        if names == self.TrackedPlayers():
            self.players = {} 
        else:
            for i in range(len(names)):
                try:
                    del self.players[names[i]]
                except KeyError:
                    raise KeyError(f"{names[i]} is not being tracked.")

    def SeatPlayers(self, players):
        # select seats
        seats = self.AvailableSeats()
        shuffle(seats)
        # assert enough seats
        if len(players) > len(seats):
            raise Exception(f"There is not enough available seats for {players}.")
        for assignment in zip(players, seats):
            # occupy seats
            name, empty_seat = assignment
            self.OccupySeat(name, empty_seat)
        # track players
        self.TrackPlayers(players)

    def KickPlayers(self, names):
        for name in names:
            # assert player is seated
            if name not in self.TrackedPlayers():
                raise KeyError(f"{name} wasn't being tracked.")
            # empty seat
            seat = self.players[name]["seat"]
            self.EmptySeat(seat)
        # untrack players
        self.UntrackPlayers(names)

    def TrackButton(self):
        # store player with button if there is one
        b_seat = self.button["seat"]
        self.button["player"] = self.seats[b_seat]

    def MoveButton(self):
        # find player to give button to if possible
        while True:
            # check each seat for a player
            seat = self.button["seat"]
            seat += 1
            seat %= len(self)
            self.button["seat"] = seat
            # stop if player is at seat or there are no seated players
            if self.seats[seat] or not self.TrackedPlayers():
                break
        # update button tracker
        self.TrackButton()

    def TrackedPlayers(self):
        # return all tracked players
        return self.players.keys()

    def AvailableSeats(self):
        # return all empty seats
        return [i for i, occupant in enumerate(self.seats) if not occupant]


class ChipTracker(object):
    def __init__(self):
        # initialise player and rules trackers
        self.gameinfo = {"ante" : 0}
        self.players = {}

    def TrackPlayers(self, names):
        # initialise player tracking
        self.players = {name : {"stack" : 0, "contribution" : 0 } for name in names}

    def UntrackPlayers(self, names):
        # stop tracking players
        if names == self.TrackedPlayers():
            self.players = {} 
        else:
            for i in range(len(names)):
                try:
                    del self.players[names[i]]
                except KeyError:
                    raise KeyError(f"{names[i]} is not being tracked.")

    def AddChipsPlayer(self, name, amount):
        # determine players current stack or set it to zero.
        self.players.setdefault(name, {"stack" : 0, "contribution" : 0})
        # add chips to players stack
        self.players[name]["stack"] += amount

    def WithdrawChipsPlayer(self, name):
        # stop tracking player
        del self.players[name]

    def BetChipsPlayer(self, name, amount):
        # update players stack and contribution values
        self.players[name]["stack"] -= amount
        self.players[name]["contribution"] += amount

    def RewardChipsPlayer(self, name, amount):
        # add chips to players stack
        self.players[name]["stack"] += amount

    def ApproveBet(self, name, amount):
        # decide legality of accepting bet
        return True if amount <= self.players[name]["stack"] else False

    def AmountToCall(self, name):
        # calculate how many chips a player needs to contribute, to minimum call
        contributions = [self.players[name]["contribution"] for name in self.players.keys()]
        return max(contributions) - self.players[name]["contribution"]

    def BetStatus(self, name, amount):
        # analyse bet relative to circumstances for classifying the action taken
        min_to_call = self.AmountToCall(name)
        has_raised = True if amount > min_to_call else False
        has_allin = True if amount == self.players[name]["stack"] else False
        has_mincalled = True if amount >= min_to_call else False
        has_folded = True if min_to_call and not amount else False
        return {"has_raised" : has_raised, "has_allin" : has_allin, "has_mincalled" : has_mincalled, "has_folded" : has_folded}

    def CalculateRewards(self, player_info):
        # initialise rewards tracker
        rewards = {}
        # determine players who have not folded and sort them by hand rank and contribution; ascending 
        candidates = [name for name in player_info.keys() if not player_info[name]["status"]["has_folded"]]
        candidates.sort(key = lambda x : (player_info[x]["hand"]["rank_n"], player_info[x]["chips"]["contribution"]))
        # group players by hand rank
        candidate_splits = groupby(candidates, key = lambda x : player_info[x]["hand"]["rank_n"])
        # determine rewards per group
        for rank_n, group in candidate_splits:
            candidates = list(group)
            reward_to_split = 0
            # determine rewards per player in the group, starting from the player who contributed least to the pot
            for i, candidate in enumerate(candidates):
                # determine pot contributions that the player will get a share of
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
                # include players own chips
                reward_to_split += player_info[candidate]["chips"]["contribution"]
                player_info[candidate]["chips"]["contribution"] = 0
                # determine fraction of group rewards player will get
                candidate_reward = reward_to_split // (len(candidates) - i)
                rewards[candidate] = candidate_reward
                # remove player reward from groups reward 
                reward_to_split -= candidate_reward
        # return rewards tracker
        return rewards

    def ClearPot(self):
        # reset player contributions to zero
        for name in self.players.keys():
            self.players[name]["contribution"] = 0

    def PotTotal(self):
        # determine and return total amount of chips in pot
        return sum([self.players[name]["contribution"] for name in self.players.keys()])

    def ChipStacks(self):
        # return player stacks
        return {name : self.players[name]["stack"] for name in self.players}

    def SetAnte(self, amount):
        # update ante amount
        self.gameinfo["ante"] = amount

    def GetAnte(self):
        # return ante amount 
        return self.gameinfo["ante"]

    def CheckAnte(self, player):
        # analyse ante relative to player stack for classifying action
        status = {"bet_all" : False, "bet_something" : False, "bet_nothing" : False}
        if self.GetAnte() == self.players[player]["stack"]:
            status["bet_all"] = True
        elif self.GetAnte() < self.players[player]["stack"]:
            status["bet_something"] = True
        else:
            status["bet_nothing"] = True
        return status

    def TrackedPlayers(self):
        # return all tracked players
        return self.players.keys()

    def SkintPlayers(self):
        return [player for player in self.TrackedPlayers() if self.ChipStacks(player) < self.GetAnte()]
            

class ActionTracker(object):
    def __init__(self):
        # initialise players and species tracker
        self.players = {}
        self.beings = {"humans" : [], "bots" : []}

    def UntrackPlayers(self, names):
        # stop tracking players
        if names == self.TrackedPlayers():
            self.players = {} 
        else:
            for i in range(len(names)):
                try:
                    del self.players[names[i]]
                except KeyError:
                    raise KeyError(f"{names[i]} is not being tracked.")

    def NewRound(self, names):
        # set players statuses to false
        for name in names:
            self.players[name] = {"has_allin" : False, "has_mincalled" : False, "has_folded" : False}

    def ExtendRound(self):
        # set players statuses to have not mincalled
        for name in self.players.keys():
            self.players[name]["has_mincalled"] = False

    def AddHumans(self, names):
        # start tracking humans
        for name in names:
            self.beings["humans"].append(name)
    
    def AddBots(self, names):
        # start tracking bots
        for name in names:
            self.beings["bots"].append(name)

    def KickBot(self, name):
        # stop tracking bot
        self.beings["bots"].remove(name)
        if name in self.players:
            del self.players[name]

    def KickPlayers(self, names):
        for name in names:
            # assert player is seated
            if name not in self.TrackedPlayers():
                raise KeyError(f"{name} wasn't being tracked.")
            # kick bot
            self.KickBot(name)
        # untrack players
        self.UntrackPlayers(names)

    def SelectAmount(self, name, info):
        # determine species and get a bet amount request
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
        # determine species to ask for discards from
        if name in self.beings["humans"]:
            # give info and get user input from human
            print(f"[INFO] Your cards are {info['self']['hand']['cards']}")
            mask = input("Which cards would you like to swap? (00000 for none, 11111 for all)")
            discards =  [info['self']['hand']['cards'][i] for i, v in enumerate(mask) if int(v)]
        else:
            # get random input from bots
            discards = [info['self']['hand']['cards'][i] for i in range(5) if choice([True,False])]
        return discards

    def SetAllIn(self, name):
        # record player has gone all in
        self.players[name]["has_allin"] = True

    def SetMinCalled(self, name):
        # record player has min called
        self.players[name]["has_mincalled"] = True

    def SetFolded(self, name):
        # record player has folded
        self.players[name]["has_folded"] = True

    def PlayerHasActed(self, name):
        # determine if player needs to take an action
        return any(self.players[name].values())

    def ShowdownPlayers(self, dealing_order):
        # return players who have not folded
        return [name for name in dealing_order if name and not self.players[name]["has_folded"]]

    def ActingPlayers(self, action_order):
        # return players who have not folded or gone all in
        return [name for name in action_order if name and not self.players[name]["has_folded"] and not self.players[name]["has_allin"]]

    def TrackedPlayers(self):
        return self.players.keys()


class Dealer(object):
    def __init__(self, num_seats=6):
        # initialise trackers
        self.cards = HandTracker()
        self.seats = SeatTracker(num_seats)
        self.chips = ChipTracker()
        self.action = ActionTracker()
        
    def MoveButton(self):
        # move button to next player and log
        self.seats.MoveButton()
        player = self.seats.button["player"]
        print(f"[BUTTON] The button was given to {player}.")

    def ShuffleDeck(self):
        self.cards.ShuffleDeck()
        print(f"[CARDS] The deck has been shuffled.")
        
    def DealHands(self):
        # determine players in the round and begin tracking
        names = self.seats.TrackedPlayers()
        self.cards.TrackPlayers(names)
        # deal and evaluate hands and log
        self.cards.DealPlayersIn()
        self.cards.EvaluatePlayersIn()
        print(f"[CARDS] Hands have been dealt.")
        # initialise player statuses
        self.action.NewRound(names)
    
    def EditHand(self, name, discards):
        hand = self.cards[name]["cards"]
        # act on discard request and return success or not
        if self.cards.AllowDiscards(hand, discards):
            self.cards.SwapPlayersCards(name, discards)
            self.cards.EvaluatePlayersIn()
            # log approved request
            if discards:
                print(f"[CARDS] {name} swapped {len(discards)} cards.")
            else:
                print(f"[CARDS] {name} didn't swap any cards.")
            return True
        return False
        
    def CollectCards(self):
        # collect all cards and log
        self.cards.CollectCards()
        print(f"[CARDS] Cards have been collected.")
        
    def TakeAnte(self):
        # take ante from players
        for name in self.seats:
            if not name:
                continue
            amount = self.chips.GetAnte()
            status = self.chips.CheckAnte(name)
            # log all-in or not
            if status["bet_all"]:
                print(f"[ANTE] The ante forced {name} to go all-in with {amount} chips!")
                self.action.SetAllIn(name)
            elif status["bet_something"]:
                print(f"[ANTE] {name} paid {amount} chips for the ante.")
            self.chips.BetChipsPlayer(name, amount)
    
    def TakeBet(self, name, amount):
        # act on bet request and return success or not
        # check player has enough chips
        if self.chips.ApproveBet(name, amount):
            # determine action based on bet amount
            status = self.chips.BetStatus(name, amount)
            # assert action is legal
            if not any([status["has_mincalled"], status["has_allin"], status["has_folded"]]):
                return False
            # log action
            if status["has_raised"] and status["has_allin"]:
                self.action.ExtendRound()
                self.action.SetAllIn(name)
                surplass = amount - self.chips.AmountToCall(name) 
                print(f"[ACTION] {name} has raised by {surplass} and gone all-in!")
            elif status["has_raised"] and status["has_mincalled"]:
                self.action.ExtendRound()
                self.action.SetMinCalled(name)
                surplass = amount - self.chips.AmountToCall(name) 
                print(f"[ACTION] {name} has raised by {surplass}.")
            elif status["has_allin"] and status["has_mincalled"]:
                self.action.SetAllIn(name)
                print(f"[ACTION] {name} has gone all-in to call!")
            elif status["has_mincalled"] and amount == 0:
                self.action.SetMinCalled(name)
                print(f"[ACTION] {name} has checked.")
            elif status["has_mincalled"]:
                self.action.SetMinCalled(name)
                print(f"[ACTION] {name} has called.")
            elif status["has_folded"]:
                self.action.SetFolded(name)
                print(f"[ACTION] {name} has folded.")
            elif status["has_allin"]:
                self.action.SetAllIn(name)
                print(f"[ACTION] {name} couldn't call but has gone all-in.")
            self.chips.BetChipsPlayer(name, amount)
            return True
        else:
            return False

    def PlayerInfo(self):
        # initialise info tracker and return it
        info = {}
        # add info about each player
        for name in self.seats.TrackedPlayers():
            info[name] = {}
            info[name]["seat"] = self.seats.players[name]
            info[name]["chips"] = self.chips.players[name]
            if name in self.cards.hands:
                info[name]["hand"] = self.cards.hands[name]
            if name in self.action.players:
                info[name]["status"] = self.action.players[name]
        # log missing info
        if not self.action.players:
            print(f"[WARNING] Nobody has a status.")
        if not self.cards.hands:
            print(f"[WARNING] Nobody has a hand.")
        return info

    def TableView(self, viewer):
        # initialise info tracker and return it
        info = {"self" : {}, "others" : {}, "game" : {}}
        for name in self.seats.TrackedPlayers():
            # add info about viewer
            if viewer == name:
                info["self"]["seat"] = self.seats.players[name]
                info["self"]["chips"] = self.chips.players[name]
                info["self"]["status"] = self.action.players[name]
                info["self"]["hand"] = self.cards.hands[name]
            else:
                # add info about other players
                info["others"][name] = {}
                info["others"][name]["seat"] = self.seats.players[name]
                info["others"][name]["chips"] = self.chips.players[name]
                info["others"][name]["status"] = self.action.players[name]
                info["others"][name]["hand"] = []
        # add info game circumstances
        info["game"]["call"] = self.chips.AmountToCall(viewer)
        info["game"]["pot"] = self.chips.PotTotal()
        return info

    def KickPlayers(self, names):
        self.seats.KickPlayers(names)
        self.action.KickPlayers(names)
        self.chips.UntrackPlayers(names)
        for name in names:
            print(f"[PLAYER] {name} is leaving the table.")
         
    def Payout(self):
        # get data to determine size of rewards
        info = self.PlayerInfo()
        rewards = self.chips.CalculateRewards(info)
        # get info to determine order to pay rewards
        showdown = self.action.ShowdownPlayers(self.seats)
        
        # check if hand reveal step can be skipped
        if len(rewards) < 2:
            winner = showdown[0]
            print(f"[SHOWDOWN] {winner} won {rewards[winner]} chips.")
            return True
        
        # determine which players should reveal hands
        mucks = set([])
        i, rank_n = 0, inf
        for name in showdown:
            if self.cards.hands[name]["rank_n"] <= rank_n:
                hand = self.cards.hands[name]["cards"]
                print(f"[SHOWDOWN] {name} is holding {hand}")
                rank_n = self.cards.hands[name]["rank_n"]
            else:
                print(f"[SHOWDOWN] {name} mucked.")
                mucks.add(name)
        # reward players
        for name in showdown:
            reward = rewards[name]
            if reward:
                if name not in mucks:
                    hand = self.cards.hands[name]["rank_c"]
                    print(f"[REWARDS] {name} won {reward} with a {hand}")
                else:
                    print(f"[REWARDS] {name} got {reward} chips back.")
                self.chips.RewardChipsPlayer(name, reward)
        # reset pot contributions
        self.chips.ClearPot()

    def StartingChips(self, amount):
        # give chips to all players
        for name in self.seats.TrackedPlayers():
            self.chips.AddChipsPlayer(name, amount)
        print(f"[SETUP] All players have been given {amount} chips.")

    def SetAnte(self, amount):
        # set ante amount
        self.chips.SetAnte(amount)
        print(f"[SETUP] The ante has been set to {amount} chips.")

    def TrackedPlayers(self):
        # return all tracked players
        return self.seats.TrackedPlayers()

    def DealingOrder(self):
        # determine order that players should take turns postflop
        return [occupant for occupant in self.seats if occupant]

    def PreflopOrder(self):
        # determine order that players should take turns preflop
        name = self.DealingOrder()[2 % len(self.TrackedPlayers())]
        seat = self.players[name]["seat"]
        queue = [name for name in self.seats[seat:] + self.seats[:seat] if name]
        # return order that players should take turns preflop
        return queue

    def SkintPlayers(self):
        return self.chips.SkintPlayers()

    def Summary(self):
        # log summary of player chips
        for name in self.seats.TrackedPlayers():
            print(f"[STANDINGS] {name} has got {self.chips.players[name]['stack']} chips remaining.")

    def InitializeTable(self, humans, bots, starting_chips):
        # seat players
        players = humans + bots
        shuffle(players)
        self.seats.SeatPlayers(players)
        # track species
        self.action.AddHumans(humans)
        self.action.AddBots(bots)
        # give chips to players
        self.StartingChips(starting_chips)


class PlayGame(object):
    def __init__(self, chips=500, ante=5, opponents=["Phil Ivey", "Gus Hanson", "Dan Negreanu", "Phil Hellmuth"]):
        # store input parameters
        self.OPPONENTS = opponents
        self.CHIPS = chips
        self.ANTE = ante
        
        # initialise game 
        self.Configuration()

        # gameloop
        while self.NewHand():
            self.BettingPhase("preflop")
            self.SwitchingPhase()
            self.BettingPhase("postflop")
            self.EvaluationPhase()
        else:
            self.EndGame()

    def Configuration(self):
        # initialise dealer
        self.dealer = Dealer(len(self.OPPONENTS)+1)
        # get name and begin tracking human
        player = input("What's your name?")
        self.HUMAN = player
        # initialise table and economy
        self.dealer.InitializeTable([player], self.OPPONENTS, self.CHIPS)
        self.dealer.SetAnte(self.ANTE)

    def NewHand(self):
        # check human has chips
        if not self.dealer.chips.players[self.HUMAN]["stack"]:
            print(f"[END] Game over {self.HUMAN}, better luck next time.")
            return False

        # kick bots with few chips
        self.dealer.KickPlayers(self.dealer.SkintPlayers())

        # check amount of players remaining
        if len(self.dealer.TrackedPlayers()) < 2:
            print(f"[END] {self.HUMAN} has won!")
            return False

        # begin new round
        print(f"\n[NEW ROUND]")
        self.dealer.ShuffleDeck()
        self.dealer.MoveButton()
        self.dealer.TakeAnte()
        self.dealer.DealHands()
        return True

    def BettingPhase(self, phase):
        # determine betting order
        if phase == "preflop":
            action_order = self.dealer.PreflopOrder()
        if phase == "postflop":
            action_order = self.dealer.DealingOrder()
        
        # determine if betting phase can be skipped
        if len(self.dealer.action.ActingPlayers(action_order)) < 2:
            return True

        # begin betting loop
        unfinished = True
        while unfinished:
            # check if each player needs to act
            for name in action_order:
                # skip player if no action is needed
                if self.dealer.action.PlayerHasActed(name):
                    continue
                # get action from player
                info = self.dealer.TableView(name)
                while True:
                    amount = self.dealer.action.SelectAmount(name, info)
                    if self.dealer.TakeBet(name, amount):
                        break
            # track if more actions are needed
            players_are_done = [self.dealer.action.PlayerHasActed(name) for name in action_order]
            unfinished = not all(players_are_done)

        # update player statuses for next round
        self.dealer.action.ExtendRound()
        return True

    def SwitchingPhase(self):
        # determine if switching phase can be skipped
        dealing_order = self.dealer.seats
        if len(self.dealer.action.ShowdownPlayers(dealing_order)) < 2:
            return True

        # begin switching loop
        for name in dealing_order:
            # check if player is allowed to switch cards
            if self.dealer.action.players[name]["has_folded"]:
                continue
            # get action from player
            info = self.dealer.TableView(name)
            while True:
                discards = self.dealer.action.SelectDiscards(name, info)
                if self.dealer.EditHand(name, discards):
                    if name == self.HUMAN and discards:
                        print(f"[CARDS] Your new hand is {self.dealer.cards.hands[name]['cards']}")
                    break
        return True

    def EvaluationPhase(self):
        # reward players, collect cards and log player standings
        self.dealer.Payout()
        self.dealer.CollectCards()
        self.dealer.Summary()
    
    def EndGame(self):
        print("[END] Thanks for playing!")


class SpectateGame(PlayGame):
    def __init__(self):
        # initialise humanless game
        super().__init__()
    
    def Configuration(self):
        # configure game
        self.dealer = Dealer(len(self.OPPONENTS))
        humans = []
        self.dealer.InitializeTable(humans, self.OPPONENTS, self.CHIPS)
        self.dealer.SetAnte(self.ANTE)
        self.HUMAN = None
    
    def NewHand(self):
        # kick bots with few chips
        self.dealer.KickPlayers(self.dealer.SkintPlayers())

        # check amount of players remaining
        if len(self.dealer.seats.TrackedPlayers()) < 2:
            print(f"[END] {self.dealer.seats.TrackedPlayers()[0]} has won!")
            return False
        

        # begin new round
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