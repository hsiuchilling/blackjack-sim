def estimate_rounds(shoe, n_players):
    return int((shoe.shoe_size - shoe.idx) / 2.7 / (n_players + 1) * 1.5)