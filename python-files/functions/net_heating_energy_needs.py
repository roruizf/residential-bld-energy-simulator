import numpy as np


# ---------------------
# Net Heating Needs
# ---------------------
def net_heating_demand(C_sec_i, H_trans_heat_sec_i, H_vent_heat_sec_i, Q_solar_heat_sec_i_m, Q_int_heat_sec_i_m, Q_trans_heat_sec_i_m, Q_vent_heat_sec_i_m):
    """
    Net heating demand [MJ]: Monthly net heating demand (numpy.ndarray (12,))

    Inputs:
    ------
        - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
        - H_trans_heat_sec_i [W/K]: Transmission heat transfer coefficient (float)
        - H_vent_heat_sec_i [W/K]: Ventilation heat transfer coefficient (float)
        - Q_solar_heat_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
        - Q_int_heat_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
        - Q_trans_heat_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
        - Q_vent_heat_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))       

    Outputs:
    -------
        - Net heating demand [MJ]: Monthly net heating demand (numpy.ndarray (12,))
    """

    # Total gains and losses (energetic sector)
    # ------------------------------------------
    Q_loss_heat_sec_i_m = Q_trans_heat_sec_i_m + Q_vent_heat_sec_i_m  # MJ
    Q_gain_heat_sec_i_m = Q_int_heat_sec_i_m + Q_solar_heat_sec_i_m  # MJ

    # Heat balance ratio
    # ------------------
    gamma_heat_sec_i_m = heat_balance_ratio_heating(
        Q_solar_heat_sec_i_m, Q_int_heat_sec_i_m, Q_trans_heat_sec_i_m, Q_vent_heat_sec_i_m)

    # Utilization factor
    # -------------------
    eta_util_heat_sec_i_m = utilization_factor_heating(
        C_sec_i, H_trans_heat_sec_i, H_vent_heat_sec_i, gamma_heat_sec_i_m)

    # Net space heating demand, MJ
    # ------------------------------
    Q_heat_net_sec_i_m = Q_loss_heat_sec_i_m - \
        eta_util_heat_sec_i_m * Q_gain_heat_sec_i_m

    # Allowance factor
    # ------------------
    f_allow_heat_sec_i_m = allowance_factor_heating(gamma_heat_sec_i_m)

    # Applying allowance factor to heating needs
    # -------------------------------------------
    Q_heat_net_sec_i_m = Q_heat_net_sec_i_m * f_allow_heat_sec_i_m

    return Q_heat_net_sec_i_m


def utilization_factor_heating(C_sec_i, H_trans_heat_sec_i, H_vent_heat_sec_i, gamma_heat_sec_i_m):
    """
    Utilization factor [-]: fraction of heat gains to be discounted from net heating demand [0, 1]

    Inputs:
    ------
        - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
        - H_trans_heat_sec_i [W/K]: Transmission heat transfer coefficient (float)
        - H_vent_heat_sec_i [W/K]: Ventilation heat transfer coefficient (float)
        - gamma_heat_sec_i_m [-]: Monthly heat balance ratio (numpy.ndarray (12,))

    Outputs:
    -------
        - Utilization factor (eta_util_heat_sec_i_m) [-]: Monthly utilization factor (numpy.ndarray (12,))
    """

    tau_heat_sec_i = C_sec_i / \
        (H_trans_heat_sec_i + H_vent_heat_sec_i)  # s Time constant of the building zone
    # [-] Dimensionless numerical parameter
    a = 1 + tau_heat_sec_i / 54_000

    eta_util_heat_sec_i_m = np.array([])

    for item in gamma_heat_sec_i_m.flatten():

        if item == 1:
            eta_util_heat_sec_i_m_j = a/(a+1)
        else:
            eta_util_heat_sec_i_m_j = (
                1-item**a)/(1-item**(a+1))

        eta_util_heat_sec_i_m = np.append(
            eta_util_heat_sec_i_m, eta_util_heat_sec_i_m_j)

    return eta_util_heat_sec_i_m


def heat_balance_ratio_heating(Q_solar_heat_sec_i_m, Q_int_heat_sec_i_m, Q_trans_heat_sec_i_m, Q_vent_heat_sec_i_m):
    """
    Heat balance ratio: Ratio between gains and losses 

    Inputs:
    ------
        - Q_solar_heat_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
        - Q_int_heat_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
        - Q_trans_heat_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
        - Q_vent_heat_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))

    Outputs:
    -------
        - Heat balance ratio (gamma_heat_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))
    """
    # Gain and losses
    Q_loss_heat_sec_i_m = Q_trans_heat_sec_i_m + Q_vent_heat_sec_i_m  # MJ
    Q_gain_heat_sec_i_m = Q_int_heat_sec_i_m + Q_solar_heat_sec_i_m  # MJ

    # Heat balance ratio (gamma_heat_sec_i_m)
    gamma_heat_sec_i_m = Q_gain_heat_sec_i_m / \
        Q_loss_heat_sec_i_m  # [-], monthly gain-loss rate
    return gamma_heat_sec_i_m


def allowance_factor_heating(gamma_heat_sec_i_m):
    """
    Heating allowance factor {0, 1} -> if gamma_heat_sec_i_m < 2.5 then 1 otherwise 0

    Inputs:
    ------
        - Heat balance ratio (gamma_heat_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))

    Outputs:
    -------
        - Heating allowance factor (f_allow_heat_sec_i_m) [-]: Monthly heating allowance factor to be included when calculating net heating demand (numpy.ndarray (12,))
    """
    f_allow_heat_sec_i_m = np.array([])

    for item in gamma_heat_sec_i_m.flatten():
        if item < 2.5:
            f_allow_heat_sec_i_m_j = 1
        else:
            f_allow_heat_sec_i_m_j = 0

        f_allow_heat_sec_i_m = np.append(
            f_allow_heat_sec_i_m, f_allow_heat_sec_i_m_j)
    f_allow_heat_sec_i_m = f_allow_heat_sec_i_m.flatten()

    return f_allow_heat_sec_i_m
