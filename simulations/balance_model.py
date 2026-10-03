#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEADLOCK: Sobrevive o Traiciona - Simulador de Balance Matemático
Modelo Monte Carlo para calibración de HP, duración de turnos y punto de quiebre de recursos.
"""

import random
import sys
from typing import Dict, List, Tuple

# Asegurar codificación UTF-8 en terminales de Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# Configuración del Modelo Matemático
NUM_SIMULATIONS = 1000
TOTAL_TURNS = 12            # 12 semanas = "3 meses"
INITIAL_HP = 12             # HP base por facción (rango 10-14)
NUM_FACTIONS = 4            # 4 facciones humanas
FOOD_BURN_RATE = 1          # Comida consumida por facción viva en cada turno
INITIAL_FOOD_PER_FACTION = 2

# Probabilidad de dados D6
# 1-2: Fallo (0 daño)
# 3-5: Éxito Normal (2 daño base o mitiga defensa)
# 6:   Éxito Crítico (3 daño o brecha directa)
def roll_d6() -> Tuple[int, str]:
    roll = random.randint(1, 6)
    if roll <= 2:
        return roll, "FALLO"
    elif roll <= 5:
        return roll, "EXITO_NORMAL"
    else:
        return roll, "EXITO_CRITICO"

class GameSimulation:
    def __init__(self, initial_hp: int = INITIAL_HP, total_turns: int = TOTAL_TURNS):
        self.total_turns = total_turns
        self.initial_hp = initial_hp
        self.hp = [initial_hp] * NUM_FACTIONS
        self.food = [INITIAL_FOOD_PER_FACTION] * NUM_FACTIONS
        self.wood = [1] * NUM_FACTIONS
        self.medicine = [1] * NUM_FACTIONS
        self.barricades = [0] * NUM_FACTIONS
        self.alive = [True] * NUM_FACTIONS
        self.first_death_turn = None
        self.first_betrayal_turn = None
        self.total_betrayals = 0

    def run(self) -> Dict[str, any]:
        for turn in range(1, self.total_turns + 1):
            alive_indices = [i for i, is_alive in enumerate(self.alive) if is_alive]
            if not alive_indices:
                break

            # 1. Fase de Amanecer: Evento del Overlord (40% de probabilidad de condición global)
            if random.random() < 0.40:
                # Evento global: consume 1 madera o hace 1 daño si no hay madera
                for idx in alive_indices:
                    if self.wood[idx] > 0:
                        self.wood[idx] -= 1
                    else:
                        self.hp[idx] -= 1
                        if self.hp[idx] <= 0:
                            self.alive[idx] = False
                            if self.first_death_turn is None:
                                self.first_death_turn = turn

            # 2. Fase de Acción Humana: Generación de recursos y posible traición
            alive_indices = [i for i, is_alive in enumerate(self.alive) if is_alive]
            for idx in alive_indices:
                # Cada facción roba 1-2 recursos al azar
                r_type = random.choice(["food", "wood", "medicine"])
                if r_type == "food":
                    self.food[idx] += 1
                elif r_type == "wood":
                    self.wood[idx] += 1
                else:
                    self.medicine[idx] += 1

                # Si tiene madera suficiente, construye barricada (hasta máx 3)
                if self.wood[idx] >= 2 and self.barricades[idx] < 3:
                    self.wood[idx] -= 2
                    self.barricades[idx] += 1

                # Curación si HP es bajo y tiene medicina
                if self.hp[idx] <= 6 and self.medicine[idx] >= 1:
                    self.medicine[idx] -= 1
                    self.hp[idx] = min(self.initial_hp, self.hp[idx] + 2)

                # TRIGGER DE TRAICIÓN: Si a una facción le falta comida para el turno
                if self.food[idx] < FOOD_BURN_RATE:
                    targets = [t for t in alive_indices if t != idx and self.food[t] > 1]
                    if targets:
                        target = random.choice(targets)
                        self.food[target] -= 1
                        self.food[idx] += 1
                        self.total_betrayals += 1
                        if self.first_betrayal_turn is None:
                            self.first_betrayal_turn = turn

            # 3. Fase de Noche: Ataque del Overlord contra una facción viva al azar
            alive_indices = [i for i, is_alive in enumerate(self.alive) if is_alive]
            if alive_indices:
                target_faction = random.choice(alive_indices)
                _, outcome = roll_d6()
                if outcome == "EXITO_NORMAL":
                    raw_damage = 2
                    if self.barricades[target_faction] > 0:
                        self.barricades[target_faction] -= 1
                        raw_damage = 1
                    self.hp[target_faction] -= raw_damage
                elif outcome == "EXITO_CRITICO":
                    raw_damage = 3
                    self.barricades[target_faction] = 0  # destruye barricadas
                    self.hp[target_faction] -= raw_damage

                if self.hp[target_faction] <= 0:
                    self.alive[target_faction] = False
                    if self.first_death_turn is None:
                        self.first_death_turn = turn

            # 4. Fase de Mantenimiento: Consumo de comida
            alive_indices = [i for i, is_alive in enumerate(self.alive) if is_alive]
            for idx in alive_indices:
                if self.food[idx] >= FOOD_BURN_RATE:
                    self.food[idx] -= FOOD_BURN_RATE
                else:
                    # Inanición: -2 HP
                    self.hp[idx] -= 2
                    if self.hp[idx] <= 0:
                        self.alive[idx] = False
                        if self.first_death_turn is None:
                            self.first_death_turn = turn

        survivors = sum(1 for is_alive in self.alive if is_alive)
        return {
            "survivors": survivors,
            "first_death_turn": self.first_death_turn or (self.total_turns + 1),
            "first_betrayal_turn": self.first_betrayal_turn or (self.total_turns + 1),
            "total_betrayals": self.total_betrayals,
            "final_hp": list(self.hp)
        }

def run_monte_carlo(num_sims: int = NUM_SIMULATIONS, initial_hp: int = INITIAL_HP) -> None:
    print(f"=================================================================")
    print(f"🧟‍♂️ DEADLOCK - SIMULACIÓN MONTE CARLO DE BALANCE ({num_sims} PARTIDAS)")
    print(f"   Config: HP Base = {initial_hp} | Duración = {TOTAL_TURNS} Turnos | Facciones = {NUM_FACTIONS}")
    print(f"=================================================================\n")

    results = [GameSimulation(initial_hp=initial_hp).run() for _ in range(num_sims)]

    survivor_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    early_deaths = 0  # Muertes en Turno 1 o 2
    betrayal_turns = []

    for r in results:
        surv = r["survivors"]
        survivor_counts[surv] += 1
        if r["first_death_turn"] <= 2:
            early_deaths += 1
        if r["first_betrayal_turn"] <= TOTAL_TURNS:
            betrayal_turns.append(r["first_betrayal_turn"])

    avg_survivors = sum(r["survivors"] for r in results) / num_sims
    early_death_rate = (early_deaths / num_sims) * 100
    avg_first_betrayal = (sum(betrayal_turns) / len(betrayal_turns)) if betrayal_turns else 0
    overlord_win_rate = (survivor_counts[0] / num_sims) * 100

    print("📊 DISTRIBUCIÓN DE SUPERVIVIENTES AL FINAL DEL JUEGO (Turno 12):")
    for count in range(5):
        pct = (survivor_counts[count] / num_sims) * 100
        bar = "█" * int(pct // 2)
        label = "Victoria Total Overlord" if count == 0 else f"{count} Superviviente(s)"
        print(f"  [{count}] {label:<24}: {pct:5.1f}% | {bar}")

    print("\n🎯 MÉTRICAS CLAVE DE DISEÑO Y EQUILIBRIO:")
    print(f"  • Supervivientes Promedio por Partida : {avg_survivors:.2f} / 4 facciones")
    print(f"  • Victoria Absoluta del Overlord     : {overlord_win_rate:.1f}%")
    print(f"  • Muerte Prematura (Turnos 1 o 2)    : {early_death_rate:.1f}%  {'✅ (Saludable < 5%)' if early_death_rate < 5 else '⚠️ (Demasiado castigador)'}")
    print(f"  • Turno Promedio de Primera Traición : Turno {avg_first_betrayal:.1f} {'✅ (Ocurre en fase media)' if 3 <= avg_first_betrayal <= 6 else '⚠️'}")

    print("\n💡 RECOMENDACIÓN PARA LA SESIÓN DE HOY:")
    if early_death_rate > 5:
        print("  ⚠️ El HP inicial o la defensa de inicio es baja. Aumentar HP a 14 o iniciar con 1 Barricada activa.")
    elif avg_survivors > 2.5:
        print("  ⚠️ El juego es demasiado generoso con los humanos. Aumentar agresividad del Overlord o reducir comida inicial.")
    else:
        print("  ✅ Los números actuales (HP 12, 12 turnos) generan el arco dramático ideal: cooperación inicial, quiebre en Turno 4-5 y 1-2 supervivientes al final.")
    print("=================================================================\n")

if __name__ == "__main__":
    hp_arg = int(sys.argv[1]) if len(sys.argv) > 1 else INITIAL_HP
    run_monte_carlo(initial_hp=hp_arg)
