import unittest
from random import randint
from fivecarddraw import Card, Deck

class DeckTest(unittest.TestCase):
    def setUp(self):
        self.deck = Deck()


    def testDealing(self):
        for _ in range(52):
            dealt_card = next(self.deck)
            # Check each card is a card
            self.assertIsInstance(dealt_card, Card)
            # Check each card is categorised correctly when dealt
            self.assertNotIn(dealt_card, self.deck.RemainingCards())
            self.assertIn(dealt_card, self.deck.DepartedCards())
            # Check each card is unique in the deck
            self.assertEqual(self.deck.DepartedCards().count(dealt_card), 1)
        # Check no more cards can be dealt when deck is empty
        self.assertRaises(StopIteration, lambda x : next(x), self.deck)


    def testCounting(self):
        # Check 52 cards in deck
        self.assertEqual(len(self.deck), 52)
        for i in range(52):
            next(self.deck)
            count_remaining = 52-i-1
            count_departed = 52 - count_remaining
            # Check dealt cards no longer count towards len(deck)
            self.assertEqual(len(self.deck), count_remaining)
            # Check dealt cards no longer count towards remaining cards in deck
            self.assertEqual(len(self.deck.RemainingCards()), count_remaining)
            # Check dealt cards count towards departed cards from deck
            self.assertEqual(len(self.deck.DepartedCards()), count_departed)


    def testShuffling(self):
        # 52 cards in deck
        preshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()
        self.deck.Shuffle()
        postshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()
        # Check remaining card count is unaffected by shuffle
        self.assertEqual(len(preshuffle[0]), len(postshuffle[0]))
        # Check remaining cards hash unaffected by shuffle
        self.assertEqual(set(preshuffle[0]), set(postshuffle[0]))
        # Check departed cards completely unaffected by shuffle
        self.assertEqual(preshuffle[1], postshuffle[1])

        # Lower number of cards remaining in deck
        for i in range(52):
            for _ in range(i): 
                next(self.deck)
            preshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()
            self.deck.Shuffle()
            postshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()
            # Check remaining card count unaffected by shuffle
            self.assertEqual(len(preshuffle[0]), len(postshuffle[0]))
            # Check remaining cards hash unaffected by shuffle
            self.assertEqual(set(preshuffle[0]), set(postshuffle[0]))
            # Enough cards in deck to expect a derangement
            if i < 35:
                # Check remaining card order is affected by shuffle
                self.assertNotEqual(preshuffle[0], postshuffle[0])
            # Check departed cards completely unaffected by shuffle
            self.assertEqual(preshuffle[1], postshuffle[1])
            self.deck.CollectCards()


    def testCollecting(self):
        precollect = self.deck.RemainingCards()
        for i in range(52):
            # shuffled decks
            self.deck.Shuffle()
            # different amount of remaining cards in deck
            for _ in range(i): 
                next(self.deck)
            self.deck.CollectCards()
            postcollect = self.deck.RemainingCards()
            # Check remaining cards hash unaffected by collect
            self.assertEqual(set(precollect), set(postcollect))
            # check collect restarts deck iterator
            self.assertEqual(len(self.deck), 52)

if __name__ == "__main__":
    unittest.main()