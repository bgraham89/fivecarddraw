import unittest
from random import randint
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
            self.assertIn(card, self.tracker.TrackedHand(player))
            self.assertEqual(len(self.tracker.TrackedHand(player)), len(assigned_cards))

        # implicit hand collection
        num_cards = len(assigned_cards)
        for card in assigned_cards:
            self.tracker.UnassignCards(player, [card])
            num_cards -= 1
            # check single card unassignment
            self.assertNotIn(card, self.tracker.TrackedHand(player))
            self.assertEqual(len(self.tracker.TrackedHand(player)), num_cards)
        # check all cards unassigned
        self.assertEqual(len(self.tracker.TrackedHand(player)), 0)

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
            self.tracker.Collect()

        # 1000 more hands
        for _ in range(100):
            self.tracker.ShuffleDeck()
            # 10 dealt in players
            names = [f"{j}" for j in range(10)]
            self.tracker.TrackPlayers(names)
            self.tracker.DealPlayersIn()
            for name in self.tracker.TrackedPlayers():
                hand = self.tracker.hands[name]["cards"]
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
            self.tracker.Collect()


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
            self.tracker.Collect()


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
        self.tracker.Collect()

        # tracked swaps
        self.tracker.ShuffleDeck()
        names = [f"{i}" for i in range(3)]
        self.tracker.TrackPlayers(names)
        self.tracker.DealPlayersIn()
        # tracked players
        for name in names:
            # allowed cardinality of discards
            for j in range(4):
                discards = self.tracker.TrackedHand(name)[:j+1]
                self.tracker.SwapPlayersCards(name, discards)
                # check correct amount of cards is returned
                self.assertEqual(len(self.tracker.TrackedHand(name)), 5)
                # check each card is unique
                self.assertEqual(len(set(self.tracker.TrackedHand(name))), 5)
                # check each card not in original hand
                self.assertFalse(set(discards).intersection(set(self.tracker.TrackedHand(name))))
                for card in self.tracker.TrackedHand(name):
                    # check each card not in deck anymore
                    self.assertNotIn(card, self.tracker.DECK.RemainingCards())
                    # check each card categorised as departed
                    self.assertIn(card, self.tracker.DECK.DepartedCards())
                    # check each card is unique in deck
                    self.assertEqual(self.tracker.DECK.DepartedCards().count(card), 1)


if __name__ == "__main__":
    unittest.main()