from Entity_class import *
from Encounter_Simulator import *
from Dm_class import *

import numpy as np

def benchmark(party, enemy_names, verbose=False):
    """Simulates a combat encounter and returns a reward."""
    DM = DungeonMaster()
    DM.block_print()

    # Create entities dictionary
    Entities = {i: {"name": f"{member} Lv5", "team": 0} for i, member in enumerate(party)}
    
    enemy_start_index = len(party)
    for i, enemy in enumerate(enemy_names):
        if enemy is not None:
            Entities[enemy_start_index + i] = {"name": enemy, "team": 1}

    # Create Fighter objects
    Fighters = [entity(Entities[i]['name'], Entities[i]['team'], DM, archive=True) for i in Entities]

    # Run simulation
    text, win_probability, rounds_number, dmg_player, DeathNumber, TeamHealth = full_statistical_recap(100, Fighters)


    return win_probability, np.mean(rounds_number), np.mean(dmg_player), np.mean(DeathNumber), np.mean(TeamHealth)

if __name__ == "__main__":
    party = ["Fighter", "Rogue", "Wizard"]
    enemy_names = ["Goblin", "Ogre", "Pirate"]
    win_probability, rounds_number, dmg_player, DeathNumber, TeamHealth = benchmark(party, enemy_names, verbose=True)
    print(f"Win probability: {win_probability}")
    print(f"Rounds number: {np.mean(rounds_number)}")
    print(f"Player damage: {np.mean(dmg_player)}")
    print(f"Death number: {np.mean(DeathNumber)}")
    print(f"Team health: {np.mean(TeamHealth)}")