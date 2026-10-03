# 🧟‍♂️ DEADLOCK: Sobrevive o Traiciona

> **Juego de mesa asimétrico híbrido Euro-Ameritrash**
> **4 Facciones Humanas vs. 1 Overlord Zombie** | **60 - 90 Minutos**

---

## 📖 Visión General
**Deadlock** combina la gestión determinista de recursos mediante cartas (estilo Eurogame) con la tensión, el azar del combate y las tiradas de dados (estilo Ameritrash).

Cuatro facciones humanas supervivientes deben administrar suministros escasos para aguantar **"3 meses" (12 turnos)** hasta el rescate del gobierno. Paralelamente, un quinto jugador encarna al **Overlord Zombie**, manipulando el clima, desatando plagas y comandando hordas para aniquilar a la humanidad antes de que expire el tiempo.

> [!important] El Dilema Central
> Estadísticamente, los recursos generados en el mapa **no alcanzan para salvar a las cuatro facciones**. La cooperación inicial se desmorona inevitablemente ante el hambre y las heridas, forzando pactos rotos, saqueos nocturnos y traición abierta.

---

## ⚙️ Arquitectura de Mecánicas

| Componente | Mecánica | Descripción |
| :--- | :--- | :--- |
| **Acciones** | Puntos de Acción (AP) | Reserva fija por turno para robar cartas de recursos, cartas de acción o jugarlas al tablero. |
| **Recursos** | Economía Cuádruple | `Comida` (mantenimiento), `Madera` (defensas básicas), `Piedra` (fortificaciones), `Medicina` (infecciones y HP). |
| **Asimetría** | Overlord vs. Supervivientes | El Overlord juega Condiciones Globales (*Invierno, Hambruna*) y Ataques Directos (*Hordas Boomer, Mordidas*). |
| **Azar Táctico** | Dados por Umbrales | Tiradas de tensión con tres resultados: *Fallo*, *Éxito Normal*, *Éxito Crítico*. |

---

## 🗂️ Estructura del Repositorio

```text
deadlock-game/
├── README.md                     # Documentación principal del proyecto
├── docs/
│   ├── GDD_Deadlock.md           # Game Design Document completo
│   ├── Reglas_y_Mecanicas.md     # Manual detallado de reglas y flujo de turno
│   └── Minuta_Sesion_1.md        # Minuta de prototipado y playtest alfa
├── data/
│   ├── cards_humanos.csv         # Base de datos y balance de cartas humanas
│   └── cards_overlord.csv        # Catálogo de cartas de ataque y eventos globales
├── simulations/
│   ├── balance_model.py          # Simulador Monte Carlo en Python de supervivencia y recursos
│   └── requirements.txt          # Dependencias (pandas, numpy, matplotlib)
└── playtest/
    └── registro_playtest_sesion1.md # Plantilla de recolección de métricas ronda a ronda
```

---

## 🚀 Cómo Ejecutar la Simulación de Balance

Para comprobar la curva de supervivencia de 12 turnos y el impacto del HP inicial (10 a 14 HP):

```bash
cd simulations
python balance_model.py
```

El script simula **1,000 partidas completas** y calcula:
- Tasa de supervivencia por turno (1 a 12).
- Probabilidad de eliminación en Turnos tempranos (1-2) vs Turnos finales (9-12).
- Turno exacto de colapso de recursos donde la traición se vuelve matemáticamente óptima.
