import unittest
from fivecarddraw import Card, Deck

class DeckTest(unittest.TestCase):
    def setUp(self):
        # create explicit deck of cards
        self.deck = Deck()


    def testDealing(self):
        # cycle tests for all cards in deck
        for _ in range(52):
            dealt_card = next(self.deck)
            # Check card is a card
            self.assertIsInstance(dealt_card, Card)
            # Check card is categorised correctly
            self.assertNotIn(dealt_card, self.deck.RemainingCards())
            self.assertIn(dealt_card, self.deck.DepartedCards())
            # Check card is unique
            self.assertEqual(self.deck.DepartedCards().count(dealt_card), 1)

        # Check no more cards can be dealt when deck is empty
        self.assertRaises(StopIteration, lambda x : next(x), self.deck)


    def testCounting(self):
        # Check 52 cards in deck
        self.assertEqual(len(self.deck), 52)

        # cycle tests for all cards in deck
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
        # check shuffling 52 cards
        preshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()
        self.deck.Shuffle()
        postshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()

        # Check remaining card count is unaffected by shuffle
        self.assertEqual(len(preshuffle[0]), len(postshuffle[0]))
        # Check remaining cards hash unaffected by shuffle
        self.assertEqual(set(preshuffle[0]), set(postshuffle[0]))
        # Check departed cards completely unaffected by shuffle
        self.assertEqual(preshuffle[1], postshuffle[1])

        # check shuffling less cards
        for i in range(52):
            # discard some cards
            for _ in range(i): 
                next(self.deck)
            
            # shuffle remaining cards
            preshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()
            self.deck.Shuffle()
            postshuffle = self.deck.RemainingCards(), self.deck.DepartedCards()

            # Check remaining card count unaffected by shuffle
            self.assertEqual(len(preshuffle[0]), len(postshuffle[0]))
            # Check remaining cards hash unaffected by shuffle
            self.assertEqual(set(preshuffle[0]), set(postshuffle[0]))

            # check special case when derangement is expected
            if i < 35:
                # Check remaining card order is affected by shuffle
                self.assertNotEqual(preshuffle[0], postshuffle[0])

            # Check departed cards completely unaffected by shuffle
            self.assertEqual(preshuffle[1], postshuffle[1])
            self.deck.CollectCards()


    def testCollecting(self):
        # cycle tests for different amounts of departed cards
        precollection = self.deck.RemainingCards()
        for i in range(52):
            # discard some cards
            self.deck.Shuffle()
            for _ in range(i): 
                next(self.deck)

            # check discard alters deck iterator
            self.assertEqual(len(self.deck), 52-i)

            # collect cards
            self.deck.CollectCards()
            postcollection = self.deck.RemainingCards()

            # Check remaining cards hash unaffected by collect
            self.assertEqual(set(precollection), set(postcollection))
            # check collect restarts deck iterator
            self.assertEqual(len(self.deck), 52)


if __name__ == "__main__":
    unittest.main()