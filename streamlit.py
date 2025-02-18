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

import logging
logging.basicConfig(level=logging.DEBUG)



# GitHub Configuration
GIT_SECRET  = os.getenv("DB_TOKEN")  # Ensure this is properly set in your environment or Streamlit secrets
GITHUB_REPO = "CarloRomeo427/DnD_DM_Questionary/"
GITHUB_BRANCH = "main"
# Note: The file path is now dynamic (unique per session)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# --------------------- FOOTER ---------------------
footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 50%;
    background-color: rgba(241, 241, 241, 0.95); /* Slight transparency */
    color: #333;
    text-align: left;
    padding: 3px 5px;  /* Smaller padding to reduce thickness */
    font-size: 0.5em;  /* Adjust font size for a smaller appearance */
    line-height: 1;  /* Reduce line height for compactness */
    z-index: 1000;  /* Ensures it stays on top */
    box-shadow: 0px -1px 3px rgba(0, 0, 0, 0.2); /* Softer shadow */
}
.footer a {
    color: #007BFF;
    text-decoration: none;
}
.footer a:hover {
    text-decoration: underline;
}
</style>
<div class="footer">
    Not affiliated with or endorsed by Wizards of the Coast.
    For research and educational purposes only.
</div>
"""
st.markdown(footer, unsafe_allow_html=True)



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
st.session_state.setdefault("session_encounters", [])
st.session_state.setdefault("blocks", False)
# st.session_state.setdefault("start", False)

if "start" not in st.session_state:
    st.session_state.start = False

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
def log_debug(message):
    # Append the message and force flush the print to the terminal as well.
    st.session_state.debug_logs.append(message)
    print(message, flush=True)


def reset_session():
    # Keep session_encounters and any other keys you want to persist
    keys_to_preserve = {"session_encounters"}
    for key in list(st.session_state.keys()):
        if key not in keys_to_preserve:
            del st.session_state[key]
    st.session_state.counter = 0
    st.rerun()
 
    

@st.dialog("Statistics Popup", width="large")
def show_statistics(wins, rounds, dmgs, deaths, healths):
    st.write("Here are the statistics for the last 5 encounters:")
    st.write(f"Win probability: {wins}")
    st.write(f"Rounds number: {rounds}")
    st.write(f"Player damage: {dmgs}")
    st.write(f"Death number: {deaths}")
    st.write(f"Team health: {healths}")


    st.write("If you want to play again, press the Reset Session button below!")
    # Reset button
    if st.button("New Game!"):
        reset_session()
        

def get_next_party_matrix():
    idx = rnd.choice(st.session_state.party_indices)
    return st.session_state.precomputed_parties[idx], st.session_state.precomputed_class_names[idx]

def generate_encounter():
    st.session_state.generated_party, st.session_state.generated_class_names = get_next_party_matrix()
    st.session_state.party_exp = calculate_party_exp(st.session_state.generated_class_names, "deadly")
    st.session_state.start = True
    

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
enemy_option_to_xp = {opt: xp for opt, xp in zip(enemy_options, [0] + list(exp_dict.values()))}

def compute_enemy_exp(selected_options):
    xp_values = [enemy_option_to_xp[o] for o in selected_options if enemy_option_to_xp[o] > 0]
    return sum(xp_values) * MULTIPLIER_TABLE.get(len(xp_values), 4.0)

def calculate_party_exp(party, difficulty="deadly"):
    EXP_THRESHOLDS = {"easy": 250, "medium": 500, "hard": 750, "deadly": 1100}
    return EXP_THRESHOLDS[difficulty] * len(party)

# --------------------- UI ELEMENTS ---------------------
st.title("🧙‍♂️ D&D Encounter Balance Tester 🐉")

if st.session_state.blocks:
    # Show simulation results and statistics modal.
    simulation_results = []
    for encounter in st.session_state.session_encounters:
        party = encounter["party"]
        enemy_names = [
            enemy.split("->")[0].strip()
            for enemy in encounter["enemies"]
            if enemy != enemy_options[0]
        ]
        win_prob, rounds_num, dmg_player, death_num, team_health = benchmark(party, enemy_names, verbose=False)
        simulation_results.append({
            "win_prob": win_prob,
            "rounds_num": rounds_num,
            "dmg_player": dmg_player,
            "death_num": death_num,
            "team_health": team_health
        })
    wins = np.round(np.mean([r["win_prob"] for r in simulation_results]), 2)
    rounds = np.round(np.mean([r["rounds_num"] for r in simulation_results]), 2)
    dmg = np.round(np.mean([r["dmg_player"] for r in simulation_results]), 2)
    deaths = np.round(np.mean([r["death_num"] for r in simulation_results]), 2)
    healths = np.round(np.mean([r["team_health"] for r in simulation_results]), 2)

    @st.dialog("Here are the average statistics for the simulated battles!!", width="large")
    def show_statistics():

        st.write(f"**Win probability: {wins*100}%** - Probability of the hero team winning the encounter.")
        st.write(f"**Rounds number: {rounds}** - Number of rounds per battle (measures fight duration).")
        # st.write(f"**Damage: {dmg}** - Average damage dealt per fighter (heroes and enemies).")
        st.write(f"**Total Party Kill: {deaths}** - Number of hero deaths per simulation.")
        st.write(f"**Team health: {healths*100}%** - Percentage of total HP remaining after battle.")
        st.write("If you want to play again, press the **New Game** button below!")
        if st.button("New Game!"):
            reset_session()

    show_statistics()
    st.markdown("---")
    if st.button("🔄 Reset Game"):
        reset_session()
else:
    # --------------------- DESCRIPTION CHECK ---------------------
    if st.session_state.start is False:
        # Landing page description (first time the user lands)
        st.subheader("Test your skills as a Dungeon Master!")
        st.markdown(
            """
            This is a research tool to test your expertise as Dungeon Master in creating balanced encounters for your party! \n
            A balanced encounter should be challenging but not deadly for the party. \n
            Therefore, given the Party XP the Dungeon Master should select a team of enemies with a similar XP value. 

            To simulate the fights and get your statistics as a Dungeon Master, you need to submit 3 times!

            Your selections will be stored in a JSON file and uploaded to GitHub for further analysis.
            Good luck and have fun!
            """
        )
        st.subheader("How to play:")
        
        st.markdown(
            """
            1. Click the button to generate a random adventuring party.
            2. Each party member is Level 5, with distinct classes, stats, and abilities. Click on a class name to review its details.
            3. Based on the party's composition, select an enemy team (up to 8 creatures).
            4. The tool will calculate the total enemy XP and compare it against the party XP (deadly setting).
            5. Adjust your enemy selection to ensure the challenge level is appropriate:
               - Too Low? The fight will be too easy and unengaging.
               - Too High? It could become overwhelming and result in a total party wipe.
               - Just Right? The battle feels intense but winnable, requiring teamwork and strategy.
            """
        )

        
        st.subheader("Select your expertise level as Dungeon Master:")
        expertise_levels = [
            "Noob - Still learning what a d20 is",
            "Amateur - Can handle small encounters, but big foes are scary",
            "Skilled - Runs epic battles with minimal confusion",
            "Expert - NPC voices so good, players forget it's you",
            "Legendary - Godlike storyteller, even Tiamat takes notes"
        ]
        st.session_state.selected_expertise = st.selectbox("Choose your expertise level:", expertise_levels)
        st.markdown("---")
    else:
        # After the first encounter is generated, show the new description.
        
        st.markdown("### 🧾 Encounter Balancing: Key Concepts")

        st.write("""
        When designing encounters, keep in mind the **official XP guidelines** from the *Dungeon Master’s Guide (DMG)*.
        A well-balanced encounter should be **challenging but not overwhelmingly deadly** to keep players engaged.
        """)

        # Step 1: Calculate Party Thresholds
        st.markdown("### **Step 1: Calculate Party Thresholds**")

        st.write("""
        Each adventurer level has **three XP thresholds** that determine the difficulty of an encounter:
        - **Easy:** The party can win with little effort or risk.
        - **Medium:** A fair challenge that might require some resources (e.g., spells, healing, positioning).
        - **Hard:** A dangerous fight where players must strategize 
        - **Deadly:** A fight that could result in **character deaths** if they make poor choices or get unlucky.
                 
        The tool sets the Deadly threshold as the default party XP, aiming to create a true challenge. However, be cautious—push too hard, and you might wipe out the entire party!
        """)

        # st.markdown("### **XP Thresholds for a Level 5 Party**")
        # st.table({
        #     "Difficulty": ["Easy", "Medium", "Hard", "Deadly"],
        #     "XP per Character": ["250 XP", "500 XP", "750 XP", "1,100 XP"],
        #     "XP for 4-Player Party": ["1,000 XP", "2,000 XP", "3,000 XP", "4,400 XP"]
        # })

        # st.write("""
        # Multiply these values by the number of players in your party to get the **party XP budget**.
        # """)

        # Step 2: Apply Encounter Multipliers
        st.markdown("### **Step 2: Apply the Encounter Multiplier**")

        st.write("""
        The **number of enemies** affects difficulty beyond their raw XP values.
        More enemies = **harder fight** because of increased attacks and action economy.
        The DMG provides an **XP multiplier** to account for this:
        """)

        st.markdown("#### **Encounter XP Multipliers**")
        st.table({
            "Number of Enemies": ["1", "2", "3–6", "7–10", "11–14", "15+"],
            "XP Multiplier": ["×1", "×1.5", "×2", "×2.5", "×3", "×4"]
        })

        st.write("""
        For example, if you choose **four enemies worth 500 XP each (2,000 XP total)**,  
        the **actual challenge XP** would be:

        `2,000 XP × 2 (multiplier) = 4,000 XP → Very Hard/Deadly for a 4-player party!`
        """)

        # Step 3: Adjust and Fine-Tune
        st.markdown("### **Step 3: Adjust and Fine-Tune**")

        st.write("""
        - **Fewer, stronger enemies** (e.g., one big boss or a couple of elite foes) make for **high-risk, high-reward** fights.
        - **More numerous but weaker enemies** (e.g., a swarm of goblins or skeletons) can **overwhelm players with action economy**, making the fight trickier than it looks.
        - Consider the **party’s strengths and weaknesses**—some groups handle hordes better, while others struggle with single strong foes.
        """)



    # --------------------- ENCOUNTER GENERATION BUTTON ---------------------
    col_gen, col_counter = st.columns([3, 1])
    subs = 3 - st.session_state.counter
    with col_gen:
        st.button("🎲 Generate Encounter 🎲", on_click=generate_encounter, disabled=st.session_state.blocks)
    with col_counter:
        st.metric(label="MISSING SUBMISSIONS FOR THE FIGHT!!!", value= subs)

    # --------------------- DISPLAY GENERATED PARTY & ENEMY SELECTION ---------------------
    if st.session_state.generated_party is not None:
        st.subheader(f"Party XP: {st.session_state.party_exp}")

        # st.session_state.has_generated = True


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
        
        enemy_total_exp = compute_enemy_exp(selected_enemies)
        st.subheader(f"**Enemy Encounter XP:** {enemy_total_exp}")

        col_sub, col_res = st.columns([3, 1])
        with col_res:
            if st.button("🔄 Reset Game"):
                reset_session()

        with col_sub:
            if st.button("🛡️ Submit Decision ⚔️", ):
                # Check if at least one enemy is selected (i.e. not "None -> 0 EXP")
                if not any(choice != enemy_options[0] for choice in selected_enemies):
                    st.warning(
                        "Please, to submit you have at least to pick one enemy encounter or, if you do not like the current Party Members, generate a new party by pressing the Generate Encounter button!"
                    )
                else:
                    st.session_state.counter += 1
                    encounter_data = {
                        "expertise": st.session_state.selected_expertise,
                        "party": list(st.session_state.generated_class_names),
                        "party_exp": st.session_state.party_exp,
                        "enemies": selected_enemies,
                        "enemy_exp": enemy_total_exp
                    }
                    new_line = json.dumps(encounter_data)
                    st.session_state.session_encounters.append(encounter_data)
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
                        if key not in ["counter", "git_filename", "parties", "enemies", "session_encounters", "blocks", "start", "selected_expertise"]:
                            del st.session_state[key]
                    st.session_state.counter = counter

                    # If fewer than 5 encounters have been submitted, reset party and enemy selections for a new encounter.
                    if st.session_state.counter < 3:
                        # Clear the current party so that a new one is generated on the next run.
                        st.session_state.generated_party = None
                        st.session_state.generated_class_names = None
                        st.session_state.party_exp = 0
                        # Clear enemy selection keys so the selectboxes reset to default.
                        for i in range(1, 9):
                            if f"enemy_{i}" in st.session_state:
                                del st.session_state[f"enemy_{i}"]
                        st.rerun()
                    # If 5 encounters have been submitted, run simulations and show a fullscreen modal popup.
                    else:
                        st.session_state.is_locked = True
                        st.session_state.blocks = True
                        st.rerun()

    


    


                        