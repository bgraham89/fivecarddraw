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

    def __init__(self, value : int, suit : int):
        """
        Constructs all the necessary attributes for the card object.

        Parameters
        ----------
            value : card value
            suit : card suit

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
        Shuffle : 
            Shuffles order of remaining cards in deck.
        CollectCards : 
            Set the amount of cards no longer in the deck to 0.
        DepartedCards : 
            Get a list of the cards no longer in the deck.
        RemainingCards : 
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
            The t attribute is set to 0.

        """
        self.t = 0

    def DepartedCards(self) -> list[Card]:
        """
        Get a list of the cards no longer in the deck.

        """
        return self.state[:self.t]

    def RemainingCards(self) -> list[Card]:
        """
        Get a list of the cards remaining in the deck.

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
        TrackPlayers :
            Begin tracking players.
        UntrackPlayers :
            Stop tracking players.
        AssignCards :
            Associate cards with a player.
        UnassignCards :
            Stop associating cards with a player.
        DealHand :
            Get top five cards of the deck.
        DealPlayersIn :
            Deal cards to each player being tracked.
        SwapCards :
            Get a list of cards to replace some discarded cards.
        SwapPlayersCards :
            Replace the discarded cards of a tracked player.
        AllowDiscards :
            Decide if discarding chosen cards is allowed.
        CollectCards :
            Remove cards from tracked players and return them to the deck.
        ShuffleDeck :
            Shuffles order of remaining cards in deck.
        LoadData :
            Load the ratings for each possible hand in five card draw poker.
        HasFlush :
            Determines if a hand contains a flush.
        HasUnique5 :
            Determines if a hand contains five unique valued cards.
        TwosEncoding :
             Convert hand to a sum of powers of two.
        PrimesEncoding :
             Convert hand to a product of prime numbers.
        EvaluateHand :
            Get the rating of a hand.
        EvaluatePlayersIn :
            Store the rating of each tracked players hand.
        TrackedPlayers :
            Get a list of players being tracked.
        TrackedHand :
            Get a list of cards assigned to a player.

    """

    def __init__(self):
        """Constructs all the necessary attributes for the handtracker object."""
        # create a deck
        self.DECK = Deck()
        # create a state for player hand data
        self.players = {}
        # load data containing ratings of all possible five card hands
        self.LoadData()

    def TrackPlayers(self, names : list[str]):
        """
        Inserts some names into the tracker so the tracker can begin storing data about them.
        
        Parameters
        ----------
            names : the names of players
        
        Side effects
        ------------
            The players attribute gets additional keys.

        """
        # assert player is not being tracked already
        for name in names:
            if name in self.players:
                raise Exception(f"{name} is already being tracked.")
        # begin tracking players
        self.players.update({name : {"cards" : []} for name in names})

    def UntrackPlayers(self, names : list[str]):
        """
        Removes some names from the tracker.

        Parameters
        ----------
            names : the names of players
        
        Side effects
        ------------
            The players attribute loses some keys.

        """
        for name in names:
            # assert each player was being tracked
            try:
                # stop tracking player
                del self.players[name]
            except KeyError:
                raise KeyError(f"{name} is not being tracked.")

    def AssignCards(self, name : str, cards : list[Card]):
        """
        Allocates additional cards to a player.

        Parameters
        ----------
            name : the name of a player
            cards : cards to assign to the player

        Side effects
        ------------
            The players attribute has some values updated.

        """
        # assert player is being tracked
        try:
            # allocate cards to player
            self.players[name]["cards"].extend(cards)
        except KeyError:
            raise KeyError(f"{name} is not being tracked.")

    def UnassignCards(self, name : str, cards : list[Card]):
        """
        Unallocates specifric cards from a player.

        Parameters
        ----------
            name : the name of a player
            cards : cards to unassign from the player
        
        Side effects
        ------------
            The players attribute has some values updated.

        """
        # assert player is holding all cards
        if set(cards).intersection(self.Hand(name)) != set(cards):
            raise Exception(f"{name} is not holding some of {cards}.")
        
        # assert player is being tracked
        try:
            # unallocate cards from player
            self.players[name]["cards"] = [card for card in self.Hand(name) if card not in cards]
        except KeyError:
            raise KeyError(f"{name} is not being tracked.")

    def DealHand(self) -> list[Card]:
        """
        Provide five cards from the deck.
        
        Side effects
        ------------
            The DECK.t attribute is increased by five.

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
            The players attribute has some values updated.

        """
        # determine if enough cards are in the deck to deal everyone hands
        if len(self.players) * 5 > len(self.DECK):
            Exception("There are not enough cards remaining to deal all players hands.")

        # deal hands to tracked players
        for player in self.players:
            hand = self.DealHand()
            self.AssignCards(player, hand)

    def SwapCards(self, discards : list[Card]) -> list[Card]:
        """
        Provides cards to replace some discarded cards.

        Parameters
        ----------
            discards : cards to swap
        
        Side effects
        ------------
            The DECK attribute has the t attribute increased by the amount of cards being discarded.

        """
        # assert enough cards in deck
        if len(self.DECK) < len(discards):
            raise Exception(f"Not enough cards in deck to swap {discards}.")

        # get new cards and return them
        new_cards = [next(self.DECK) for _ in range(len(discards))]
        return new_cards

    def SwapPlayersCards(self, name : str, discards : list[Card]):
        """
        Provides cards to replace some cards discarded by a tracked player.

        Parameters
        ----------
            name : name of tracked player
            discards : cards to swap
        
        Side effects
        ------------
            The DECK attribute has the t attribute increased by the amount of cards being discarded.\n
            The players attribute has some values updated.

        """
        # assert enough cards in deck
        if len(self.DECK) < len(discards):
            raise Exception(f"Not enough cards in deck to swap {discards}.")

        # remove discards from hand
        self.UnassignCards(name, discards)

        # get new cards and assign to player
        new_cards = [next(self.DECK) for _ in range(len(discards))]
        self.AssignCards(name, new_cards)

    def AllowDiscards(self, hand : list[Card], discards : list[Card]) -> bool:
        """
        Decides if discarding a selection of cards from a hand is acceptible in five card draw.

        Parameters
        ----------
            hand : the hand to discard from
            discards : the selection of cards to discard
        
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
        Puts all cards back in the deck.
        
        Side effects
        ------------
            The deck attribute has the t attribute set to 0. \n
            The players attribute is cleared.

        """
        self.DECK.CollectCards()
        players = self.TrackedPlayers()
        self.UntrackPlayers(players)

    def ShuffleDeck(self):
        """
        Shuffles the remaining cards in the deck .
        
        Side effects
        ------------
            The deck attribute has the state attribute permutated.

        """
        self.DECK.Shuffle()

    def LoadData(self):
        """
        Constructs all the hand ranking attributes for the handtracker object.
        
        Side effects
        ------------
            The FLUSH_RANKS attribute is created. \n
            The UNIQUE5_RANKS attribute is created. \n
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
        # read data
        with open("data/flushes.txt", "r") as file:
            for line in file:
                # locate and encode hand as sum of powers of two
                hand = reduce(lambda x, y : x+y, map(lambda x : DV[line[int(x)]], "45678"))
                # store hand ratings by integer key 
                self.FLUSH_RANKS[hand] = []
                # store numerical rating
                self.FLUSH_RANKS[hand].append(int(str(line)[11:]))
                # store categorical rating
                self.FLUSH_RANKS[hand].append(CLASSES[str(line[:2])])

        # store ratings of all non-flush hands with 5 unique card values
        self.UNIQUE5_RANKS = {}
        # read data
        with open("data/uniquefive.txt", "r") as file:
            for line in file:
                # locate and encode hand as sum of powers of two
                hand = reduce(lambda x, y : x+y, map(lambda x : DV[line[int(x)]], "45678"))
                # store hand ratings by integer key 
                self.UNIQUE5_RANKS[hand] = []
                # store numerical rating
                self.UNIQUE5_RANKS[hand].append(int(str(line)[11:]))
                # store categorical rating
                self.UNIQUE5_RANKS[hand].append(CLASSES[str(line[:2])])

        # store ratings of all hands with duplicate card values
        self.DUPE_RANKS = {}
        # read data
        with open("data/dupes.txt", "r") as file:
            for line in file:
                # locate and encode hand as product of primes
                hand = reduce(lambda x, y : x*y, map(lambda x : DP[line[int(x)]], "45678"))
                # store hand ratings by integer key 
                self.DUPE_RANKS[hand] = []
                # store numerical rating
                self.DUPE_RANKS[hand].append(int(str(line)[11:]))
                # store categorical rating
                self.DUPE_RANKS[hand].append(CLASSES[str(line[:2])])

    def HasFlush(self, cards : list[Card]) -> bool:
        """
        Check if a hand contains a flush.

        Parameters
        ----------
            cards : hand to check
        
        """
        # look at suit bits of each card
        suit_mask = 15 << 12
        has_flush = reduce(lambda x, y : x&y, map(lambda x : int(x), cards)) & suit_mask
        return bool(has_flush)

    def HasUnique5(self, cards : list[Card]) -> bool:
        """
        Check if a hand contains five unique cards.

        Parameters
        ----------
            cards : hand to check
        
        """
        # look at value bits of each card
        values = reduce(lambda x, y : x|y, map(lambda x : int(x), cards)) >> 16
        has_unique5 = bin(values).count("1") == 5
        return has_unique5

    def TwosEncoding(self, cards : list[Card]) -> int:
        """
        Convert hand to a sum of powers of two.

        Parameters
        ----------
            cards : hand to convert
        
        """
        return reduce(lambda x, y : x|y, map(lambda x : int(x), cards)) >> 16

    def PrimesEncoding(self, cards : list[Card]) -> int:
        """
        Convert hand to a product of primes.

        Parameters
        ----------
            cards : hand to convert
        
        """
        return reduce(lambda x, y : x*y, map(lambda x : int(x) & 255, cards))

    def EvaluateHand(self, hand : list[Card]) -> tuple[int, str]:
        """
        Evaluates a hand both numerically and categorically.

        Parameters
        ----------
            hand : hand to evaluate
        
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
            hands : The players attribute has some values updated.

        """
        # evaluate hands of players being tracked and store the info
        for player in self.players:
            hand = self.Hand(player)
            rank_n, rank_c = self.EvaluateHand(hand)
            self.players[player]["rank_n"] = rank_n
            self.players[player]["rank_c"] = rank_c

    def TrackedPlayers(self) -> list:
        """
        Provides the names of players being tracked.
        
        """
        return [*self.players]

    def Hand(self, name : str) -> list[Card]:
        """
        Provides the hand of a player being tracked.
        
        """
        # assert player is being tracked and return hand
        try:
            return self.players[name]["cards"]
        except KeyError:
            raise KeyError(f"{name} is not being tracked.")


class SeatTracker(object):
    """
    A class to handle seating dynamics during a game of five card draw poker.

    Attributes
    ----------
        seats : list[str]
            seat vacancies and occupants indexed by seat number
        players : dict
            player seating data
        button : dict
            button assignment data
        L : int
            the maximum player capacity of the tracker

    Methods
    -------
        OccupySeat :
            Assign a player to a seat
        EmptySeat :
            Unassign a player from a seat
        TrackPlayers :
            Begin tracking players
        UntrackPlayers :
            Stop tracking players
        SeatPlayers :
            Assign tracked players to seats
        KickPlayers :
            Unassign tracked players from seats
        MoveButton :
            Move button to next player
        TrackButton :
            Update button data
        TrackedPlayers :
            Get list of tracked players
        AvailableSeats :
            Get list of available seats
        

    """
    def __init__(self, amount_seats : int = 5):
        """
        Constructs all the necessary attributes for the seattracker object.

        Parameters
        ----------
            amount_seats : the maximum player capacity of the game of five card draw
            
        """
        # initialise seat tracking
        self.seats = ["" for _ in range(amount_seats)]
        # initialise player tracking
        self.players = {}
        # initialise button tracking
        self.button = {"seat" : -1, "player" : ""}
        # store input parameters
        self.L = amount_seats

    def __iter__(self):
        """Converts the seatracker object to an iterator providing players in dealing order."""
        b_seat = self.button["seat"]
        return (player for player in self.seats[b_seat+1:] + self.seats[:b_seat+1] if player)

    def __len__(self):
        """Provides the amount of seats being tracked by the tracker."""
        return self.L

    def OccupySeat(self, name : str, seat : int):
        """
        Occupies a seat with a player.

        Parameters
        ----------
            name : player's name
            seat : index of seat to occupy
        
        Side effects
        ------------
            The seats attribute has an item replaced.

        """
        # assert name is unique
        if name in self.seats:
            raise Exception(f"{name} is already occupying a seat.")
        # assert seat at table
        if seat >= len(self) or seat < 0:
            raise IndexError(f"No seat with index {seat}.") 
        # assert seat is empty
        if self.seats[seat]:
            raise Exception(f"The seat is already occupied by {self.seats[seat]}.")
        # occupy seat
        self.seats[seat] = name

    def EmptySeat(self, seat : int):
        """
        Empties a seat occupied by a player.

        Parameters
        ----------
            seat : index of seat to empty
        
        Side effects
        ------------
            The seats attribute has an item replaced.

        """
        # assert seat at table
        if seat >= len(self) or seat < 0:
            raise IndexError(f"No seat with index {seat}.")
        # assert seat is occupied
        if not self.seats[seat]:
            raise Exception(f"The seat {seat} wasn't occupied.")
        # empty seat
        self.seats[seat] = ""
        
    def TrackPlayers(self, names : list[str]):
        """
        Inserts some names into the tracker so the tracker can begin storing data about them.

        Parameters
        ----------
            names : players to track
        
        Side effects
        ------------
            The players attribute gets additional keys.

        """
        for name in names:
            # assert name is unique
            if name in self.players:
                raise Exception(f"{name} is already being tracked.")
            # begin tracking
            self.players.update({name : {}})

    def UntrackPlayers(self, names : list[str]):
        """
        Removes some names from the player tracker.

        Parameters
        ----------
            names : players to stop tracking
        
        Side effects
        ------------
            The players attribute has some keys removed.

        """
        for name in names:
            # assert each player was being tracked
            try:
                # stop tracking player
                del self.players[name]
            except KeyError:
                raise KeyError(f"{names} is not being tracked.")

    def SeatPlayers(self):
        """
        Allocates seats to tracked players.

        Side effects
        ------------
            The seats attribute has items replaced. \n
            The players attribute has some values updated.

        """
        # select seats
        seats = self.AvailableSeats()
        shuffle(seats)
        # get players names to be seated
        players = [name for name in self.players if not self.players[name]]
        # assert enough seats
        if len(players) > len(seats):
            raise Exception(f"There is not enough available seats for {players}.")
        # allocate seats 
        for assignment in zip(players, seats):
            name, empty_seat = assignment
            # update seat tracker
            self.OccupySeat(name, empty_seat)
            # update player tracker
            self.players[name] = empty_seat

    def KickPlayers(self, players : list[str]):
        """
        Removes players from the game.

        Parameters
        ----------
            players : players to kick from seats
        
        Side effects
        ------------
            The seats attribute has items replaced. \n
            The players attribute has some keys deleted.

        """
        # assert players are being tracked
        for name in players:
            if name not in self.players:
                raise KeyError(f"{name} is not being tracked.")
            # update seat tracker 
            seat = self.players[name]
            self.EmptySeat(seat)
        # update player tracker
        self.UntrackPlayers(players)
        
    def TrackButton(self):
        """
        Stores information about the button seat.

        Side effects
        ------------
            The button attribute has a value updated.

        """
        b_seat = self.button["seat"]
        self.button["player"] = self.seats[b_seat]

    def MoveButton(self):
        """
        Moves the button to the next occupied seat if possible, otherwise the next empty one.

        Side effects
        ------------
            The button attribute has both values updated.

        """
        # find player to give button to if possible
        while True:
            # check each seat for a player
            seat = self.button["seat"]
            seat += 1
            seat %= len(self)
            self.button["seat"] = seat
            # stop if player is at seat or there are no seated players
            if self.seats[seat] or not self.players:
                break
        # update button tracker
        self.TrackButton()

    def TrackedPlayers(self) -> list[str]:
        """
        Provides the names of players being tracked.

        """
        return [*self.players]

    def AvailableSeats(self) -> list[int]:
        """
        Provides the seats that are unoccupied.

        """
        return [i for i, occupant in enumerate(self.seats) if not occupant]

    def OccupiedSeats(self) -> list[int]:
        """
        Provides the seats that are occupied.

        """
        return [i for i, occupant in enumerate(self.seats) if occupant]


class ChipTracker(object):
    def __init__(self):
        # initialise player and rules trackers
        self.gameinfo = {"ante" : 0}
        self.players = {}

    def __abs__(self):
        return sum([self.Contribution(player) + self.Stack(player) for player in self.players])

    def TrackPlayers(self, names):
        # initialise player tracking
        self.players = {name : {"stack" : 0, "contribution" : 0 } for name in names}

    def UntrackPlayers(self, names):
        for name in names:
            # assert each player was being tracked
            try:
                # stop tracking player
                del self.players[name]
            except KeyError:
                raise KeyError(f"{name} is not being tracked.")

    def Reward(self, name, amount):
        # assert player is being tracked
        if name not in self.players:
            raise KeyError(f"{name} is not being tracked.")
        # add chips to players stack
        self.players[name]["stack"] += amount

    def Spend(self, name, amount):
        # assert player has enough chips
        if not self.HasEnough(name, amount):
            raise ValueError(f"{name} doesn't have enough chips to pay {amount} chips.")
        # remove chips from players stack
        self.players[name]["stack"] -= amount

    def HasEnough(self, name, amount):
        # check if player has enough chips
        return True if amount <= self.players[name]["stack"] else False

    def Bet(self, name, amount):
        # remove chips from player
        self.Spend(name, amount)
        # add chips to pot
        self.players[name]["contribution"] += amount

    def CallAmount(self, name):
        # calculate how many chips a player needs to contribute, to minimum call
        return self.MaxContribution() - self.Contribution(name)

    def BetDetails(self, name, amount):
        # check if bet is players full stack
        has_allin = True if amount == self.Stack(name) else False
        # check if bet is atleast the min call amount
        min_to_call = self.CallAmount(name)
        has_mincalled = True if amount >= min_to_call else False
        if has_mincalled:
            # check if bet is more than the min call amount
            has_raised = True if amount > min_to_call else False
            has_folded = False
        else:
            # check if player didn't bet anything
            has_folded = True if not amount else False
            has_raised = False
        return {"has_raised" : has_raised, "has_allin" : has_allin, "has_mincalled" : has_mincalled, "has_folded" : has_folded}

    def GatherContributions(self, cap):
        contributions = 0
        # check contribution of each player
        for contributor in self.players:
            # take capped contributions
            if not self.Contribution(contributor):
                continue
            if self.Contribution(contributor) > cap:
                contributions += cap
                self.players[contributor]["contribution"] -= cap
            else:
                contributions += self.Contribution(contributor)
                self.players[contributor]["contribution"] = 0
        return contributions

    def SplitContributions(self, names):
        # track rewards
        rewards = {}
        # calculate rewards per player based on contributions
        contributions = 0
        # accomodate side pots
        names.sort(key = lambda x : self.Contribution(x))
        for i, name in enumerate(names):
            # check if total player contribution has been accounted for
            contribution = self.Contribution(name)
            if contribution:
                # account for contribution
                contributions += self.GatherContributions(contribution)
            # split contributions
            split = contributions // (len(names) - i)
            # reward contributions
            self.Reward(name, split)
            contributions -= split
            # track rewards
            rewards[name] = split
        return rewards

    def UpdateAnte(self, amount):
        # update ante amount
        self.gameinfo["ante"] = amount

    def PayAnte(self, player):
        ante = self.Ante()
        stack = self.Stack(player)
        # track payment details
        status = {"bet_all" : False, "bet_something" : False}
        # pay
        if ante >= stack:
            status["bet_all"] = True
            self.Bet(player, stack)
        else:
            status["bet_something"] = True
            self.Bet(player, ante)
        return status

    def TrackedPlayers(self):
        # return all tracked players
        return [*self.players]

    def SkintPlayers(self):
        # return players without chips
        return [player for player in self.players if not self.Stack(player)]

    def Stack(self, name):
        # return player stack
        return self.players[name]["stack"]

    def Contribution(self, name):
        return self.players[name]["contribution"]

    def MaxContribution(self):
        return max([self.players[name]["contribution"] for name in self.players])

    def Ante(self):
        # return ante amount 
        return self.gameinfo["ante"]

    def PotAmount(self):
        # determine and return total amount of chips in pot
        return sum([self.Contribution(name) for name in self.players])

            

class ActionTracker(object):
    def __init__(self):
        # initialise players and species tracker
        self.players = {}
        self.beings = {"humans" : [], "bots" : []}

    def UntrackPlayers(self, names):
        for name in names:
            # assert each player was being tracked
            try:
                # stop tracking player
                del self.players[name]
            except KeyError:
                raise KeyError(f"{names} is not being tracked.")

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
            if name not in self.players:
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
        return [*self.players]


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
        names = self.seats.players
        self.cards.TrackPlayers(names)
        # deal and evaluate hands and log
        self.cards.DealPlayersIn()
        self.cards.EvaluatePlayersIn()
        print(f"[CARDS] Hands have been dealt.")
        # initialise player statuses
        self.action.NewRound(names)
    
    def EditHand(self, name, discards):
        hand = self.cards.Hand(name)
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
        for name in list(self.seats):
            status = self.chips.PayAnte(name)
            amount = self.chips.Contribution(name)
            # log all-in or not
            if status["bet_all"]:
                print(f"[ANTE] The ante forced {name} to go all-in with {amount} chips!")
                self.action.SetAllIn(name)
            elif status["bet_something"]:
                print(f"[ANTE] {name} paid {amount} chips for the ante.")
    
    def TakeBet(self, name, amount):
        # act on bet request and return success or not
        # check player has enough chips
        if self.chips.HasEnough(name, amount):
            # determine action based on bet amount
            status = self.chips.BetDetails(name, amount)
            # assert action is legal
            if not any([status["has_mincalled"], status["has_allin"], status["has_folded"]]):
                return False
            # log action
            if status["has_raised"] and status["has_allin"]:
                self.action.ExtendRound()
                self.action.SetAllIn(name)
                surplass = amount - self.chips.CallAmount(name) 
                print(f"[ACTION] {name} has raised by {surplass} and gone all-in!")
            elif status["has_raised"] and status["has_mincalled"]:
                self.action.ExtendRound()
                self.action.SetMinCalled(name)
                surplass = amount - self.chips.CallAmount(name) 
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
            self.chips.Bet(name, amount)
            return True
        else:
            return False

    def PlayerInfo(self):
        # initialise info tracker and return it
        info = {}
        # add info about each player
        for name in self.seats.players:
            info[name] = {}
            info[name]["seat"] = self.seats.players[name]
            info[name]["chips"] = self.chips.players[name]
            if name in self.cards.players:
                info[name]["hand"] = self.cards.players[name]
            if name in self.action.players:
                info[name]["status"] = self.action.players[name]
        # log missing info
        if not self.action.players:
            print(f"[WARNING] Nobody has a status.")
        if not self.cards.players:
            print(f"[WARNING] Nobody has a hand.")
        return info

    def TableView(self, viewer):
        # initialise info tracker and return it
        info = {"self" : {}, "others" : {}, "game" : {}}
        for name in self.seats.players:
            # add info about viewer
            if viewer == name:
                info["self"]["seat"] = self.seats.players[name]
                info["self"]["chips"] = self.chips.players[name]
                info["self"]["status"] = self.action.players[name]
                info["self"]["hand"] = self.cards.players[name]
            else:
                # add info about other players
                info["others"][name] = {}
                info["others"][name]["seat"] = self.seats.players[name]
                info["others"][name]["chips"] = self.chips.players[name]
                info["others"][name]["status"] = self.action.players[name]
                info["others"][name]["hand"] = []
        # add info game circumstances
        info["game"]["call"] = self.chips.CallAmount(viewer)
        info["game"]["pot"] = self.chips.PotAmount()
        return info

    def KickPlayers(self, names):
        self.seats.KickPlayers(names)
        self.action.KickPlayers(names)
        self.chips.UntrackPlayers(names)
        for name in names:
            print(f"[PLAYER] {name} is leaving the table.")
         

    def CalculateRewards(self, player_info):
        pot = self.chips.PotAmount()
        # initialise rewards tracker
        rewards = {}
        # determine players who have not folded and sort them by hand rank and contribution; ascending 
        candidates = [name for name in player_info.keys() if not player_info[name]["status"]["has_folded"]]
        candidates.sort(key = lambda x : (player_info[x]["hand"]["rank_n"], player_info[x]["chips"]["contribution"]))
        # group players by hand rank
        groups = groupby(candidates, key = lambda x : player_info[x]["hand"]["rank_n"])
        # determine rewards per group
        for rank_n, players in groups:
            splits = self.chips.SplitContributions(list(players))
            rewards.update(splits)
            if sum(rewards.values()) == pot:
                break
        # return rewards tracker
        return rewards

    def Payout(self):
        # get data to determine size of rewards
        info = self.PlayerInfo()
        rewards = self.CalculateRewards(info)
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
            if self.cards.players[name]["rank_n"] <= rank_n:
                hand = self.cards.Hand(name)
                print(f"[SHOWDOWN] {name} is holding {hand}")
                rank_n = self.cards.players[name]["rank_n"]
            else:
                print(f"[SHOWDOWN] {name} mucked.")
                mucks.add(name)
        # reward players
        for name in showdown:
            reward = rewards[name]
            if reward:
                if name not in mucks:
                    hand = self.cards.players[name]["rank_c"]
                    print(f"[REWARDS] {name} won {reward} with a {hand}")
                else:
                    print(f"[REWARDS] {name} got {reward} chips back.")

    def StartingChips(self, amount):
        # give chips to all players
        names = self.TrackedPlayers()
        self.chips.TrackPlayers(names)
        for name in names:
            self.chips.Reward(name, amount)
        print(f"[SETUP] All players have been given {amount} chips.")

    def UpdateAnte(self, amount):
        # set ante amount
        self.chips.UpdateAnte(amount)
        print(f"[SETUP] The ante has been set to {amount} chips.")

    def TrackedPlayers(self):
        # return all tracked players
        return self.seats.TrackedPlayers()

    def DealingOrder(self):
        # determine order that players should take turns postflop
        return list(self.seats)

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
        for name in self.TrackedPlayers():
            print(f"[STANDINGS] {name} has got {self.chips.players[name]['stack']} chips remaining.")
    
    def SeatPlayers(self, players):
        self.seats.TrackPlayers(players)
        self.seats.SeatPlayers()

    def InitializeTable(self, humans, bots, starting_chips):
        # seat players
        players = humans + bots
        shuffle(players)
        self.SeatPlayers(players)
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
        self.dealer.UpdateAnte(self.ANTE)

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
                        print(f"[CARDS] Your new hand is {self.dealer.cards.players[name]['cards']}")
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
        self.dealer.UpdateAnte(self.ANTE)
        self.HUMAN = None
    
    def NewHand(self):
        # kick bots with few chips
        self.dealer.KickPlayers(self.dealer.SkintPlayers())

        # check amount of players remaining
        if len(self.dealer.TrackedPlayers()) < 2:
            print(f"[END] {self.dealer.TrackedPlayers()[0]} has won!")
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