import unittest
from random import randint
from fivecarddraw import Card, Deck

class DeckTest(unittest.TestCase):
    def setUp(self):
        self.deck = Deck()

    def testDeal(self):
        last_card = None
        for _ in range(52):
            dealt_card = next(self.deck)
            self.assertIsInstance(dealt_card, Card)
            self.assertNotEqual(dealt_card, last_card)

    def testCount(self):
        self.assertEqual(len(self.deck), 52)
        for i in range(52):
            next(self.deck)
            count_remaining = 52-i-1
            count_departed = 52 - count_remaining
            self.assertEqual(len(self.deck), count_remaining)
            self.assertEqual(len(self.deck.RemainingCards()), count_remaining)
            self.assertEqual(len(self.deck.DepartedCards()), count_departed)

    def testShuffle(self):
        preshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()
        self.deck.Shuffle()
        postshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()
        self.assertEqual(set(preshuffle[0]), set(postshuffle[0]))
        self.assertEqual(preshuffle[1], postshuffle[1])

        for i in range(52):
            for _ in range(i): next(self.deck)
            preshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()
            self.deck.Shuffle()
            postshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()
            self.assertEqual(set(preshuffle[0]), set(postshuffle[0]))
            self.assertEqual(preshuffle[1], postshuffle[1])
            self.deck.Collect()

    def testCollect(self):
        precollect = self.deck.RemainingCards(), self.deck.DepartedCards()
        for i in range(52):
            for _ in range(i): next(self.deck)
            self.deck.Collect()
            postcollect = self.deck.RemainingCards(), self.deck.DepartedCards()
            self.assertEqual(precollect[0], postcollect[0])
            self.assertEqual(precollect[1], postcollect[1])

        self.deck.Shuffle()
        precollect = self.deck.RemainingCards(), self.deck.DepartedCards()
        for i in range(52):
            for _ in range(i): next(self.deck)
            self.deck.Collect()
            postcollect = self.deck.RemainingCards(), self.deck.DepartedCards()
            self.assertEqual(precollect[0], postcollect[0])
            self.assertEqual(precollect[1], postcollect[1])

if __name__ == "__main__":
    unittest.main()