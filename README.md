# 🛡️ D&D Encounter Generator

## 📖 About the Project  

The **D&D Encounter Generator** is an interactive **web application** designed to help Dungeon Masters (DMs) create **balanced and engaging combat encounters** for their players.  

A well-balanced encounter should be **challenging but not overwhelming**, ensuring that combat remains **exciting, strategic, and rewarding** without leading to frustration or unfair difficulty.  

This tool uses **official encounter-building rules** from the *Dungeons & Dragons 5th Edition Dungeon Master's Guide (DMG)* to calculate **experience point (XP) thresholds** and **enemy multipliers**, helping DMs craft encounters that are properly tuned to their party's strength.  

---

## 🎯 **Project Goals**  

- **Teach DMs how to balance encounters effectively** using XP values and multipliers.  
- **Provide an interactive tool** for selecting enemies and immediately calculating the encounter difficulty.  
- **Encourage strategic thinking** by considering action economy, enemy variety, and party composition.  
- **Streamline the DM's preparation process** by quickly generating encounter ideas.  

---

## 🚀 **How It Works**  

1. **Generate a random adventuring party** with a button click.  
2. **View character details** by clicking on their class names.  
3. **Choose a set of enemies** (up to 8 creatures) to challenge the party.  
4. The app **calculates the total enemy XP** and applies the **encounter multiplier** based on the number of enemies.  
5. The tool then **compares the enemy XP to the party’s XP thresholds**, indicating whether the fight is **Easy, Medium, Hard, or Deadly**.  
6. Adjust your selection to **fine-tune the encounter balance** before finalizing your battle!  

---

## 🔧 **Encounter Balancing: Key Rules Used**  

The app follows the **official XP budgeting system** from the DMG:  

1. **XP Thresholds for a Level 5 Party (Example for 4 Players)**  
   | **Difficulty** | **XP per Character** | **XP for 4-Player Party** |
   |--------------|------------------|---------------------|
   | Easy        | 250 XP           | 1,000 XP           |
   | Medium      | 500 XP           | 2,000 XP           |
   | Hard        | 750 XP           | 3,000 XP           |
   | Deadly      | 1,100 XP         | 4,400 XP           |

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

## 🏗️ **Tech Stack**  

- **[Streamlit](https://streamlit.io/)** – Used to build the web application.  
- **Python** – Backend calculations for encounter difficulty.  
- **D&D 5e Mechanics** – XP budgeting system from the *Dungeon Master's Guide*.  

---

## 🎮 **How to Run the Project Locally**  

1. **Clone the repository:**  
   ```bash
   git clone https://github.com/your-username/dd-encounter-generator.git
   cd dd-encounter-generator
