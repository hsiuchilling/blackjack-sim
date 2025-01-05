# blackjack-sim

Blackjack simulator for recreational observations.

## Getting Started

We use `poetry` as a package manager. Installation instructions are [here](https://python-poetry.org/docs/#installation). 

```
cd blackjack_sim
poetry install

poetry run python basic_play.py
```

## TODO

**Features**
* prohibit illegal dhits
* implement surrenders
* F4 surrenders
* mid-shoe entry
* mid-shoe benchmarks vs. don't count, true count
* game state pretty print

**Clean up**
* game termination condition
* card + hand name + strategy file standardization 