import unittest
from fivecarddraw import Card, HandTracker

class HandTrackerTest(unittest.TestCase):
    def setUp(self):
        self.tracker = HandTracker()


    def testPlayerTracking(self):
        # untrack all players at a time
        for i in range(10):
            # different amounts of players
            names = [f"{j}" for j in range(i+1)]
            self.tracker.TrackPlayers(names)
            # check correct amount of players tracked
            self.assertEqual(len(self.tracker.TrackedPlayers()), len(names))
            # check correct hash of players tracked
            self.assertEqual(set(names), set(self.tracker.TrackedPlayers()))
            # check all players are forgotten
            self.tracker.UntrackPlayers(names)
            self.assertEqual(len(self.tracker.TrackedPlayers()), 0)

        # untrack one player at a time
        for i in range(10):
            # different amounts of players
            names = [f"{j}" for j in range(i+1)]
            self.tracker.TrackPlayers(names)
            num_tracked = len(self.tracker.TrackedPlayers())
            # individual players
            for name in names:
                self.tracker.UntrackPlayers(name)
                # check player no longer tracked
                self.assertNotIn(name, self.tracker.TrackedPlayers())
                # check only one player is forgotten
                num_tracked -= 1
                self.assertEqual(len(self.tracker.TrackedPlayers()), num_tracked)
            # check all players are forgotten
            self.assertEqual(num_tracked, 0)

        # check can't forget a player if not tracked
        names = [f"{i}" for i in range(10)]
        self.tracker.TrackPlayers(names)
        self.assertRaises(KeyError, self.tracker.UntrackPlayers, names=["10"])


    def testCardAssignment(self):
        # tracking players
        names = [f"{i}" for i in range(10)]
        self.tracker.TrackPlayers(names)

        # check cant assign or unassign to player if not tracked
        no_cards = []
        self.assertRaises(KeyError, self.tracker.AssignCards, name="10", cards=no_cards)
        self.assertRaises(KeyError, self.tracker.UnassignCards, name="10", cards=no_cards)

        # implicit hand dealing
        assigned_cards = []
        for _ in range(5):
            card, player = next(self.tracker.DECK), names[0]
            self.tracker.AssignCards(player, [card])
            assigned_cards += [card]
            # check single card assignment
            self.assertIn(card, self.tracker.Hand(player))
            self.assertEqual(len(self.tracker.Hand(player)), len(assigned_cards))

        # implicit hand collection
        num_cards = len(assigned_cards)
        for card in assigned_cards:
            self.tracker.UnassignCards(player, [card])
            num_cards -= 1
            # check single card unassignment
            self.assertNotIn(card, self.tracker.Hand(player))
            self.assertEqual(len(self.tracker.Hand(player)), num_cards)
        # check all cards unassigned
        self.assertEqual(len(self.tracker.Hand(player)), 0)

        # check cant unassign card not assigned to player
        self.assertRaises(Exception, self.tracker.UnassignCards, name="1", cards=[card])


    def testDealing(self):
        # 1000 hands
        for _ in range(100):
            self.tracker.ShuffleDeck()
            # 10 hands per deck
            for _ in range(10):
                hand = self.tracker.DealHand()
                # check hand size
                self.assertEqual(len(hand), 5)
                for card in hand:
                    # check each card is a card
                    self.assertIsInstance(card, Card)
                    # check each card not in deck anymore
                    self.assertNotIn(card, self.tracker.DECK.RemainingCards())
                    # check each card categorised as departed
                    self.assertIn(card, self.tracker.DECK.DepartedCards())
                    # check each card is unique in deck
                    self.assertEqual(self.tracker.DECK.DepartedCards().count(card), 1)
                    # check each card is unique in hand
                    self.assertEqual(hand.count(card), 1)
            self.tracker.CollectCards()

        # 1000 more hands
        for _ in range(100):
            self.tracker.ShuffleDeck()
            # 10 dealt in players
            names = [f"{j}" for j in range(10)]
            self.tracker.TrackPlayers(names)
            self.tracker.DealPlayersIn()
            for name in self.tracker.TrackedPlayers():
                hand = self.tracker.players[name]["cards"]
                # check hand size
                self.assertEqual(len(hand), 5)
                for card in hand:
                    # check each card is a card
                    self.assertIsInstance(card, Card)
                    # check each card not in deck anymore
                    self.assertNotIn(card, self.tracker.DECK.RemainingCards())
                    # check each card categorised as departed
                    self.assertIn(card, self.tracker.DECK.DepartedCards())
                    # check each card is unique in deck
                    self.assertEqual(self.tracker.DECK.DepartedCards().count(card), 1)
                    # check each card is unique in hand
                    self.assertEqual(hand.count(card), 1)
            self.tracker.CollectCards()


    def testDiscardCriteria(self):
        # 1000 hands
        for _ in range(100):
            self.tracker.ShuffleDeck()
            # 10 hands per deck
            for _ in range(10):
                hand = self.tracker.DealHand()
                # check hand must have 5 cards
                self.assertRaises(Exception, self.tracker.AllowDiscards, hand=hand[1:], discards=hand[0])

                # check discarding 5 cards is not allowed
                self.assertFalse(self.tracker.AllowDiscards(hand, hand))
                # check discarding less 3 or less is allowed
                self.assertTrue(self.tracker.AllowDiscards(hand, hand[:3]))
                self.assertTrue(self.tracker.AllowDiscards(hand, hand[:2]))
                self.assertTrue(self.tracker.AllowDiscards(hand, hand[:1]))
                self.assertTrue(self.tracker.AllowDiscards(hand, hand[:0]))
                # check discarding 4 is only allowed if ace remains
                if str(hand[4])[0] == "A":
                    self.assertTrue(self.tracker.AllowDiscards(hand, hand[:4]))
                else:
                    self.assertFalse(self.tracker.AllowDiscards(hand, hand[:4]))
            self.tracker.CollectCards()


    def testSwapping(self):
        # untracked swaps
        self.tracker.ShuffleDeck()
        hand = self.tracker.DealHand()
        # repeat 5 times to exhaust deck
        for i in range(5):
            # allowed cardinality of discards
            for j in range(4):
                if i == 4 and j == 3:
                    # check cards can not be swapped if not enough cards remaining in deck
                    self.assertRaises(Exception, self.tracker.SwapCards, hand[:j+1])
                else:
                    cards = self.tracker.SwapCards(hand[:j+1])
                    # check correct amount of cards is returned
                    self.assertEqual(len(cards), j+1)
                    # check each card is unique
                    self.assertEqual(len(set(cards)), j+1)
                    # check each card not in original hand
                    self.assertFalse(set(cards).intersection(set(hand)))
                    for card in cards:
                        # check each card not in deck anymore
                        self.assertNotIn(card, self.tracker.DECK.RemainingCards())
                        # check each card categorised as departed
                        self.assertIn(card, self.tracker.DECK.DepartedCards())
                        # check each card is unique in deck
                        self.assertEqual(self.tracker.DECK.DepartedCards().count(card), 1)
        self.tracker.CollectCards()

        # tracked swaps
        self.tracker.ShuffleDeck()
        names = [f"{i}" for i in range(3)]
        self.tracker.TrackPlayers(names)
        self.tracker.DealPlayersIn()
        # tracked players
        for name in names:
            # allowed cardinality of discards
            for j in range(4):
                discards = self.tracker.Hand(name)[:j+1]
                self.tracker.SwapPlayersCards(name, discards)
                # check correct amount of cards is returned
                self.assertEqual(len(self.tracker.Hand(name)), 5)
                # check each card is unique
                self.assertEqual(len(set(self.tracker.Hand(name))), 5)
                # check each card not in original hand
                self.assertFalse(set(discards).intersection(set(self.tracker.Hand(name))))
                for card in self.tracker.Hand(name):
                    # check each card not in deck anymore
                    self.assertNotIn(card, self.tracker.DECK.RemainingCards())
                    # check each card categorised as departed
                    self.assertIn(card, self.tracker.DECK.DepartedCards())
                    # check each card is unique in deck
                    self.assertEqual(self.tracker.DECK.DepartedCards().count(card), 1)


    def testEncoding(self):
        # selected hands
        hands = [
            [Card(5,0), Card(3,1), Card(2,2), Card(1,3), Card(0,0)],
            [Card(5,0), Card(5,1), Card(6,2), Card(7,3), Card(8,0)],
            [Card(5,0), Card(5,1), Card(2,2), Card(2,3), Card(9,0)],
            [Card(5,0), Card(5,1), Card(5,2), Card(10,3), Card(11,0)],
            [Card(11,0), Card(10,1), Card(9,2), Card(8,3), Card(7,0)],
            [Card(5,0), Card(3,0), Card(2,0), Card(1,0), Card(0,0)],
            [Card(7,0), Card(7,1), Card(9,2), Card(9,3), Card(9,0)],
            [Card(5,0), Card(5,1), Card(5,2), Card(5,3), Card(0,0)],
            [Card(4,1), Card(3,1), Card(2,1), Card(1,1), Card(0,1)],
            [Card(12,2), Card(11,2), Card(10,2), Card(9,2), Card(8,2)]]
        
        twos = [47, 480, 548, 3104, 3968, 47, 640, 33, 31, 7936]
        primes = [2730, 1255501, 122525, 2519959, 14535931, 2730, 8804429, 57122, 2310, 31367009]

        for i, hand in enumerate(hands):
            # check twos encoding
            self.assertEqual(self.tracker.TwosEncoding(hand), twos[i])
            # checkprimes encoding
            self.assertEqual(self.tracker.PrimesEncoding(hand), primes[i])


    def testFeatureChecking(self):
        # selected hands
        hands = [
            [Card(5,0), Card(3,1), Card(2,2), Card(1,3), Card(0,0)],
            [Card(5,0), Card(5,1), Card(6,2), Card(7,3), Card(8,0)],
            [Card(5,0), Card(5,1), Card(2,2), Card(2,3), Card(9,0)],
            [Card(5,0), Card(5,1), Card(5,2), Card(10,3), Card(11,0)],
            [Card(11,0), Card(10,1), Card(9,2), Card(8,3), Card(7,0)],
            [Card(5,0), Card(3,0), Card(2,0), Card(1,0), Card(0,0)],
            [Card(7,0), Card(7,1), Card(9,2), Card(9,3), Card(9,0)],
            [Card(5,0), Card(5,1), Card(5,2), Card(5,3), Card(0,0)],
            [Card(4,1), Card(3,1), Card(2,1), Card(1,1), Card(0,1)],
            [Card(12,2), Card(11,2), Card(10,2), Card(9,2), Card(8,2)]]
        
        # check flushes are recognised
        for i, hand in enumerate(hands):
            if i in [5, 8, 9]:
                self.assertTrue(self.tracker.HasFlush(hand))
            else:
                self.assertFalse(self.tracker.HasFlush(hand))

        # check duplicates are recognised
        for i, hand in enumerate(hands):
            if i in [0, 4, 5, 8, 9]:
                self.assertTrue(self.tracker.HasUnique5(hand))
            else:
                self.assertFalse(self.tracker.HasUnique5(hand))

        
    def testHandRankDicts(self):
        # check each hand rank dict has correct amount of keys
        self.assertEqual(len(self.tracker.DUPE_RANKS), 4888)
        self.assertEqual(len(self.tracker.UNIQUE5_RANKS), 1287)
        self.assertEqual(len(self.tracker.FLUSH_RANKS), 1287)

        # check each entry has correct structure
        for v in self.tracker.DUPE_RANKS.values():
            self.assertEqual(len(v), 2)
            self.assertIsInstance(v[0], int)
            self.assertIsInstance(v[1], str)
        for v in self.tracker.UNIQUE5_RANKS.values():
            self.assertEqual(len(v), 2)
            self.assertIsInstance(v[0], int)
            self.assertIsInstance(v[1], str)
        for v in self.tracker.FLUSH_RANKS.values():
            self.assertEqual(len(v), 2)
            self.assertIsInstance(v[0], int)
            self.assertIsInstance(v[1], str)

        # selected hands
        hands = [
            [Card(5,0), Card(3,1), Card(2,2), Card(1,3), Card(0,0)],
            [Card(5,0), Card(5,1), Card(6,2), Card(7,3), Card(8,0)],
            [Card(5,0), Card(5,1), Card(2,2), Card(2,3), Card(9,0)],
            [Card(5,0), Card(5,1), Card(5,2), Card(10,3), Card(11,0)],
            [Card(11,0), Card(10,1), Card(9,2), Card(8,3), Card(7,0)],
            [Card(5,0), Card(3,0), Card(2,0), Card(1,0), Card(0,0)],
            [Card(7,0), Card(7,1), Card(9,2), Card(9,3), Card(9,0)],
            [Card(5,0), Card(5,1), Card(5,2), Card(5,3), Card(0,0)],
            [Card(4,1), Card(3,1), Card(2,1), Card(1,1), Card(0,1)],
            [Card(12,2), Card(11,2), Card(10,2), Card(9,2), Card(8,2)]]


        # check correct keys in dictionaries
        for i, hand in enumerate(hands):
            if i in [5, 8, 9]:
                self.assertIn(self.tracker.TwosEncoding(hand), self.tracker.FLUSH_RANKS)
            elif i in [0, 4]:
                self.assertIn(self.tracker.TwosEncoding(hand), self.tracker.UNIQUE5_RANKS)
            else:
                self.assertIn(self.tracker.PrimesEncoding(hand), self.tracker.DUPE_RANKS)
    

    def testEvaluating(self):
        # selected hands
        hands = [
            [Card(5,0), Card(3,1), Card(2,2), Card(1,3), Card(0,0)],
            [Card(5,0), Card(5,1), Card(6,2), Card(7,3), Card(8,0)],
            [Card(5,0), Card(5,1), Card(2,2), Card(2,3), Card(9,0)],
            [Card(5,0), Card(5,1), Card(5,2), Card(10,3), Card(11,0)],
            [Card(11,0), Card(10,1), Card(9,2), Card(8,3), Card(7,0)],
            [Card(5,0), Card(3,0), Card(2,0), Card(1,0), Card(0,0)],
            [Card(7,0), Card(7,1), Card(9,2), Card(9,3), Card(9,0)],
            [Card(5,0), Card(5,1), Card(5,2), Card(5,3), Card(0,0)],
            [Card(4,1), Card(3,1), Card(2,1), Card(1,1), Card(0,1)],
            [Card(12,2), Card(11,2), Card(10,2), Card(9,2), Card(8,2)]]

        # check cant evaluate hands that have less than 5 cards
        for i in range(4):
            self.assertRaises(Exception, self.tracker.EvaluateHand, hands[0][:i])
        # check cant evaluate hands that have more than 5 cards
            self.assertRaises(Exception, self.tracker.EvaluateHand, hands[0]+hands[1])
            
        categories = ["high card", "pair", "two pair", "three of a kind", "straight", 
            "flush", "full house", "four of a kind", "straight flush","royal flush"]

        numbers = [7462, 5030, 3186, 2083, 1601, 1599, 207, 106, 9, 1]
        
        # untracked hands
        for i, hand in enumerate(hands):
            # check hand is numerically ranked correctly
            self.assertEqual(self.tracker.EvaluateHand(hand)[0], numbers[i])
            # check hand is categorised correctly
            self.assertEqual(self.tracker.EvaluateHand(hand)[1], categories[i])

        # tracked hands
        names = [f"{j}" for j in range(10)]
        self.tracker.TrackPlayers(names)
        for name in names:
            self.tracker.AssignCards(name, hands[int(i)])
        self.tracker.EvaluatePlayersIn()

        for name in self.tracker.TrackedPlayers():
            # check hand is numerically ranked correctly
            self.assertEqual(self.tracker.players[name]["rank_n"], numbers[int(i)])
            # check hand is categorised correctly
            self.assertEqual(self.tracker.players[name]["rank_c"], categories[int(i)])


if __name__ == "__main__":
    unittest.main()