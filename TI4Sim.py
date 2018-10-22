#!/usr/bin/env python

"""Code for simulating TI4 battles. Editable information is outlined in the main method."""

__author__ = "Nick Fone"
__date__ = 'Oct 2018'

import secrets


class Ship:
    """Ship class"""
    def __init__(self, name, cost, combat, priority, attacks=1, capacity=0, sustain=False, barrage=False, sus_worry=True):
        self.name = name
        self.cost = cost
        self.combat = combat
        self.attacks = attacks
        self.capacity = capacity
        self.sustain = sustain
        self.sustained = False if sustain else None  # This is the current state of sustained where False = healthy
        self.barrage = barrage
        self.destroyed = False
        self.priority = priority
        self.sustain_worry = sus_worry
        self.repair()  # Changes priority if relevant

    def roll_hits(self, is_red=False):
        hits = 0
        buff = 0 if is_red else 0
        for _ in range(self.attacks):
            if secrets.randbelow(11)+buff >= self.combat:
                hits += 1
        return hits

    def take_hit(self):
        if self.sustain and self.sustained is False:
            self.sustained = True
            if "Dreadnought" in self.name:
                self.priority = 9
            elif self.name == "War Sun":  # After war sun sustains, max priority
                self.priority = 10
        else:
            self.destroyed = True
        return self

    def is_destroyed(self):
        return self.destroyed

    def has_barrage(self):
        return self.barrage

    def get_priority(self):
        return self.priority

    def get_name(self):
        return self.name

    def is_fighter(self):
        return self.name == "Fighter 1" or self.name == "Fighter 2"

    def repair(self):
        if self.sustain:
            self.sustained = False
        self.destroyed = False
        if "Dreadnought" in self.name:
            self.priority = 9 if self.sustain_worry else 1
        elif self.name == "War Sun":
            self.priority = 10 if self.sustain_worry else 1
        return self

    def print(self):
        print("Name: {}\n"
              "Cost: {}\n"
              "Combat: {}\n"
              "Attacks: {}\n"
              "Capacity: {}\n"
              "Priority: {}\n"
              "Sustain: {}  ({})\n"
              "Barrage: {}\n"
              "Destroyed: {}\n"
              .format(self.name, self.cost, self.combat, self.attacks, self.capacity,
                      self.priority, self.sustain, self.sustained, self.barrage, self.destroyed))


def build_ship(ship_name, upgraded, sustain_worry):
    """Builds a single ship - Args:  Name,  Cost,  Combat,  Priority,
    Attacks, capacity, sustain, barrage (fighter only)"""
    if ship_name == "war":
        return Ship("War Sun", 12, 3, 10, 3, 6, True, sus_worry=sustain_worry)
    if ship_name == "dre":
        return Ship("Dreadnought 2", 4, 5, 9, capacity=2, sustain=True, sus_worry=False) if upgraded\
            else Ship("Dreadnought 1", 4, 5, 9, capacity=1, sustain=True, sus_worry=sustain_worry)
    if ship_name == "car":
        return Ship("Carrier 2", 3, 9, 8, capacity=6) if upgraded else Ship("Carrier 1", 3, 9, 8, capacity=4)
    if ship_name == "cru":
        return Ship("Cruiser 2", 2, 6, 7, capacity=1) if upgraded else Ship("Cruiser 1", 2, 7, 7)
    if ship_name == "des":
        return Ship("Destroyer 2", 1, 8, 6, barrage=True) if upgraded else Ship("Destroyer 1", 1, 9, 6, barrage=True)
    if ship_name == "fig":
        return Ship("Fighter 2", 0.5, 8, 5) if upgraded else Ship("Fighter 1", 0.5, 9, 5)
    return None


def build_fleet(menu, sustain_worry=False):
    """Returns a list of ships in he menu"""
    player_fleet = []
    for order in menu:
        name, upgraded, number = order
        for _ in range(number):
            player_fleet.append(build_ship(name, upgraded, sustain_worry))
    return player_fleet


def assign_hits(r_fleet, b_fleet, r_hits, b_hits):
    """Assigns the hits to the ships in priority order"""
    #  Blue take hits
    for _ in range(r_hits):
        target_ship = None
        for ship in b_fleet:
            if ship.is_destroyed():
                continue
            if target_ship is None:
                target_ship = ship
            elif ship.get_priority() < target_ship.get_priority():
                target_ship = ship
        if target_ship is not None:
            index = b_fleet.index(target_ship)
            b_fleet[index] = target_ship.take_hit()
        else:
            break  # AKA more hits than ships
    #  Red take hits
    for _ in range(b_hits):
        target_ship = None
        for ship in r_fleet:
            if ship.is_destroyed():
                continue
            if target_ship is None:
                target_ship = ship
            elif ship.get_priority() < target_ship.get_priority():
                target_ship = ship
        if target_ship is not None:
            index = r_fleet.index(target_ship)
            r_fleet[index] = target_ship.take_hit()
        else:
            break  # AKA more hits than ships
    return r_fleet, b_fleet


