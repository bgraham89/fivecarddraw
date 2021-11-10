from fivecarddraw import Card
from random import randint
  
def TestMask(num_trials):
    dummy = Card(0,0)
    print("  ", dummy.MASK, "MASK")
    
    for _ in range(num_trials):
        value = randint(0,12)
        suit = randint(0,3)
        card = Card(value, suit)
        try:
            assert(len(bin(card.b >> 16)) == value + 3) #has decipherable value
            assert((bin(card.b >> 16)).count("1") == 1) #has one value
            assert(len(bin((card.b >> 12) & 15)) == suit + 3) #has decipherable suit
            assert((bin((card.b >> 12) & 15)).count("1") == 1) #has one suit
            assert((card.b & 255) in card.P) #has decipherable prime
            assert(((card.b >> 8) & 15) == value) #has decipherable rank
        except:
            print(card, bin(card.b), "FAIL")
            continue
        print(card, bin(card.b)[2:], "PASS")

TestMask(10)        

def Configuration():
    dummy = Card(0,0)
    print("VALUES", " ".join(dummy.VALUES))
    print("P", dummy.P)
    print("R", tuple(dummy.R))
    print("SUITS", dummy.SUITS, "\n")
    
Configuration()

def Attributes():
    value = randint(0,12)
    suit = randint(0,3)
    card = Card(value, suit)
    print(card, "prime:", bin(card.prime), f"({card.prime})")
    print(card, "rank:", bin(card.rank >> 8), f"({card.rank >> 8})")
    print(card, "suit:", bin(card.suit >> 12), f"({len(bin(card.suit >> 12)) - 3})")
    print(card, "value:", bin(card.value >> 16), f"({len(bin(card.value >> 16)) - 3})")
    mask = list(bin(card.b))
    mask.insert(-16, " ")
    mask.insert(-12, " ")
    mask.insert(-8, " ")
    print(card, "mask", "".join(mask))
       
Attributes()
