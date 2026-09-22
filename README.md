# 🏁 MotoGP Calendar Sustainability Optimisation

**Can a smarter race calendar cut a championship's carbon footprint?**

This project models the 2025 MotoGP World Championship as an optimisation problem: reschedule 22 races around the globe to **minimise total team travel distance** — without ever sending anyone to race in unsafe heat or cold. Three different metaheuristic algorithms go head-to-head to solve it: **Simulated Annealing**, **Genetic Algorithms**, and **Particle Swarm Optimisation**.

> Built for the Numerical Optimisation module at Griffith College Dublin. **Grade: 82%**

---

## 🌍 The Problem

Motorsport travels a lot. Teams, freight, and equipment fly between continents almost every fortnight of the season, and most of that freight goes by air — the highest-carbon option available. Reducing the distance a calendar forces teams to fly is one of the more direct levers MotoGP has for cutting its CO2 footprint.

But you can't just reorder races for shorter flights. Racing at the wrong time of year in the wrong place is dangerous: too cold and tyres won't grip, too hot and riders risk heat exhaustion. So the calendar has to satisfy real constraints while still getting shorter.

**The rules the calendar has to respect:**
- 🌡️ Every race must fall in a window where the expected temperature is **between 15°C and 35°C**
- 🏖️ A **3-weekend summer shutdown** (weeks 29–31) is mandatory — no races during this period
- 🏆 **Valencia** is fixed as the season finale on weekend 46 and cannot move
- ✈️ Teams fly home after a race unless the following weekend is also a race weekend (a "double header"), in which case they fly directly to the next venue
- 🔁 All 22 races must occur exactly once, with no repeats

**The baseline:** with the 2025 calendar as published and Mugello (home to most teams) as the base, total seasonal team travel comes to **146,768 km**.

**The target:** find valid calendars that meaningfully beat that — ideally under 130,000 km, with the strongest solutions dipping below 100,000 km.

---

## ⚙️ How It Works

### 1. Build and verify the simulation
Before any optimisation happens, the project first builds a simulation that can:
- Parse raw race-weekend and track-location data from CSV
- Calculate great-circle distance between any two venues using the **Haversine formula**
- Estimate the expected temperature at a venue for a given week
- Walk through a full season and total up real travel distance under the double-header/home-travel rules above

This simulation is validated against a provided **unit-test suite** before a single optimisation run — if the simulation itself is wrong, "better" results downstream mean nothing.

### 2. Optimise the calendar
Once verified, the same simulation becomes the scoring function for three independent optimisation approaches:

| Algorithm | Library | Idea |
|---|---|---|
| 🔥 **Simulated Annealing** | `simanneal` | Gradually "cools" a single candidate calendar, accepting worse moves early on to escape bad local optima, then converging on a strong solution |
| 🧬 **Genetic Algorithms** | `deap` | Evolves a *population* of 300 candidate calendars over 1,000 generations using roulette-wheel crossover and constraint-aware mutation |
| 🐝 **Particle Swarm Optimisation** | `pyswarms` | Sends a swarm of 100 candidate calendars exploring the solution space in parallel over 1,000 iterations, each "particle" nudged by its own and the swarm's best finds |

### 3. Fix the hard constraints first
The key design decision in this project: **temperature violations are fixed before anything else.**

Randomly swapping races rarely produces a valid calendar — venues like Silverstone and Assen only have a narrow window of weeks where they're warm enough to race. Instead, every move made by all three algorithms follows the same priority order:

1. If any race is **too cold**, swap the coldest one out first
2. If any race is **too hot**, swap the hottest one out next
3. Otherwise, swap two races at random to keep exploring

This single change made the difference between algorithms that reliably converge on valid, lower-distance calendars — and ones that spend their entire run failing to find a legal solution at all.

---

## 📊 Results

- **Baseline distance:** 146,768 km (2025 calendar, Mugello home base)
- **Target range:** 100,000 – 130,000 km for a valid, optimised calendar
- **Outcome:** all three algorithms produced valid calendars landing within that target range, confirming that constraint-aware optimisation can meaningfully cut travel distance without compromising race-day safety

---

## 🛠️ Tech Stack

- **Python 3** (standard library: `csv`, `math`, `unittest`)
- [`simanneal`](https://github.com/perrygeo/simanneal) — Simulated Annealing
- [`deap`](https://github.com/DEAP/deap) — Genetic Algorithms
- [`pyswarms`](https://github.com/ljvmiranda921/pyswarms) — Particle Swarm Optimisation

No dependencies outside the Python SDK and these three optimisation libraries were used.

---

## 📁 Project Structure

```
├── motogp-calendar.py       # Simulation, unit tests, and all three optimisers
├── race-weekends.csv        # 2025 calendar: which weekend each race falls on
├── track-locations.csv      # Venue coordinates and monthly temperature estimates
└── README.md
```

---

## ▶️ Running It

```bash
# Run the unit test suite to verify the simulation
python motogp-calendar.py

# Then run the optimisation cases (uncomment in main)
# SAcases()   — Simulated Annealing
# GAcases()   — Genetic Algorithms
# PSOcases()  — Particle Swarm Optimisation
```

---

## 💡 Key Takeaway

Constraints define the search space. In a problem like this, the biggest performance gains didn't come from tuning the optimisation algorithms themselves — they came from teaching every algorithm to fix the *hardest* constraint (temperature) first. Once that was in place, all three approaches — despite working in completely different ways — converged on genuinely better, safer, lower-emission calendars.

---

**Author:** Chibuike Nwosu — [GitHub](https://github.com/chibuikeNwosu) · [LinkedIn](https://www.linkedin.com/in/chibuike-nwosu)
