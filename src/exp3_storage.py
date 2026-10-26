"""
Experiment 3: Multi-Agent Coordination of Distributed Energy Storage for
Resilience. When a fault islands a zone of the IEEE 33-bus feeder from
the substation and no tie-switch can fully restore it (Experiment 1
identified 11/32 such fault scenarios), locally installed battery storage
is the only remaining resource able to sustain load. We compare:
  (a) Uncoordinated dispatch: each battery serves only the load
      electrically nearest to it, greedily, until its own state of
      charge (SoC) is exhausted, with no information sharing.
  (b) Coordinated multi-agent dispatch: battery agents exchange SoC and
      local critical-load information with zone neighbors each hour (a
      simple consensus/negotiation round) and jointly prioritize
      critical loads across the whole islanded zone, shifting power from
      a battery with surplus margin to a neighbor serving a critical
      load that would otherwise be shed.
"""
import os as _o, os.path as _p
_o.chdir(_p.dirname(_p.dirname(_p.abspath(__file__))))  # run from the repo root: portable paths
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')
from grid_env import build_base_net, get_load_by_bus, ZONE_OF_BUS, downstream_deenergized_buses

net0 = build_base_net()
loads = get_load_by_bus(net0)  # MW per bus

# Select a realistic, moderate-sized islanding scenario: a single fault
# whose downstream zone is normally restorable by a tie-switch (per
# Experiment 1), but here we consider the resilience-planning-relevant
# N-1-1 case where a coincident second failure (e.g., the alternate-path
# tie breaker is also out of service, as can happen during storms with
# multiple simultaneous equipment failures) leaves tie-switch restoration
# unavailable, so the only remaining resource is local battery storage.
faulted_line = 8
islanded_buses = sorted(downstream_deenergized_buses(net0, faulted_line))
print(f"Using fault on line {faulted_line} (N-1-1: tie-switch restoration assumed "
      f"unavailable): islands buses {islanded_buses}")

