import tkinter as tk
from tkinter import ttk, messagebox

# Path abilities
PATH_ABILITIES = {
    "Damage Path": ["Critical", "Marker", "Element Boost", "Disruption"],
    "Range Path": ["Surge", "Assassin", "Ricochet", "Overload"],
    "Speed Path": ["Additional", "Dodge", "Employment", "Element Resist"]
}

# Ability effects
ABILITIES = {
    "Critical":        {"DMG_MULTI": 1 + 0.10 * 1.0},
    "Marker":          {"DMG_MULTI": 1 + 0.10 * 0.30},
    "Element Boost":   {},
    "Disruption":      {"NOTES": "Ignore for DPS unless shields exist."},
    "Surge":           {"NOTES": "Situational, skip for baseline DPS."},
    "Assassin":        {"DMG_MULTI": 1 + 0.15 * 1.0},
    "Ricochet":        {"DMG_MULTI": 1 + 0.10 * 0.40},
    "Overload":        {"DMG_MULTI": 1 + 0.05 * 0.5},
    "Additional":      {"DMG_MULTI": 1 + 0.10 * 1.0},
    "Dodge":           {"NOTES": "No DPS effect."},
    "Employment":      {"NOTES": "No DPS effect."},
    "Element Resist":  {},
}

PATHS = {
    "Damage Path": {"DMG": 1.15, "RNG": 1.05, "SPD": 0.95},
    "Range Path":  {"DMG": 1.05, "RNG": 1.125, "SPD": 0.95},
    "Speed Path":  {"DMG": 1.05, "RNG": 1.05, "SPD": 0.90}
}
PATH_LIST = list(PATHS.keys())

# Traits
TRAITS = [
    "None",
    "Tank", "Perception 1", "Perception 2", "Perception 3",
    "Dexterity 1", "Dexterity 2", "Dexterity 3",
    "Prodigy", "Zenkai 1", "Zenkai 2", "Zenkai 3",
    "Midas", "Sharpshooter", "Tempest", "Companion", "Bloodlust", "Corrupted", "Genesis", "All Star"
]

# DoT Effects
DOT_EFFECTS = ["None", "Bleed", "Fire"]

def trait_effects(trait, base_placements):
    effects = {
        "DMG": 1.0,
        "RNG": 1.0,
        "SPD": 1.0,
        "TRUE_DMG": 0.0,  # For Genesis
        "PLACEMENTS": base_placements,
        "DURABILITY": 1.0,  # For Tank/All Star
        "DOT_BONUS": 1.0,   # For Tempest
        "SHIELD_BYPASS": 1.0, # For Corrupted
        "COST_MULT": 1.0,    # For All Star
        "UNIT_LIMIT": None   # For All Star
    }
    if trait == "None":
        pass
    elif trait == "Tank":
        effects["DURABILITY"] = 1.5
    elif trait.startswith("Perception"):
        lv = int(trait[-1])
        rng_bonus = {1: 1.03, 2: 1.05, 3: 1.07}
        effects["RNG"] = rng_bonus.get(lv, 1.0)
    elif trait.startswith("Dexterity"):
        lv = int(trait[-1])
        spd_bonus = {1: 0.97, 2: 0.95, 3: 0.93}
        effects["SPD"] = spd_bonus.get(lv, 1.0)
    elif trait == "Prodigy":
        pass  # No DPS effect
    elif trait.startswith("Zenkai"):
        lv = int(trait[-1])
        dmg_bonus = {1: 1.05, 2: 1.07, 3: 1.10}
        effects["DMG"] = dmg_bonus.get(lv, 1.0)
    elif trait == "Midas":
        pass  # No DPS effect
    elif trait == "Sharpshooter":
        effects["RNG"] = 1.15
        effects["EXTRA_HIT"] = 0.05  # 5% damage to another enemy
    elif trait == "Tempest":
        effects["SPD"] = 0.90
        effects["DOT_BONUS"] = 1.30
    elif trait == "Companion":
        effects["PLACEMENTS"] += 1
    elif trait == "Bloodlust":
        # +10% DMG, +10% RNG, +10 stacks: Each stack +1% DMG, -1% SPD
        effects["DMG"] = 1.10 * (1.01 ** 10)
        effects["RNG"] = 1.10
        effects["SPD"] = 0.90  # -1% per stack, 10 stacks => 0.99^10 ≈ 0.904
    elif trait == "Corrupted":
        effects["SPD"] = 0.90
        effects["RNG"] += 7.5 / 100.0
        effects["SHIELD_BYPASS"] = 1.20
        effects["EXTRA_MARK"] = 1.10  # 10% mark damage
    elif trait == "Genesis":
        effects["DMG"] = 1.125
        effects["SPD"] = 0.915
        effects["RNG"] = 1.085
        effects["TRUE_DMG"] = 0.5  # 50% of damage as true damage
    elif trait == "All Star":
        effects["DMG"] = 4.0   # 300% extra means 4x base
        effects["SPD"] = 0.90
        effects["RNG"] = 1.10
        effects["DURABILITY"] = 1.5
        effects["PLACEMENTS"] = 1
        effects["COST_MULT"] = 1.75
        effects["UNIT_LIMIT"] = 1
    return effects

