import random

def generate_deck():
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
    deck = []

    for suit in suits:
        for rank in ranks:
            card = {
                "suit": suit,
                "rank": rank,
                "value": get_value(rank)
            }
            deck.append(card)

    return deck



def get_value(rank):
    power_order = {'ace': 1, 'king': 2, 'queen': 3, 'jack': 4, '10': 5, '9': 6, '8': 7, '7': 8, '6': 9, '5': 10, '4': 11, '3': 12, '2': 13}
    return power_order[rank]
    


def shuffle_deck(deck):
    shuffled_deck = deck[:]  # Create a copy of the deck to shuffle
    random.shuffle(shuffled_deck)
    return shuffled_deck


