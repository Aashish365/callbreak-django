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


















def are_same_suit(cards):
    initial_suit=cards[0]['suit']
    for card in cards:
        if(card['suit']!=initial_suit):
            return False
    return True


def big_from_same_cards(cards):
    index=0
    bigValue=cards[0]['value']
    for i in range(len(cards)):
        if(cards[i]['value']<bigValue):
            index=i
            bigValue=cards[i]['value']
    return cards[index]

def spades_count(cards):
    spades_count = 0
    for card in cards:
        if card['suit'] == 'spades':
            spades_count += 1
    return spades_count

def get_cards_of_suit(cards,suit):
    mycards=[]
    for card in cards:
        if(card['suit']==suit):
            mycards.append(card)
    return mycards


def get_index_of_card(cards,mycard):
    for i in range(len(cards)):
        if cards[i]==mycard:
            return i
            break
    


def winner_card_index(cards):
    if(spades_count(cards)>=1):
        return get_index_of_card(cards,big_from_same_cards(get_cards_of_suit(cards,"spades")))
        
    else:
        return get_index_of_card(cards,big_from_same_cards(get_cards_of_suit(cards,cards[0]['suit'])))
        