def dot_effect(dot_type, base_dmg, trait_dot_bonus=1.0):
    """Return (total_dot_damage_per_attack, dot_multiplier_for_dps)"""
    if dot_type == "None":
        return 0.0, 1.0
    if dot_type in ["Bleed", "Fire"]:
        # 25% of damage over 3 ticks per attack, scales with trait DoT bonus (e.g. Tempest)
        dot = base_dmg * 0.25 * trait_dot_bonus
        # Enemies under DoT take +5% more damage from attacks
        dot_mult = 1.05
        return dot, dot_mult
    return 0.0, 1.0

def calc_dps(dmg, rng, spd, path, abilities, trait, dot, placements, enemy_strong=False, enemy_weak=False):
    # Initial multipliers
    base_placements = placements
    traitfx = trait_effects(trait, base_placements)
    placements = min(traitfx["PLACEMENTS"], 10)
    if traitfx.get("UNIT_LIMIT"):
        placements = min(placements, traitfx["UNIT_LIMIT"])

    # Path effects
    p = PATHS[path]
    dmg_mult = p["DMG"] * traitfx["DMG"]
    rng_mult = p["RNG"] * traitfx["RNG"]
    spd_mult = p["SPD"] * traitfx["SPD"]
    extra_dmg_mult = 1.0

    elem_boost_count = sum(1 for ab in abilities if ab == "Element Boost")
    elem_resist_count = sum(1 for ab in abilities if ab == "Element Resist")

    for ab in abilities:
        effect = ABILITIES[ab]
        if "DMG" in effect: dmg_mult *= effect["DMG"]
        if "RNG" in effect: rng_mult *= effect["RNG"]
        if "SPD" in effect: spd_mult *= effect["SPD"]
        if "DMG_MULTI" in effect: extra_dmg_mult *= effect["DMG_MULTI"]

    # Apply Bloodlust stacks (done in traitfx), Genesis true damage (done after)
    base_dmg = dmg * dmg_mult * extra_dmg_mult
    base_spd = spd * spd_mult
    base_rng = rng * rng_mult

    # DoT calculation (before element/true adjustments)
    dot_damage, dot_mult = dot_effect(dot, base_dmg, traitfx["DOT_BONUS"])

    # Sharpshooter trait: attacks hit an extra enemy for 5% damage
    extra_hit_dmg = 0
    if trait == "Sharpshooter":
        extra_hit_dmg = base_dmg * 0.05

    # Genesis: 50% of damage as true, not affected by strong/weak for that half
    if trait == "Genesis":
        half_dmg = base_dmg * 0.5
        rest_dmg = base_dmg * 0.5
        if enemy_strong:
            rest_dmg *= 2.0
            if elem_boost_count > 0:
                rest_dmg *= (1.10) ** elem_boost_count
        elif enemy_weak:
            rest_dmg *= 0.5
            if elem_resist_count > 0:
                rest_dmg *= (1.25) ** elem_resist_count
        # True half is not affected by strong/weak
        new_dmg = half_dmg + rest_dmg
    else:
        new_dmg = base_dmg
        if enemy_strong:
            new_dmg *= 2.0
            if elem_boost_count > 0:
                new_dmg *= (1.10) ** elem_boost_count
        elif enemy_weak:
            new_dmg *= 0.5
            if elem_resist_count > 0:
                new_dmg *= (1.25) ** elem_resist_count

    # Apply Mark effect from Corrupted (marks enemies for 10% more damage)
    if trait == "Corrupted":
        new_dmg *= 1.10

    # Apply DoT bonus to attack DPS (enemy under DoT takes +5% from attacks)
    new_dmg *= dot_mult

    # Add Sharpshooter extra hit
    if extra_hit_dmg:
        new_dmg += extra_hit_dmg

    # DPS from attack
    dps = new_dmg / base_spd

    # DPS from DoT per placement
    dot_dps = dot_damage / base_spd if dot_damage else 0.0

    # Group DPS
    total_unit_dps = dps + dot_dps
    group_dps = total_unit_dps * placements

    # Handle All Star durability display
    durability_note = ""
    if traitfx["DURABILITY"] != 1.0:
        durability_note = f" (x{traitfx['DURABILITY']} Durability)"

    # Output
    return {
        "DPS": round(dps, 2),
        "DOT_DPS": round(dot_dps, 2) if dot_dps else None,
        "Total_DPS": round(total_unit_dps, 2),
        "Group_DPS": round(group_dps, 2),
        "Damage/Attack": round(new_dmg, 2),
        "Attack Interval": round(base_spd, 2),
        "Range": round(base_rng, 2),
        "Placements": placements,
        "Durability": durability_note
    }

class DPSCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DPS Calculator")
        self.geometry("510x600")
        self.resizable(True, True)
        self.create_widgets()

    def create_widgets(self):
        row = 0
        tk.Label(self, text="Base Damage:").grid(row=row, column=0, sticky="e")
        tk.Label(self, text="Range:").grid(row=row+1, column=0, sticky="e")
        tk.Label(self, text="Seconds per Attack:").grid(row=row+2, column=0, sticky="e")
        tk.Label(self, text="Placements (1-10):").grid(row=row+3, column=0, sticky="e")

        self.dmg_var = tk.DoubleVar(value=100)
        self.rng_var = tk.DoubleVar(value=20)
        self.spd_var = tk.DoubleVar(value=1.0)
        self.place_var = tk.IntVar(value=1)

        tk.Entry(self, textvariable=self.dmg_var).grid(row=row, column=1)
        tk.Entry(self, textvariable=self.rng_var).grid(row=row+1, column=1)
        tk.Entry(self, textvariable=self.spd_var).grid(row=row+2, column=1)
        tk.Spinbox(self, from_=1, to=10, textvariable=self.place_var, width=5).grid(row=row+3, column=1, sticky="w")

        tk.Label(self, text="Pick ONE Path:").grid(row=row+4, column=0, columnspan=2, pady=(8,0))
        self.path_var = tk.StringVar(value=PATH_LIST[0])
        path_combo = ttk.Combobox(self, textvariable=self.path_var, values=PATH_LIST, state="readonly")
        path_combo.grid(row=row+5, column=0, columnspan=2, sticky="we", padx=30)
        path_combo.bind("<<ComboboxSelected>>", self.update_abilities)

        tk.Label(self, text="Pick 4 Abilities:").grid(row=row+6, column=0, columnspan=2, pady=8)
        self.ability_vars = []
        self.ability_combos = []
        for i in range(4):
            var = tk.StringVar()
            combo = ttk.Combobox(self, textvariable=var, state="readonly")
            combo.grid(row=row+7 + i, column=0, columnspan=2, sticky="we", pady=2, padx=30)
            self.ability_vars.append(var)
            self.ability_combos.append(combo)

        tk.Label(self, text="Trait:").grid(row=row+11, column=0, columnspan=2, pady=(8,0))
        self.trait_var = tk.StringVar(value=TRAITS[0])
        trait_combo = ttk.Combobox(self, textvariable=self.trait_var, values=TRAITS, state="readonly")
        trait_combo.grid(row=row+12, column=0, columnspan=2, sticky="we", padx=30)
        trait_combo.bind("<<ComboboxSelected>>", self.handle_trait_change)

        tk.Label(self, text="Damage Over Time:").grid(row=row+13, column=0, columnspan=2, pady=(8,0))
        self.dot_var = tk.StringVar(value=DOT_EFFECTS[0])
        dot_combo = ttk.Combobox(self, textvariable=self.dot_var, values=DOT_EFFECTS, state="readonly")
        dot_combo.grid(row=row+14, column=0, columnspan=2, sticky="we", padx=30)

        # Enemy relation radio buttons
        tk.Label(self, text="Enemy Relation:").grid(row=row+15, column=0, columnspan=2, pady=(8,0))
        self.enemy_relation = tk.StringVar(value="neutral")
        relations = [("Neutral", "neutral"), ("This unit is strong against enemy (+100%)", "strong"), ("This unit is weak against enemy (-50%)", "weak")]
        for idx, (txt, val) in enumerate(relations):
            tk.Radiobutton(self, text=txt, variable=self.enemy_relation, value=val).grid(row=row+16+idx, column=0, columnspan=2, sticky="w", padx=30)

        tk.Button(self, text="Calculate DPS", command=self.calculate).grid(row=row+19, column=0, columnspan=2, pady=10)
        self.result = tk.Label(self, text="", font=("Arial", 12), fg="blue", justify="left", anchor="w", wraplength=470)
        self.result.grid(row=row+20, column=0, columnspan=2, sticky="we", padx=10)

        self.update_abilities()

    def update_abilities(self, event=None):
        path = self.path_var.get()
        allowed = PATH_ABILITIES[path]
        for i, combo in enumerate(self.ability_combos):
            combo.config(values=allowed)
            if self.ability_vars[i].get() not in allowed:
                self.ability_vars[i].set(allowed[0])

    def handle_trait_change(self, event=None):
        # Update placements field if All Star or Companion is picked
        trait = self.trait_var.get()
        if trait == "All Star":
            self.place_var.set(1)
        elif trait == "Companion":
            if self.place_var.get() < 2:
                self.place_var.set(2)

    def calculate(self):
        path = self.path_var.get()
        abilities = [var.get() for var in self.ability_vars]
        trait = self.trait_var.get()
        dot = self.dot_var.get()
        relation = self.enemy_relation.get()
        placements = self.place_var.get()

        if not all(abilities):
            messagebox.showerror("Error", "Please select 4 abilities.")
            return
        if placements < 1:
            messagebox.showerror("Error", "Placements must be at least 1.")
            return

        enemy_strong = relation == "strong"
        enemy_weak = relation == "weak"
        result = calc_dps(
            self.dmg_var.get(),
            self.rng_var.get(),
            self.spd_var.get(),
            path,
            abilities,
            trait,
            dot,
            placements,
            enemy_strong=enemy_strong,
            enemy_weak=enemy_weak
        )
        text = (f"Single Unit DPS: {result['DPS']}\n"
                + (f"  (Includes DoT: {result['DOT_DPS']})\n" if result['DOT_DPS'] else "")
                + f"Total Unit DPS (Attack + DoT): {result['Total_DPS']}\n"
                f"Group DPS ({result['Placements']} units): {result['Group_DPS']}\n"
                f"Damage/Attack: {result['Damage/Attack']}\n"
                f"Attack Interval: {result['Attack Interval']}s\n"
                f"Range: {result['Range']}\n"
                f"Durability Bonus:{result['Durability']}")
        self.result.config(text=text)

if __name__ == "__main__":
    DPSCalculator().mainloop()
