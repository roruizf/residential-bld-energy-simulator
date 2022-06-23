import numpy as np


def yearly_overheating_degree(C_sec_i, H_trans_overh_sec_i, H_vent_overh_sec_i_m, Q_solar_overh_sec_i_m, Q_int_overh_sec_i_m, Q_trans_overh_sec_i_m, Q_vent_overh_sec_i_m):
    """
    Overheating risk (yearly)

    Inputs:
    ------
            - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
            - H_trans_overh_sec_i [W/K]: Transmission heat transfer coefficient (float)
            - H_vent_overh_sec_i_m [W/K]: Monthly ventilation heat transfer coefficient (numpy.ndarray (12,))
            - Q_solar_overh_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
            - Q_int_overh_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
            - Q_trans_overh_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
            - Q_vent_overh_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))

    Outputs:
    -------
            - Yearly overheating degree (I_overh_sec_i) [Kh]: Yearly overheating degree (float)
            - Active cooling probability (p_cool_sec_i)
            - Time fraction over 25°C (f_cool_sec_i)
    """
    # Total gains and losses (energetic sector)
    # ------------------------------------------
    # Q_loss_overh_sec_i_m = Q_trans_overh_sec_i_m + Q_vent_overh_sec_i_m  # MJ
    # Q_gain_overh_sec_i_m = Q_int_overh_sec_i_m + Q_solar_overh_sec_i_m  # MJ

    # Heat balance ratio
    # ------------------
    gamma_overh_sec_i_m = heat_balance_ratio_overheating(
        Q_solar_overh_sec_i_m, Q_int_overh_sec_i_m, Q_trans_overh_sec_i_m, Q_vent_overh_sec_i_m)

    # Utilization factor
    # -------------------
    eta_util_overh_sec_i_m = utilization_factor_overheating(
        C_sec_i, H_trans_overh_sec_i, H_vent_overh_sec_i_m, gamma_overh_sec_i_m)

    # Overheating risk (yearly)
    # -------------------------
    f_cool_geo_sec_i_m = 0
    Q_gain_overh_sec_i_m = Q_int_overh_sec_i_m + Q_solar_overh_sec_i_m  # MJ
    Q_excess_norm_sec_i_m = ((1 - eta_util_overh_sec_i_m) * (1 - f_cool_geo_sec_i_m) *
                             Q_gain_overh_sec_i_m) / (H_trans_overh_sec_i + H_vent_overh_sec_i_m) * 1_000 / 3.6  # Kh
    I_overh_sec_i = np.sum(Q_excess_norm_sec_i_m)  # Kh

    # Active cooling probability
    # --------------------------
    p_cool_sec_i = active_cooling_probability(I_overh_sec_i)

    # Time fraction over 25°C
    # -----------------------
    f_cool_sec_i = time_fraction_over_25C(I_overh_sec_i)
    return I_overh_sec_i, p_cool_sec_i, f_cool_sec_i


def heat_balance_ratio_overheating(Q_solar_overh_sec_i_m, Q_int_overh_sec_i_m, Q_trans_overh_sec_i_m, Q_vent_overh_sec_i_m):
    """
    Heat balance ratio: Ratio between gains and losses
    Inputs:
        - Q_solar_overh_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
        - Q_int_overh_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
        - Q_trans_overh_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
        - Q_vent_overh_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))

    Outputs:
        - Heat balance ratio (gamma_overh_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))
    """
    # Gain and losses
    Q_loss_overh_sec_i_m = Q_trans_overh_sec_i_m + Q_vent_overh_sec_i_m  # MJ
    Q_gain_overh_sec_i_m = Q_int_overh_sec_i_m + Q_solar_overh_sec_i_m  # MJ

    # Heat balance ratio (gamma_heat_sec_i_m)
    gamma_overh_sec_i_m = Q_gain_overh_sec_i_m / \
        Q_loss_overh_sec_i_m  # [-], monthly gain-loss rate
    return gamma_overh_sec_i_m


def utilization_factor_overheating(C_sec_i, H_trans_overh_sec_i, H_vent_overh_sec_i_m, gamma_overh_sec_i_m):
    """
    Utilization factor [-]: fraction of heat gains to be applied to evaluate the overheating risk [0, 1]
    Inputs:
        - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
        - H_trans_overh_sec_i [W/K]: Transmission heat transfer coefficient (float)
        - H_vent_overh_sec_i [W/K]: Monthly ventilation heat transfer coefficient (numpy.ndarray (12,))
        - gamma_overh_sec_i_m [-]: Monthly heat balance ratio (numpy.ndarray (12,))

    Outputs:
        - Utilization factor (eta_util_overh_sec_i_m) [-]: Monthly utilization factor (numpy.ndarray (12,))
    """

    tau_overh_sec_i_m = C_sec_i / \
        (H_trans_overh_sec_i +
         H_vent_overh_sec_i_m)  # s Time constant of the building zone
    # [-] Dimensionless numerical parameter
    a_sec_i_m = 1 + tau_overh_sec_i_m / 54_000

    eta_util_overh_sec_i_m = np.array([])

    for a, gamma in zip(a_sec_i_m.flatten(), gamma_overh_sec_i_m.flatten()):

        if gamma == 1:
            eta_util_overh_sec_i_m_j = a/(a+1)
        else:
            eta_util_overh_sec_i_m_j = (
                1-gamma**a)/(1-gamma**(a+1))

        eta_util_overh_sec_i_m = np.append(
            eta_util_overh_sec_i_m, eta_util_overh_sec_i_m_j)

    return eta_util_overh_sec_i_m


def active_cooling_probability(I_overh_sec_i):
    I_overh_thresh = 1_000  # Kh
    I_overh_max = 6_500  # Kh
    p_cool_sec_i = max(
        0, min((I_overh_sec_i - I_overh_thresh)/(I_overh_max - I_overh_thresh), 1))  # [-]
    return p_cool_sec_i


def time_fraction_over_25C(I_overh_sec_i):
    I_overh_max = 6_500  # Kh
    f_cool_sec_i = max(0, min(0.05 * I_overh_sec_i/I_overh_max, 1))  # [-]
    return f_cool_sec_i
