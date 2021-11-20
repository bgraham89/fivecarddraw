from fivecarddraw import Card, Dealer, Deck, Hand, Player
from random import choice, randint, sample, shuffle   


def Switch(num_trials):
    deck = Deck()
    for _ in range(num_trials):
        hand = Hand(sample(deck, 5))
        
        flush = bool((
            hand[0].b & hand[1].b & hand[2].b & hand[3].b & hand[4].b & 
            (15 << 12)))
        
        unique5 = bin((
            hand[0].b | hand[1].b | hand[2].b | hand[3].b | hand[4].b) >> 
            16).count("1") == 5
        
        dupes = not flush and not unique5
        print(
            hand, "flush:", flush, " unique5:", unique5, " dupes:", dupes)
            
Switch(100)      

def LookupData():
    # print(open("flush lookup.txt", "r").read())
    # print(open("unique five lookup.txt", "r").read())
    print(open("dupe lookup.txt", "r").read())
    
    VALUES = {char : 2 ** i for i, char in enumerate("23456789TJQKA")}
    PRIMES = {char : p for char, p in zip("23456789TJQKA", Card(0,0).P)}
       
    FLUSH_RANKS = {
        VALUES[line[4]] | VALUES[line[5]] | VALUES[line[6]] | 
        VALUES[line[7]] | VALUES[line[8]] : int(str(line)[11:]) 
        for line in open("flush lookup.txt", "r")}
    
    UNIQUE_FIVE_RANKS = {
        VALUES[line[4]] | VALUES[line[5]] | VALUES[line[6]] | 
        VALUES[line[7]] | VALUES[line[8]] : int(str(line)[11:]) 
        for line in open("unique five lookup.txt", "r")}
    
    DUPE_RANKS = {
        PRIMES[line[4]] * PRIMES[line[5]] * PRIMES[line[6]] * 
        PRIMES[line[7]] * PRIMES[line[8]] : int(str(line)[11:]) 
        for line in open("dupe lookup.txt", "r")}  
    
    # print(FLUSH_RANKS)
    # print(UNIQUE_FIVE_RANKS)
    # print(DUPE_RANKS)
    
LookupData()

def RankHands(num_trials):
    for _ in range(num_trials):
        players = [Player(f"player {i}") for i in range(10)]
        game = Dealer(players)
        game.ShuffleDeck()
        game.DealHands()
        rankings = game.EvaluateHands()
        
        for player in game:
            ranking = rankings[player.name]
            ranking_r = game.Lookup(ranking)
            print(player.hand, "ranked:", ranking, f"({ranking_r})" )
        
RankHands(100)
            
        
    

    
