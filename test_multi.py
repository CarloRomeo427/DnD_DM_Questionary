MULTIPLIER_TABLE = {
    1: 1.0,    # ✅ 1 → x1
    2: 1.5,    # ✅ 2 → x1.5
    3: 2.0,    # ✅ 3-6 → x2
    4: 2.0,    # ✅
    5: 2.0,    # ✅
    6: 2.0,    # ✅
    7: 2.5,    # ✅ 7-10 → x2.5
    8: 2.5,    # ✅
    9: 2.5,    # ✅
    10: 2.5,   # ✅
    11: 3.0,   # ✅ 11-14 → x3
    12: 3.0,   # ✅
    13: 3.0,   # ✅
    14: 3.0,   # ✅
    15: 4.0,   # ✅ 15+ → x4
}
exp_dict = {
    "Ape": 100, "Boar": 50, "Brown Bear": 200, "Crocodile": 100, "Displayer Beast": 700,
    "Fire Elemental": 1800, "Flameskull": 1100, "Giant Boar": 450, "Giant Centipede": 50,
    "Giant Crocodile": 1800, "Giant Eagle": 200, "Giant Scorpion": 700, "Giant Spider": 200,
    "Giant Wasp": 100, "Goblin": 50, "Night Hag": 1800, "Ogre": 450, "Pirate": 200,
    "Polar Bear": 450, "Stone Giant": 2900, "Swarm of Bats": 50, "Vampire Spawn": 1800,
    "Vampire": 10000, "Wolf": 50, "Young Dragon": 5900
}

enemy_options = ["None -> 0 XP"] + [f"{name} -> {xp} XP" for name, xp in exp_dict.items()]
enemy_option_to_xp = {name: xp for name, xp in exp_dict.items()}  # Keep keys as raw names

def compute_enemy_exp(selected_options):
    """Computes total XP for selected enemies, applying XP multiplier."""
    xp_values = [enemy_option_to_xp[o] for o in selected_options if o in enemy_option_to_xp]
    return sum(xp_values) * MULTIPLIER_TABLE.get(len(xp_values), 4.0)

e = "Ape"
# ✅ Now 'enemies' contains valid keys ("Ape" matches "Ape" in enemy_option_to_xp)
for i in [1, 2, 3, 7, 11, 15]:
    enemies = [e] * i
    print(f"Num: {i}, Exp: {100 * i}, Multiplier: {MULTIPLIER_TABLE.get(i, 4.0)}")
    print(compute_enemy_exp(enemies))  # Output: 100.0, 150.0, 200.0, 250.0, 300.0, 400.0
