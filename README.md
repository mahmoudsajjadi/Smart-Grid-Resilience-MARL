# Sustainable Smart Grid Resilience and Renewable Integration Using Multi-Agent Reinforcement Learning

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Journal: MDPI Sustainability](https://img.shields.io/badge/Journal-MDPI%20Sustainability%2018(20):10574-green.svg)](https://www.mdpi.com/2071-1050/18/20/10574)
[![DOI: 10.3390/su182010574](https://img.shields.io/badge/DOI-10.3390%2Fsu182010574-blue.svg)](https://doi.org/10.3390/su182010574)
[![Interactive Page](https://img.shields.io/badge/Interactive-Landing%20Page%20%26%20BibTeX-007acc.svg)](https://mahmoudsajjadi.github.io/papers/sustainable-smart-grid-resilience-marl.html)

Official code and data repository for the paper:  
**["Sustainable Smart Grid Resilience and Renewable Integration Using Multi-Agent Reinforcement Learning"](https://www.mdpi.com/2071-1050/18/20/10574)**  
*Seyed Mahmoud Sajjadi Mohammadabadi and Sayed Mohammad Sajjadi*  
Published in **MDPI Sustainability**, Vol. 18, Issue 20, 10574 (Special Issue: *Advances in Renewable Energy and Power Generation Technology*), 2026.  
📄 **[Read Official Open-Access Article](https://www.mdpi.com/2071-1050/18/20/10574)** • 📥 **[Download Full PDF](https://www.mdpi.com/2071-1050/18/20/10574/pdf)** • 🔗 **[DOI: 10.3390/su182010574](https://doi.org/10.3390/su182010574)** • 🎓 **[Google Scholar](https://scholar.google.com/citations?user=tkhCR5IAAAAJ&hl=en)**

---

## 📌 Graphical Abstract

<p align="center">
  <img src="figures/graphical_abstract.png" alt="Graphical Abstract" width="90%">
</p>

---

## 💡 Overview & Key Contributions

Distribution networks undergoing extreme weather events face multiple simultaneous challenges: rapid restoration under high outage counts, local voltage violations driven by distributed energy resources (DERs), and reliance on polluting diesel backup generators.

This repository provides the complete simulation environment, decentralized algorithms, and benchmark datasets introduced in the paper:

1. **Two-Tier Hierarchical Multi-Agent Framework**:
   - **Tier 1 (Restoration):** Multi-agent contextual bandit / Q-learning for bounded decentralized feeder reconfiguration that matches centralized restoration on single faults and maintains **95.2%** of optimal reward on double faults with **72–76% fewer AC power-flow feasibility evaluations**.
   - **Tier 2 (Islanded Operation):** Finite-horizon Markov Decision Process (MDP) for battery energy storage systems (BESS) delivering synchronized peak-shaving and critical-load dispatch.
2. **Communication-Efficient Decentralized Training (ComDML)**:
   - Workload-balanced decentralized model learning that reduces training wall-clock time by a factor of **1.46×** across heterogeneous agents while maintaining resilience under packet-loss rates up to 30%.
3. **Decentralized Volt–VAr Droop Control**:
   - Increases Photovoltaic (PV) hosting capacity by **51%** (from 196% to 296% of peak feeder load) without requiring communication or curtailment.
4. **Decarbonization Impact**:
   - Coordinated microgrid restoration and storage dispatch avoids **158–945 kg of CO₂ emissions per storm event** by eliminating reliance on fossil diesel backup generators.

---

## 📂 Repository Structure

```
Smart-Grid-Resilience-MARL/
├── README.md                           # Comprehensive documentation & quickstart
├── LICENSE                             # MIT License
├── requirements.txt                    # Python dependencies
├── src/
│   ├── grid_env.py                     # IEEE 33-bus & 179-bus Oberrhein network models
│   ├── exp1_restoration.py             # Exp 1: Single-fault restoration benchmark
│   ├── exp2_qlearning.py               # Exp 2: Tabular Q-learning restoration policy
│   ├── exp3_storage.py                 # Exp 3: BESS multi-agent dispatch & forecast sensitivity
│   ├── exp4_comdml.py                  # Exp 4: Latency-balanced decentralized learning
│   ├── exp5_scalability.py             # Exp 5: 33-bus vs 179-bus computational scalability
│   ├── exp5b_scaling_sweep.py          # Exp 5b: Tie-switch scaling sweep (T = 5 to 12)
│   ├── exp6_pv_hosting_capacity.py     # Exp 6: PV hosting capacity & Volt-VAr droop
│   ├── exp7_double_faults_496.py       # Exp 7: Full N-2 contingency sweep (all 496 pairs)
│   ├── make_fig1_architecture.py       # Generates Fig 1: Multi-agent system architecture
│   ├── make_fig2_topology.py           # Generates Fig 2: IEEE 33-bus zonal topology
│   ├── make_fig9_restoration_sequence.py# Generates Fig 9: Sequential restoration timeline
│   ├── make_fig10_comdml_architecture.py# Generates Fig 10: ComDML topology
│   ├── make_graphical_abstract.py      # Generates publication Graphical Abstract
│   └── make_result_figures.py          # Generates empirical results comparison plots
├── data/                               # Precomputed experimental benchmark results
│   ├── exp1_restoration.json
│   ├── exp2_qlearning.json
│   ├── exp3_storage.json
│   ├── exp4_comdml.json
│   ├── exp5_scalability.json
│   ├── exp5b_results.json
│   └── all_496_double_faults.json
└── figures/
    └── graphical_abstract.png          # High-resolution Graphical Abstract
```

---

## ⚙️ Installation & Prerequisites

The framework requires **Python 3.9+** and standard scientific computing libraries alongside [`pandapower`](https://www.pandapower.org/) for exact AC power flow solutions.

```bash
# Clone the repository
git clone https://github.com/mahmoudsajjadi/Smart-Grid-Resilience-MARL.git
cd Smart-Grid-Resilience-MARL

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

---

## 🚀 Reproduction & Quickstart Guide

All experiments can be executed standalone. Results are verified against exact AC power flows.

### 1. Feeder Restoration Benchmarks (Exp 1, Exp 2, & Exp 7)
```bash
# Single-fault restoration comparison (Centralized vs Decentralized)
python src/exp1_restoration.py

# Q-learning training and policy convergence
python src/exp2_qlearning.py

# Full N-2 double fault contingency evaluation across all 496 line pairs
python src/exp7_double_faults_496.py
```

### 2. Battery Storage (BESS) Islanding Coordination (Exp 3)
```bash
# Evaluates critical load served under forecast errors (0% to 50%)
python src/exp3_storage.py
```

### 3. Communication-Efficient Decentralized Training (Exp 4)
```bash
# Workload-balanced federated/decentralized learning across heterogeneous agents
python src/exp4_comdml.py
```

### 4. Computational Scalability Sweeps (Exp 5 & Exp 5b)
```bash
# 33-bus vs 179-bus Oberrhein network benchmark
python src/exp5_scalability.py

# Combinatorial tie-switch scalability sweep (T = 5 to 12 switches)
python src/exp5b_scaling_sweep.py
```

### 5. PV Hosting Capacity & Local Volt–VAr Droop (Exp 6)
```bash
# Evaluates voltage limits and hosting capacity under unity-PF vs Volt-VAr droop
python src/exp6_pv_hosting_capacity.py
```

### 6. Generate Figures & Graphical Abstract
```bash
# Generate architecture, topology, and result figures
python src/make_fig1_architecture.py
python src/make_fig2_topology.py
python src/make_result_figures.py
python src/make_fig9_restoration_sequence.py
python src/make_fig10_comdml_architecture.py
python src/make_graphical_abstract.py
```

---

## 📊 Summary of Benchmark Results

| Experiment | Metric / Scenario | Centralized Baseline | Proposed Multi-Agent System | Relative Improvement |
| :--- | :--- | :---: | :---: | :---: |
| **Exp 1: Single Faults** | Feasibility evaluations | 32 AC solves | 3 AC solves | **90.6% reduction** (exact match) |
| **Exp 1: Double Faults** | Feasibility evaluations | 32 AC solves | 7.8 AC solves | **75.6% reduction** (95.2% reward) |
| **Exp 3: Storage (BESS)** | Served critical load (T=4h) | 0.0% (uncoordinated) | 4.2% (coordinated) | **+4.2% critical hours served** |
| **Exp 4: ComDML** | Wall-clock training time | 146 s (unbalanced) | 100 s (balanced) | **1.46× speedup** |
| **Exp 5b: Scalability ($T=10$)** | Switching evaluations | 1,024 AC solves | 25 AC solves | **97.6% search space reduction** |
| **Exp 6: PV Hosting** | Maximum allowable PV capacity | 196% peak load | 296% peak load | **+51% hosting capacity** |

---

## 📜 Citation

If you use this codebase, models, or datasets in your research, please cite our paper:

```bibtex
@article{sajjadi2026sustainable,
  title     = {Sustainable Smart Grid Resilience and Renewable Integration Using Multi-Agent Reinforcement Learning},
  author    = {Sajjadi Mohammadabadi, Seyed Mahmoud and Sajjadi, Sayed Mohammad},
  journal   = {Sustainability},
  volume    = {18},
  number    = {20},
  pages     = {10574},
  year      = {2026},
  publisher = {MDPI},
  doi       = {10.3390/su182010574},
  url       = {https://www.mdpi.com/2071-1050/18/20/10574}
}
```

---

## 📬 Contact & Inquiries
- **Seyed Mahmoud Sajjadi Mohammadabadi** — University of Nevada, Reno — `mahmoud.sajjadi@unr.edu`
- **Sayed Mohammad Sajjadi**