# Mark a subset of islanded buses as carrying "critical" load (e.g., a
# clinic or water pumping station), consistent with typical resilience
# planning practice.
rng = np.random.default_rng(2)
critical_buses = sorted(rng.choice(islanded_buses, size=max(1, len(islanded_buses) // 3),
                                    replace=False).tolist())
print(f"Critical-load buses in islanded zone: {critical_buses}")

# Install battery storage at 3 buses within the islanded zone (evenly
# spaced along the feeder), each sized to a fraction of local peak load.
battery_buses = islanded_buses[::max(1, len(islanded_buses) // 3)][:3]
BATTERY_CAPACITY_MWH = {b: 0.15 for b in battery_buses}  # each ~150 kWh
BATTERY_MAX_POWER_MW = {b: 0.05 for b in battery_buses}   # each ~50 kW max output

HOURS = 24
dt = 1.0  # hour


def simulate(coordinated, seed=0):
    r = np.random.default_rng(seed)
    soc = {b: BATTERY_CAPACITY_MWH[b] for b in battery_buses}
    critical_served_hours = {b: 0 for b in islanded_buses}
    energy_delivered_critical = 0.0
    energy_delivered_noncritical = 0.0
    soc_trace = {b: [] for b in battery_buses}

    # crude assignment: each islanded bus is served by its nearest battery bus
    def nearest_battery(bus):
        return min(battery_buses, key=lambda b: abs(b - bus))

    for h in range(HOURS):
        demand_this_hour = {b: loads[b] * (0.85 + 0.3 * r.random()) for b in islanded_buses}
        supply_by_battery = {b: 0.0 for b in battery_buses}

        if not coordinated:
            # Uncoordinated: each battery independently serves only its
            # nearest-assigned buses, critical or not, first-come order,
            # until its own SoC for this hour is exhausted.
            for bat in battery_buses:
                served_buses = [b for b in islanded_buses if nearest_battery(b) == bat]
                # serve critical first locally, but battery has NO visibility
                # into whether a *neighboring* battery is overloaded
                budget = min(BATTERY_MAX_POWER_MW[bat] * dt, soc[bat])
                for b in sorted(served_buses, key=lambda x: x not in critical_buses):
                    need = demand_this_hour[b] * dt
                    give = min(need, budget)
                    budget -= give
                    soc[bat] -= give
                    if b in critical_buses:
                        energy_delivered_critical += give
                        if give >= need - 1e-9:
                            critical_served_hours[b] += 1
                    else:
                        energy_delivered_noncritical += give
        else:
            # Coordinated: pool this hour's available battery budget
            # (one round of SoC-sharing among the 3 battery agents) and
            # serve ALL critical loads in the islanded zone first, from
            # whichever battery still has margin, before any
            # non-critical load anywhere in the zone.
            remaining_soc = dict(soc)

            def draw(amount):
                """Draw `amount` MWh from whichever battery has the most
                remaining SoC first (a simple coordinated allocation)."""
                drawn = 0.0
                order = sorted(battery_buses, key=lambda b: -remaining_soc[b])
                for b in order:
                    if drawn >= amount - 1e-12:
                        break
                    take = min(amount - drawn, remaining_soc[b],
                               BATTERY_MAX_POWER_MW[b] * dt)
                    remaining_soc[b] -= take
                    drawn += take
                return drawn

            for b in critical_buses:
                need = demand_this_hour[b] * dt
                give = draw(need)
                energy_delivered_critical += give
                if give >= need - 1e-9:
                    critical_served_hours[b] += 1
            for b in [x for x in islanded_buses if x not in critical_buses]:
                need = demand_this_hour[b] * dt
                give = draw(need)
                energy_delivered_noncritical += give
            for bt in battery_buses:
                soc[bt] = remaining_soc[bt]

        for bt in battery_buses:
            soc_trace[bt].append(soc[bt])

    critical_fully_served_frac = np.mean([critical_served_hours[b] / HOURS for b in critical_buses])
    critical_energy_needed = sum(
        loads[b] * dt for h in range(HOURS) for b in critical_buses
    ) * 1.0  # nominal (unscaled) needed energy, for a stable denominator across runs
    critical_adequacy = energy_delivered_critical / critical_energy_needed if critical_energy_needed > 0 else 0.0
    return {
        "energy_delivered_critical_mwh": energy_delivered_critical,
        "energy_delivered_noncritical_mwh": energy_delivered_noncritical,
        "critical_fully_served_frac": critical_fully_served_frac,
        "critical_energy_adequacy": critical_adequacy,
        "soc_trace": {str(k): v for k, v in soc_trace.items()},
    }


N_SEEDS = 20
uncoord_results = [simulate(False, seed=s) for s in range(N_SEEDS)]
coord_results = [simulate(True, seed=s) for s in range(N_SEEDS)]

uncoord_crit = np.mean([r["critical_fully_served_frac"] for r in uncoord_results])
coord_crit = np.mean([r["critical_fully_served_frac"] for r in coord_results])
uncoord_energy = np.mean([r["energy_delivered_critical_mwh"] for r in uncoord_results])
coord_energy = np.mean([r["energy_delivered_critical_mwh"] for r in coord_results])
uncoord_adeq = np.mean([r["critical_energy_adequacy"] for r in uncoord_results]) * 100
coord_adeq = np.mean([r["critical_energy_adequacy"] for r in coord_results]) * 100

print(f"\nUncoordinated: critical-load hours fully served = {uncoord_crit*100:.1f}%, "
      f"critical energy adequacy = {uncoord_adeq:.1f}%, "
      f"critical energy delivered = {uncoord_energy*1000:.1f} kWh")
print(f"Coordinated:   critical-load hours fully served = {coord_crit*100:.1f}%, "
      f"critical energy adequacy = {coord_adeq:.1f}%, "
      f"critical energy delivered = {coord_energy*1000:.1f} kWh")

with open("./data/exp3_storage.json", "w") as f:
    json.dump({
        "faulted_line": faulted_line, "islanded_buses": islanded_buses,
        "critical_buses": critical_buses, "battery_buses": battery_buses,
        "hours": HOURS, "n_seeds": N_SEEDS,
        "uncoordinated_example_trace": uncoord_results[0],
        "coordinated_example_trace": coord_results[0],
        "summary": {
            "uncoordinated_critical_served_pct": float(uncoord_crit * 100),
            "coordinated_critical_served_pct": float(coord_crit * 100),
            "uncoordinated_critical_energy_kwh": float(uncoord_energy * 1000),
            "coordinated_critical_energy_kwh": float(coord_energy * 1000),
            "uncoordinated_critical_adequacy_pct": float(uncoord_adeq),
            "coordinated_critical_adequacy_pct": float(coord_adeq),
        }
    }, f, indent=2)
print("Saved exp3_storage.json")
