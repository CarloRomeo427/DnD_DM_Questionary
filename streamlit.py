import streamlit as st
import json
import numpy as np
import random as rnd
import os
import requests
import base64
import time
import datetime  # New import for timestamp generation
from simulate import benchmark

# GitHub Configuration
GIT_SECRET  = os.getenv("DB_TOKEN")  # Ensure this is properly set in your environment or Streamlit secrets
GITHUB_REPO = "CarloRomeo427/DnD_DM_Questionary/"
GITHUB_BRANCH = "main"
# Note: The file path is now dynamic (unique per session)

def push_to_github(new_line_data):
    """Writes new_line_data (a JSON string representing a dictionary) as an element of an array in a session-specific JSON file.
    
    If the file doesn't exist, it creates one with the data wrapped in an array.
    If the file exists, it loads the current array, appends the new dictionary, and writes the updated array.
    """
    # Generate a unique file name for this session if it doesn't exist
    if "git_filename" not in st.session_state:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        random_int = rnd.randint(1000, 9999)
        st.session_state.git_filename = f"user_selection_{timestamp}_{random_int}.json"
    
    file_name = st.session_state.git_filename
    url = f"https://api.github.com/repos/CarloRomeo427/DnD_DM_Questionary/contents/Humans/{file_name}"
    headers = {
        "Authorization": f"token {GIT_SECRET}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    # Attempt to get the current remote file (if it exists)
    get_response = requests.get(url, headers=headers)
    if get_response.status_code == 200:
        remote_data = get_response.json()
        sha = remote_data.get("sha")
        encoded_content = remote_data.get("content", "")
        if encoded_content:
            current_text = base64.b64decode(encoded_content).decode("utf-8")
        else:
            current_text = ""
    else:
        sha = None
        current_text = ""
    
    # Initialize data_list as an array. If current_text exists, try to parse it.
    if current_text.strip():
        try:
            data_list = json.loads(current_text)
            # Ensure the content is a list
            if not isinstance(data_list, list):
                data_list = []
        except Exception as e:
            st.error(f"Error decoding current JSON content: {e}")
            data_list = []
    else:
        data_list = []
    
    # Parse the new_line_data (which should be a JSON string representing a dictionary)
    try:
        new_data = json.loads(new_line_data)
    except Exception as e:
        st.error(f"Error decoding new encounter data: {e}")
        return None, {"error": str(e)}
    
    # Append the new data to the array
    data_list.append(new_data)
    
    # Serialize the entire list as JSON (formatted with indentation for readability)
    new_text = json.dumps(data_list, indent=4)
    
    # Encode the new content in Base64
    content_b64 = base64.b64encode(new_text.encode("utf-8")).decode("utf-8")
    
    # Prepare the payload
    data = {
        "message": f"Updating session file {file_name} with new encounter data",
        "content": content_b64,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        data["sha"] = sha

    # Update (or create) the file on GitHub
    put_response = requests.put(url, headers=headers, json=data)
    return put_response.status_code, put_response.json()


# --------------------- LOAD PRECOMPUTED DATA ---------------------
DATA_FILE = "precomputed_party_data.npz"
if not os.path.exists(DATA_FILE):
    st.error(f"Missing data file: {DATA_FILE}. Run data generation first.")
    st.stop()

data = np.load(DATA_FILE, allow_pickle=True)
precomputed_parties = data["matrices"]
precomputed_class_names = data["class_names"]
party_indices = list(data["indices"])
st.session_state.parties = []
st.session_state.enemies = []

if "counter" not in st.session_state:
    st.session_state.counter = 0

if "party_indices" not in st.session_state:
    st.session_state.party_indices = party_indices
    st.session_state.precomputed_parties = precomputed_parties
    st.session_state.precomputed_class_names = precomputed_class_names
    st.session_state.generated_party = None
    st.session_state.generated_class_names = None
    st.session_state.party_exp = 0

# --------------------- FUNCTIONS ---------------------
def reset_session():
    for key in list(st.session_state.keys()):
        if key not in ["counter", "git_filename", "parties", "enemies"]:
            del st.session_state[key]
    st.session_state.counter = counter

def get_next_party_matrix():
    idx = rnd.choice(st.session_state.party_indices)
    return st.session_state.precomputed_parties[idx], st.session_state.precomputed_class_names[idx]

def generate_encounter():
    st.session_state.generated_party, st.session_state.generated_class_names = get_next_party_matrix()
    st.session_state.party_exp = calculate_party_exp(st.session_state.generated_class_names, "hard")
    st.session_state.parties.append(st.session_state.generated_class_names)

def extract_feature_constants(class_files_path):
    numerical_features = [
        "AC", "HP", "Proficiency", "To_Hit", "Attacks", "DMG",
        "Str", "Dex", "Con", "Int", "Wis", "Cha",
        "Spell_DC", "Spell_Mod", "Spell_Slot_1", "Spell_Slot_2", "Spell_Slot_3",
        "Speed", "Range_Attack"
    ]
    cat_set_1 = ["Saves_Proficiency", "Damage_Type", "Position"]
    cat_set_2 = ["Spell_List"]
    cat_set_3 = ["Other_Abilities"]
    categorical_features = cat_set_1 + cat_set_2 + cat_set_3

    categorical_max_lengths = {feature: 0 for feature in categorical_features}
    categorical_value_sets = {feature: set() for feature in categorical_features}

    for file_name in os.listdir(class_files_path):
        if file_name.endswith(".json"):
            with open(os.path.join(class_files_path, file_name), "r") as f:
                data = json.load(f)
                for feature in categorical_features:
                    values = str(data.get(feature, "")).split()
                    categorical_max_lengths[feature] = max(categorical_max_lengths[feature], len(values))
                    categorical_value_sets[feature].update(values)

    num_feature_count = len(numerical_features)
    cat_set_1_count = sum(categorical_max_lengths[f] for f in cat_set_1)
    cat_set_2_count = sum(categorical_max_lengths[f] for f in cat_set_2)
    cat_set_3_count = sum(categorical_max_lengths[f] for f in cat_set_3)

    index_ranges = {
        "numerical": (0, num_feature_count),
        "cat_set_1": (num_feature_count, num_feature_count + cat_set_1_count),
        "cat_set_2": (
            num_feature_count + cat_set_1_count, 
            num_feature_count + cat_set_1_count + cat_set_2_count
        ),
        "cat_set_3": (
            num_feature_count + cat_set_1_count + cat_set_2_count,
            num_feature_count + cat_set_1_count + cat_set_2_count + cat_set_3_count
        )
    }

    return (
        numerical_features, 
        categorical_features, 
        categorical_max_lengths, 
        {key: list(values) for key, values in categorical_value_sets.items()}, 
        index_ranges,
        (cat_set_1, cat_set_2, cat_set_3)
    )

def get_class_features(class_name, class_files_path):
    (numerical_features, categorical_features, categorical_max_lengths,
     categorical_value_sets, index_ranges, cat_sets) = extract_feature_constants(class_files_path)

    file_name = f"{class_name} Lv5.json"
    file_path = os.path.join(class_files_path, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Class file not found: {file_name}")

    with open(file_path, "r") as f:
        data = json.load(f)

    class_features = {}
    for feature in numerical_features:
        class_features[feature] = data.get(feature, 0)
    for feature in categorical_features:
        values = str(data.get(feature, "")).split()
        valid_values = [val for val in values if val in categorical_value_sets[feature]]
        class_features[feature] = valid_values if valid_values else ["Unknown"]

    return class_features

# --------------------- XP CALCULATIONS ---------------------
MULTIPLIER_TABLE = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5, 5: 3.0, 6: 4.0}
exp_dict = {
    "Ape": 100, "Boar": 50, "Brown Bear": 200, "Crocodile": 100, "Displayer Beast": 700,
    "Fire Elemental": 1800, "Flameskull": 1100, "Giant Boar": 450, "Giant Centipede": 50,
    "Giant Crocodile": 1800, "Giant Eagle": 200, "Giant Scorpion": 700, "Giant Spider": 200,
    "Giant Wasp": 100, "Goblin": 50, "Night Hag": 1800, "Ogre": 450, "Pirate": 200,
    "Polar Bear": 450, "Stone Giant": 2900, "Swarm of Bats": 50, "Vampire Spawn": 1800,
    "Vampire": 10000, "Wolf": 50, "Young Dragon": 5900
}
enemy_options = ["None -> 0 EXP"] + [f"{name} -> {xp} EXP" for name, xp in exp_dict.items()]
enemy_option_to_xp = {opt: xp for opt, xp in zip(enemy_options, [0] + list(exp_dict.values()))}

def compute_enemy_exp(selected_options):
    xp_values = [enemy_option_to_xp[o] for o in selected_options if enemy_option_to_xp[o] > 0]
    return sum(xp_values) * MULTIPLIER_TABLE.get(len(xp_values), 4.0)

def calculate_party_exp(party, difficulty="hard"):
    EXP_THRESHOLDS = {"easy": 500, "medium": 750, "hard": 1100, "deadly": 2200}
    return EXP_THRESHOLDS[difficulty] * len(party)

# --------------------- UI ELEMENTS ---------------------
st.title("🧙 D&D Encounter Generator")

st.markdown("""
<div class="description-box">
<b>Welcome to the D&D Encounter Generator!</b><br>
This tool tests your expertise as Dungeon Master in creating balanced encounters for your party!<br><br>
A balanced encounter should be challenging but not deadly for the party! 
Therefore, given the Party EXP the Dungeon Master should select a team of enemies with a similar EXP value.<br><br>
We are trying to reproduce the concept of flow in the game, where the group is challenged to keep the level of attention high 
but at the same time the challenge must not be insurmountable causing frustration in the player to the point of quitting. <br><br>
<b>How the tool works:</b><br>
1. Click the button to generate a random party of adventurers.<br>
2. For each party member, you can view their stats and abilities by clicking on the class name.<br>
3. All party members are Level 5.<br>
4. Based on the party composition, select a team of enemies to challenge them.<br>
5. You can choose up to 8 enemies to fight against the party.<br>
6. The tool calculates the total EXP of the enemy team using the classic formula as in the official Dungeon Master Guide.<br>
7. A balanced encounter should have an enemy EXP value close to the party EXP value.<br>
8. Differences in EXP values can make the encounter easier (down to “boring”) or harder (up to “deadly”) for the group.<br>
</div>
""", unsafe_allow_html=True)

# --------------------- DM EXPERTISE SELECTION ---------------------
expertise_levels = [
    "Noob - Still learning what a d20 is",
    "Amateur - Can handle small encounters, but big foes are scary",
    "Skilled - Runs epic battles with minimal confusion",
    "Expert - NPC voices so good, players forget it's you",
    "Legendary - Godlike storyteller, even Tiamat takes notes"
]

st.subheader("Expertise as DM")
selected_expertise = st.selectbox("Choose your expertise level:", expertise_levels)
st.markdown("---")

# --------------------- ENCOUNTER GENERATION ---------------------
col_gen, col_counter = st.columns([3, 1])
with col_gen:  
    st.button("🎲 Generate Encounter", on_click=generate_encounter)
with col_counter:
    st.metric(label="YOUR SUBMISSIONS!!!", value=st.session_state.counter,)
    
if st.session_state.generated_party is not None:
    st.subheader(f"Party EXP: {st.session_state.party_exp}")

    # Display party members in two columns
    col_party1, col_party2 = st.columns(2)
    party_cols = [col_party1, col_party2]

    for i, cls in enumerate(st.session_state.generated_class_names):
        col_index = i % 2
        with party_cols[col_index].expander(f"{cls}", expanded=False):
            class_features = get_class_features(cls, "Classes/")
            st.markdown("**LvL:** 5")
            for key, value in class_features.items():
                if isinstance(value, list):
                    st.markdown(f"**{key}:**")
                    for v in value:
                        st.markdown(f"- {v}")
                else:
                    st.markdown(f"**{key}:** {value}")

    st.markdown("---")
    st.subheader("Build the Enemy Encounter Team!")

    # Enemy selection in two columns
    col_enemy1, col_enemy2 = st.columns(2)
    enemy_cols = [col_enemy1, col_enemy2]

    selected_enemies = []
    for i in range(8):
        col_index = i % 2
        with enemy_cols[col_index]:
            slot_label = f"Enemy {i+1}"
            choice = st.selectbox(slot_label, enemy_options, index=0, key=f"enemy_{i+1}")
            selected_enemies.append(choice)
    
    st.session_state.enemies.append(selected_enemies)
    enemy_total_exp = compute_enemy_exp(selected_enemies)
    st.subheader(f"**Enemy Encounter EXP:** {enemy_total_exp}")

    if st.button("✅ Submit Decision"):
        # Check if at least one enemy is selected (i.e. not "None -> 0 EXP")
        if not any(choice != enemy_options[0] for choice in selected_enemies):
            st.warning(
                "Please, to submit you have at least to pick one enemy encounter or, if you do not like the current Party Members, generate a new party by pressing the Generate Encounter button!"
            )
        else:
            st.session_state.counter += 1
            encounter_data = {
                "expertise": selected_expertise,
                "party": list(st.session_state.generated_class_names),
                "party_exp": st.session_state.party_exp,
                "enemies": selected_enemies,
                "enemy_exp": enemy_total_exp
            }
            new_line = json.dumps(encounter_data)

            status, response = push_to_github(new_line)
            counter = st.session_state.counter

            if status in (200, 201):
                st.success("✅ Data successfully uploaded to GitHub!")
                print("✅ Data successfully uploaded to GitHub!")
            else:
                st.error(f"❌ Failed to upload data: {response}")
                print(f"❌ Failed to upload data: {response}")

            # Clear all session state keys except 'counter' and 'git_filename' so the same session file is used
            for key in list(st.session_state.keys()):
                if key not in ["counter", "git_filename", "parties", "enemies"]:
                    del st.session_state[key]
            st.session_state.counter = counter

            if st.session_state.counter == 5:
                wins, rounds, dmgs, deaths, healths = 0, 0, 0, 0, 0
                for party, enemy in zip(st.session_state.parties, st.session_state.enemies):
                    win_probability, rounds_number, dmg_player, DeathNumber, TeamHealth = benchmark(party, enemy)
                    wins += win_probability
                    rounds += rounds_number
                    dmgs += dmg_player
                    deaths += DeathNumber
                    healths += TeamHealth
                wins /= 5
                rounds /= 5
                dmgs /= 5
                deaths /= 5
                healths /= 5

                with st.container():
                    st.subheader("Your DM Expertise:")
                    st.write(f"Win Probability: {wins:.2f}")
                    st.write(f"Rounds: {rounds:.2f}")
                    st.write(f"Damage dealt: {dmgs:.2f}")
                    st.write(f"Total Party Kills: {deaths:.2f}")
                    st.write(f"Team Health: {healths:.2f}")
                    
                    # Reset button
                    st.button("Reset Session", on_click=reset_session)

            else:              
                st.rerun()
