import numpy as np


def net_cooling_demand(C_sec_i, H_trans_cool_sec_i, H_vent_cool_sec_i_m, Q_solar_cool_sec_i_m, Q_int_cool_sec_i_m, Q_trans_cool_sec_i_m, Q_vent_cool_sec_i_m, p_cool_sec_i):
    """
    Net cooling demand [MJ]: Monthly net cooling demand (numpy.ndarray (12,))

    Inputs:
    ------
        - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
        - H_trans_cool_sec_i [W/K]: Transmission heat transfer coefficient (float)
        - H_vent_cool_sec_i_m [W/K]: Monthly ventilation heat transfer coefficient (numpy.ndarray (12,))
        - Q_solar_cool_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
        - Q_int_cool_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
        - Q_trans_cool_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
        - Q_vent_cool_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))
        - p_cool_sec_i [-]: Probability of active cooling (float)

    Outputs:
    -------
        - Net cooling demand [MJ]: Monthly net cooling demand (numpy.ndarray (12,))
    """

    # Total gains and losses (energetic sector)
    # ------------------------------------------
    Q_loss_cool_sec_i_m = Q_trans_cool_sec_i_m + Q_vent_cool_sec_i_m  # MJ
    Q_gain_cool_sec_i_m = Q_int_cool_sec_i_m + Q_solar_cool_sec_i_m  # MJ

    # Heat balance ratio
    # ------------------
    lambda_cool_sec_i_m = heat_balance_ratio_cooling(
        Q_solar_cool_sec_i_m, Q_int_cool_sec_i_m, Q_trans_cool_sec_i_m, Q_vent_cool_sec_i_m)

    # Utilization factor
    # -------------------
    eta_util_cool_sec_i_m = utilization_factor_cooling(
        C_sec_i, H_trans_cool_sec_i, H_vent_cool_sec_i_m, lambda_cool_sec_i_m)

    # Net space cooling demand, MJ
    # ------------------------------
    Q_cool_net_princ_sec_i_m = Q_gain_cool_sec_i_m - \
        eta_util_cool_sec_i_m * Q_loss_cool_sec_i_m

    # Allowance factor
    # ------------------
    f_allow_cool_sec_i_m = allowance_factor_cooling(lambda_cool_sec_i_m)

    # Applying allowance factor to cooling needs
    # ------------------------------------------
    Q_cool_net_princ_sec_i_m = Q_cool_net_princ_sec_i_m * f_allow_cool_sec_i_m

    f_cool_geo_sec_i_m = 0
    Q_cool_net_sec_i_m = p_cool_sec_i * \
        (1 - f_cool_geo_sec_i_m) * Q_cool_net_princ_sec_i_m
    return Q_cool_net_sec_i_m


def utilization_factor_cooling(C_sec_i, H_trans_cool_sec_i, H_vent_cool_sec_i_m, lambda_cool_sec_i_m):
    """
    Utilization factor [-]: fraction of heat gains to be discounted from net cooling demand [0, 1]

    Inputs:
    ------
        - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
        - H_trans_cool_sec_i [W/K]: Transmission heat transfer coefficient (float)
        - H_vent_cool_sec_i_m [W/K]: Monthly ventilation heat transfer coefficient (numpy.ndarray (12,))
        - lambda_cool_sec_i_m [-]: Monthly heat balance ratio (numpy.ndarray (12,))

    Outputs:
    -------
        - Utilization factor (eta_util_cool_sec_i_m) [-]: Monthly utilization factor (numpy.ndarray (12,))
    """

    tau_cool_sec_i_m = C_sec_i / \
        (H_trans_cool_sec_i +
         H_vent_cool_sec_i_m)  # s Time constant of the building zone
    # [-] Dimensionless numerical parameter
    a_sec_i_m = 1 + tau_cool_sec_i_m / 54_000

    eta_util_cool_sec_i_m = np.array([])

    for a, gamma in zip(a_sec_i_m.flatten(), lambda_cool_sec_i_m.flatten()):

        if gamma == 1:
            eta_util_cool_sec_i_m_j = a/(a+1)
        else:
            eta_util_cool_sec_i_m_j = (
                1-gamma**a)/(1-gamma**(a+1))

        eta_util_cool_sec_i_m = np.append(
            eta_util_cool_sec_i_m, eta_util_cool_sec_i_m_j)

    return eta_util_cool_sec_i_m


def heat_balance_ratio_cooling(Q_solar_cool_sec_i_m, Q_int_cool_sec_i_m, Q_trans_cool_sec_i_m, Q_vent_cool_sec_i_m):
    """
    Heat balance ratio: Ratio between gains and losses 

    Inputs:
    ------
        - Q_solar_cool_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
        - Q_int_cool_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
        - Q_trans_cool_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
        - Q_vent_cool_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))

    Outputs:
    -------
        - Heat balance ratio (lambda_cool_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))
    """
    # Gain and losses
    # ---------------
    Q_loss_cool_sec_i_m = Q_trans_cool_sec_i_m + Q_vent_cool_sec_i_m  # MJ
    Q_gain_cool_sec_i_m = Q_int_cool_sec_i_m + Q_solar_cool_sec_i_m  # MJ

    # Heat balance ratio (lambda_cool_sec_i_m)
    # ----------------------------------------
    lambda_cool_sec_i_m = Q_loss_cool_sec_i_m / \
        Q_gain_cool_sec_i_m  # [-], monthly loss-gain rate
    return lambda_cool_sec_i_m


def allowance_factor_cooling(lambda_cool_sec_i_m):
    """
    Cooling allowance factor {0, 1} -> if lambda_cool_sec_i_m < 2.5 then 1 otherwise 0

    Inputs:
    ------
        - Heat balance ratio (lambda_cool_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))

    Outputs:
    -------
        - Cooling allowance factor (f_allow_cool_sec_i_m) [-]: Monthly cooling allowance factor to be included when calculating net cooling demand (numpy.ndarray (12,))
    """
    f_allow_cool_sec_i_m = np.array([])

    for item in lambda_cool_sec_i_m.flatten():
        if item < 2.5:
            f_allow_cool_sec_i_m_j = 1
        else:
            f_allow_cool_sec_i_m_j = 0

        f_allow_cool_sec_i_m = np.append(
            f_allow_cool_sec_i_m, f_allow_cool_sec_i_m_j)
    f_allow_cool_sec_i_m = f_allow_cool_sec_i_m.flatten()

    return f_allow_cool_sec_i_m
