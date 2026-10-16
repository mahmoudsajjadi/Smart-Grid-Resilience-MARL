import numpy as np
import pandapower as pp
import pandapower.networks as pn
import copy

# Zone of bus mapping
ZONE_OF_BUS = {
    0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1, 8: 2, 9: 2, 10: 2,
    11: 2, 12: 2, 13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 1, 19: 1,
    20: 1, 21: 1, 22: 3, 23: 3, 24: 3, 25: 4, 26: 4, 27: 4, 28: 4,
    29: 4, 30: 4, 31: 4, 32: 4,
}

# The far bus of each zone (zones 0 to 4)
# Zone 0: buses 0-6 -> bus 6
# Zone 1: buses 7, 18-21 -> bus 21
# Zone 2: buses 8-17 -> bus 17
# Zone 3: buses 22-24 -> bus 24
# Zone 4: buses 25-32 -> bus 32
ZONE_FAR_BUS = {
    0: 6,
    1: 21,
    2: 17,
    3: 24,
    4: 32
}

base_net = pn.case33bw()
total_p = base_net.load.p_mw.sum()
zone_loads = {z: 0.0 for z in range(5)}
for _, row in base_net.load.iterrows():
    b = int(row.bus)
    zone_loads[ZONE_OF_BUS[b]] += row.p_mw

rho = {z: zone_loads[z] / total_p for z in range(5)}
print(f"Total Load: {total_p:.3f} MW")
print("Zone load shares (rho):", {z: round(r, 4) for z, r in rho.items()})

def test_hosting(control_mode='unity', p_total=7.0):
    net = pn.case33bw()
    # Add PV generators at the far bus of each zone
    for z in range(5):
        bus = ZONE_FAR_BUS[z]
        p_pv = rho[z] * p_total
        pp.create_sgen(net, bus=bus, p_mw=p_pv, q_mvar=0.0, name=f"PV_zone_{z}")
    
    if control_mode == 'unity':
        try:
            pp.runpp(net, enforce_q_lims=True)
            if not net.converged: return False, net.res_bus.vm_pu.max(), 0.0
            vmax = net.res_bus.vm_pu.max()
            vmin = net.res_bus.vm_pu.min()
            feasible = (vmin >= 0.90) and (vmax <= 1.10)
            return feasible, vmax, 0.0
        except Exception:
            return False, 999.0, 0.0

    elif control_mode == 'volt_var':
        # Droop control: iterate until convergence
        # Q = -clip(k_droop * max(0, V - 1.0), 0, eta_q * P)
        k_droop = 20.0
        eta_q = 0.30
        for it in range(30):
            try:
                pp.runpp(net, enforce_q_lims=True)
                if not net.converged: return False, 999.0, 0.0
            except Exception:
                return False, 999.0, 0.0
            
            # update Q
            max_dq = 0.0
            for idx, row in net.sgen.iterrows():
                b = int(row.bus)
                v = net.res_bus.at[b, 'vm_pu']
                p_gen = row.p_mw
                q_target = -np.clip(k_droop * max(0.0, v - 1.05), 0.0, eta_q * p_gen) # or v-1.0
                dq = abs(net.sgen.at[idx, 'q_mvar'] - q_target)
                max_dq = max(max_dq, dq)
                net.sgen.at[idx, 'q_mvar'] = q_target
            
            if max_dq < 1e-4:
                break
        
        vmax = net.res_bus.vm_pu.max()
        vmin = net.res_bus.vm_pu.min()
        feasible = (vmin >= 0.90) and (vmax <= 1.10)
        return feasible, vmax, net.sgen.q_mvar.sum()

    elif control_mode == 'volt_watt':
        # IEEE 1547-2018 Volt-Watt mode:
        # If V > 1.05, curtail active power linearly up to V = 1.10 down to P_min (e.g. 20% or 0%)
        # Here: P = P_rated * (1 - (V - 1.05)/(1.10 - 1.05)) for V in [1.05, 1.10]
        # Iterate until convergence
        p_rated = net.sgen.p_mw.values.copy()
        for it in range(30):
            try:
                pp.runpp(net, enforce_q_lims=True)
                if not net.converged: return False, 999.0, 0.0
            except Exception:
                return False, 999.0, 0.0
            
            max_dp = 0.0
            for idx, row in net.sgen.iterrows():
                b = int(row.bus)
                v = net.res_bus.at[b, 'vm_pu']
                p_r = p_rated[idx]
                if v <= 1.05:
                    p_target = p_r
                elif v >= 1.10:
                    p_target = 0.20 * p_r
                else:
                    p_target = p_r * (1.0 - 0.80 * (v - 1.05) / 0.05)
                
                dp = abs(net.sgen.at[idx, 'p_mw'] - p_target)
                max_dp = max(max_dp, dp)
                net.sgen.at[idx, 'p_mw'] = p_target
            
            if max_dp < 1e-4:
                break
        vmax = net.res_bus.vm_pu.max()
        vmin = net.res_bus.vm_pu.min()
        feasible = (vmin >= 0.90) and (vmax <= 1.10)
        return feasible, vmax, net.sgen.p_mw.sum()

# Binary search / grid search for hosting capacity under each
for mode in ['unity', 'volt_var']:
    # Let's find max P
    p_low, p_high = 1.0, 25.0
    for _ in range(30):
        p_mid = (p_low + p_high) / 2.0
        feas, vm, _ = test_hosting(mode, p_mid)
        if feas:
            p_low = p_mid
        else:
            p_high = p_mid
    print(f"Mode {mode}: Max PV = {p_low:.2f} MW ({p_low / total_p * 100:.1f}% peak load)")
