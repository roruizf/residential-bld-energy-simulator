
import numpy as np
# ---------------------
# Solar Gains
# ---------------------


# ---------------------
# Internal Gains
# ---------------------

def internal_gains(V_sec_i: float, t_m: list) -> list:
    """
    Internal gains (monthly)
    Inputs:
            - V_sec_i [m³]: House / appartment total volume (float)
            - t_m [Ms]: Month time length (numpy.ndarray (12,))
    Outputs:
            - Internal gains [MJ]: Monthly internal gains for heating, overheating and cooling (numpy.ndarray (12,))
    """
    t_m = np.array(t_m)
    V_EPR = V_sec_i  # m³

    if V_EPR <= 192:
        Q_int_sec_i_m = (1.41 * V_EPR + 78) * V_sec_i/V_EPR * t_m  # MJ
    else:
        Q_int_sec_i_m = (0.67 * V_EPR + 220) * V_sec_i/V_EPR * t_m  # MJ

    return Q_int_sec_i_m.tolist()


def internal_gains_heating(V_sec_i: float, t_m: list) -> list:
    Q_int_heat_sec_i_m = internal_gains(V_sec_i, t_m)
    return Q_int_heat_sec_i_m


def internal_gains_heating(V_sec_i: float, t_m: list) -> list:
    Q_int_overh_sec_i_m = internal_gains(V_sec_i, t_m)
    return Q_int_overh_sec_i_m


def internal_gains_cooling(V_sec_i: float, t_m: list) -> list:
    Q_int_cool_sec_i_m = internal_gains(V_sec_i, t_m)
    return Q_int_cool_sec_i_m

# ---------------------
# Transmission losses
# ---------------------


def transmission_losses(H_trans_sec_i, T_i_m, T_e_m, t_m):
    """
    Transmission losses (monthly)
    Inputs:
            - H_trans_sec_i [W/K]: Transmission heat transfer coefficient for heating/overheating/cooling (float)            
            - T_i_m [°C]: Monthly average indoor temperature (numpy.ndarray (12,))
            - T_e_m [°C]: Monthly average outdoor temperature (numpy.ndarray (12,))
            - t_m [Ms]: Month time length (numpy.ndarray (12,))
    Outputs:
            - Transmission losses [MJ]: Monthly transmission losses for heating, overheating and cooling (numpy.ndarray (12,))
    """
    Q_trans_sec_i_m = H_trans_sec_i * (T_i_m - T_e_m) * t_m  # MJ
    return Q_trans_sec_i_m


def transmission_losses_heating(H_trans_heat_sec_i, T_e_m, t_m):
    T_i_m = 18
    Q_trans_heat_sec_i_m = transmission_losses(
        H_trans_heat_sec_i, T_i_m, T_e_m, t_m)
    return Q_trans_heat_sec_i_m


def transmission_losses_overheating(H_trans_overh_sec_i, T_e_m, t_m):
    T_i_m = 23
    T_e_m = T_e_m + 1
    Q_trans_overh_sec_i_m = transmission_losses(
        H_trans_overh_sec_i, T_i_m, T_e_m, t_m)  # MJ
    return Q_trans_overh_sec_i_m


def transmission_losses_cooling(H_trans_cool_sec_i, T_e_m, t_m):
    T_i_m = 23
    T_e_m = T_e_m + 1
    Q_trans_cool_sec_i_m = transmission_losses(
        H_trans_cool_sec_i, T_i_m, T_e_m, t_m)  # MJ
    return Q_trans_cool_sec_i_m


# ---------------------
# Ventilation losses
# ---------------------

def ventilation_losses_heating(H_vent_heat_sec_i, T_e_m, t_m):
    """
    Ventilation losses (monthly)
    Inputs:
            - H_vent_heat_sec_i [W/K]: Ventilation heat transfer coefficient (float)
            - H_vent_overh_sec_i_m [W/K]: Monthly ventilation heat transfer coefficient (numpy.ndarray (12,))
            - H_vent_cool_sec_i_m [W/K]: Monthly ventilation heat transfer coefficient (numpy.ndarray (12,))
            - T_e_m [°C]: Monthly average outdoor temperature (numpy.ndarray (12,))
            - t_m [Ms]: Month time length (numpy.ndarray (12,))
    Outputs:
            - Ventilation losses [MJ]: Monthly ventilation losses for heating, cooling and overheating (numpy.ndarray (12,))
    """
    Q_vent_heat_sec_i_m = H_vent_heat_sec_i * (18 - T_e_m) * t_m  # MJ
    return Q_vent_heat_sec_i_m


def ventilation_losses_overheating(H_vent_overh_sec_i_m, T_e_m, t_m):
    Q_vent_overh_sec_i_m = H_vent_overh_sec_i_m * \
        (23 - (T_e_m + 1)) * t_m  # MJ
    return Q_vent_overh_sec_i_m


def ventilation_losses_cooling(H_vent_cool_sec_i_m, T_e_m, t_m):
    Q_vent_cool_sec_i_m = H_vent_cool_sec_i_m * (23 - (T_e_m + 1)) * t_m  # MJ
    return Q_vent_cool_sec_i_m

# if __name__ == "__main__":

#     t_m = (np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])*(24*3600)/1_000_000)#.tolist()
#     print(t_m)
#     print(type(t_m))
#     V_sec_i = 100
#     print(type(internal_gains(V_sec_i, t_m)))
#     print(internal_gains(V_sec_i, t_m))
#     print(type(np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])))
