# 🧙‍♂️ D&D Encounter Balance Tester 🐉

## [**Test your skills as a Dungeon Master!!!**](https://dnddmquestionary-hbnpkcguffzs55scdltrmv.streamlit.app/)

## 📖 About the Project  

The **D&D Encounter Generation Tester** is an interactive **web application** designed to help Dungeon Masters (DMs) test their skills in creating **balanced and engaging combat encounters** for their players.  

A well-balanced encounter should be **challenging but not overwhelming**, ensuring that combat remains **exciting, strategic, and rewarding** without leading to frustration or unfair difficulty.  

This tool uses **official encounter-building rules** from the *Dungeons & Dragons 5th Edition Dungeon Master's Guide (DMG)* to calculate **experience point (XP) thresholds** and **enemy multipliers**, helping DMs craft encounters that are properly tuned to their party's strength.  

---

## 🎯 **Project Goals**  

- **Teach DMs how to balance encounters effectively** using XP values and multipliers.  
- **Provide an interactive tool** for selecting enemies and immediately calculating the encounter difficulty.  
- **Encourage strategic thinking** by considering action economy, enemy variety, and party composition.  
- **Collect data from human Dungeon Masters** to analyze and understand how real DMs balance challenging fights, improving encounter design recommendations.  


---

## 🚀 **How It Works**  

1. **Generate a random adventuring party** with a button click.  
2. **View character details** by clicking on their class names.  
3. **Choose a set of enemies** (up to 8 creatures) to challenge the party.  
4. The app **calculates the total enemy XP** and applies the **encounter multiplier** based on the number of enemies. 
5. After submitting **3 sets** of enemies, the app will simulate the fights of the selected encounters.
6. To overcome the **stocasticity of dice rolling** each combat is simulated 100 times.
7. At the end of the simulated fights, the **average statistics** for the selections made will be displayed!


[📺 Click here to watch the tutorial](DnDTutorial.mp4)

---

## 🔧 **Encounter Balancing: Key Rules Used**  

The app follows the **official XP budgeting system** from the DMG:  

1. **XP Thresholds for a Level 5 Party (Example for 4 Players)**  
   | **Difficulty** | **XP per Character** | **XP for 4-Player Party** |
   |--------------|------------------|---------------------|
   | Easy        | 250 XP           | 1,000 XP           |
   | Medium      | 500 XP           | 2,000 XP           |
   | Hard        | 750 XP           | 3,000 XP           |
   | Deadly      | 1100 XP         | 4,400 XP           |

2. **Encounter XP Multipliers Based on Number of Enemies**  
   | **Number of Enemies** | **XP Multiplier** |
   |----------------------|----------------|
   | 1  | ×1 |
   | 2  | ×1.5 |
   | 3–6  | ×2 |
   | 7–10  | ×2.5 |
   | 11–14  | ×3 |
   | 15+  | ×4 |

3. **Action Economy Matters** – More enemies can be harder even if their XP is lower!  

---

## 🎩 **References**  

- **[DnDSimulator](https://github.com/DanielK314/DnDSimulator.git)** – Used to simulate the fights between the random party and the selected encounters. Remember to leave a ⭐ on this incredible project!  
- **[Dungeons & Dragons: Dungeon Master's Guide 5e (2014)](https://dndstore.wizards.com/us/en/product/811470/2014-dungeon-master-s-guide-digital-plus-physical-bundle)** – The core rulebook for Dungeon Masters, providing guidance on encounter design, world-building, and balancing challenges. This project follows the official XP budgeting system for encounter difficulty as outlined in the DMG.  
- **[Dungeons & Dragons Beyond](https://www.dndbeyond.com/)** – A comprehensive digital toolkit for D&D 5e, including official rules, monster stats, encounter builders, and homebrew content. Used as a reference for game mechanics and encounter-building resources. 


## ⚖️ **Disclaimer & Data Collection Policy**  

1. **Not Affiliated with Wizards of the Coast**  
   This project is an independent fan-made tool and is **not affiliated with, endorsed, sponsored, or approved by Wizards of the Coast LLC**. *Dungeons & Dragons* and related materials are trademarks of Wizards of the Coast. All references to game mechanics, rules, and materials are used under fair use for educational and research purposes.  

2. **Data Collection for Research**  
   To improve encounter balancing and analyze how Dungeon Masters create combat challenges, this project **collects anonymized data** from each submitted encounter. This data is used solely for research purposes to refine encounter generation models and is never shared with third parties. By using this tool, you agree to the collection of **non-personal encounter data** for analytical purposes. From each submission, we are only interested in storing: current party, party XP, selected encounters, encounters XP and DM expertise. Each submission is stored in the [*Humans folder*](https://github.com/CarloRomeo427/DnD_DM_Questionary/tree/main/Humans).