def fleet_destroyed(r_fleet, b_fleet):
    """Returns true if fleet is completely destroyed"""
    r_dead = True
    b_dead = True
    for ship in r_fleet:
        if ship.is_destroyed() is False:
            r_dead = False
            break
    for ship in b_fleet:
        if ship.is_destroyed() is False:
            b_dead = False
            break
    return r_dead, b_dead


def barrage_hits(r_fleet, b_fleet, r_hits, b_hits):
    """This func only targets fighters"""
    #Red hit
    for _ in range(r_hits):
        for ship in b_fleet:
            if ship.is_destroyed():
                continue
            if ship.is_fighter():
                index = b_fleet.index(ship)
                b_fleet[index] = ship.take_hit()
                break
    #Blue hits
    for _ in range(b_hits):
        for ship in r_fleet:
            if ship.is_destroyed():
                continue
            if ship.is_fighter():
                index = r_fleet.index(ship)
                r_fleet[index] = ship.take_hit()
                break
    return r_fleet, b_fleet


def count_alive(fleet):
    """Debug"""
    count = 0
    for s in fleet:
        if s.is_destroyed() is False:
            count += 1
    return count


def do_battle(red_fleet, blue_fleet, runs):
    """Simulates the battle between the two fleets, runs is how many sims"""
    red_wins = 0
    blue_wins = 0
    draw = 0
    for _ in range(runs):
    #Anti fighter barrage
        red_hits = 0
        blue_hits = 0
        for ship in red_fleet:
            if ship.has_barrage() and ship.is_destroyed() is False:
                red_hits += ship.roll_hits()
        for ship in blue_fleet:
            if ship.has_barrage() and ship.is_destroyed() is False:
                 blue_hits += ship.roll_hits()
        red_fleet, blue_fleet = barrage_hits(red_fleet, blue_fleet, red_hits, blue_hits)

        #Main battle
        while True:
            red_hits = 0
            blue_hits = 0
            for ship in red_fleet:
                if ship.is_destroyed() is False:
                    red_hits += ship.roll_hits()
            for ship in blue_fleet:
                if ship.is_destroyed() is False:
                    blue_hits += ship.roll_hits()
            red_fleet, blue_fleet = assign_hits(red_fleet, blue_fleet, red_hits, blue_hits) # take hits
            red_dead, blue_dead = fleet_destroyed(red_fleet, blue_fleet)    # Check if fleets are dead
            if red_dead or blue_dead:
                break
        if red_dead and blue_dead:
            draw += 1
        elif blue_dead:
           # print("red wins")
            red_wins += 1
        else:
          #  print("blue wins")
            blue_wins += 1
        #repair
        for ship in red_fleet:
            ship.repair()
        for ship in blue_fleet:
            ship.repair()

    return red_wins, blue_wins, draw


def main():

    # Sustain worry will avoid War Suns and Dread1 sustaining until they must
    red_sustain_worry = False
    blue_sustain_worry = False

    # Number of runs. 1000 is good enough for quick info. 10k is very accurate but a bit slower.
    runs = 10000

    #  Edit as required. Don't edit name. True = upgraded ship. Number is how many produced.
    red_menu = [("war", False, 2),  # WarSuns
                ("dre", False, 10),  # Dreadnoughts
                ("car", False, 3),  # Carriers
                ("cru", False, 4),  # Cruisers
                ("des", False, 5),  # Destroyers
                ("fig", False, 12)]  # Fighters
    red_fleet = build_fleet(red_menu, red_sustain_worry)

    blu_menu = [("war", False, 1),  # WarSuns
                ("dre", False, 10),  # Dreadnoughts
                ("car", False, 3),  # Carriers
                ("cru", False, 10),  # Cruisers
                ("des", False, 5),  # Destroyers
                ("fig", False, 12)]  # Fighters
    blue_fleet = build_fleet(blu_menu, blue_sustain_worry)

    # No need to touch any of this
    red_wins, blue_wins, draw = do_battle(red_fleet, blue_fleet, runs)

    print("Red: {}%\n"
          "Blue: {}%\n"
          "Draw: {}%".format(round(red_wins/runs*100, 1), round(blue_wins/runs*100, 1), round(draw/runs*100, 1)))


main()
