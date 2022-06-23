import numpy as np


def net_dhw_demand(V_sec_i, t_m, N_bath=1, N_sink=1):
    """
    Domestic hot water needs for the energetic sector (monthly)
    DHW needs are calulated in function of the volume of the house.

    Only 2 points are considered:
        - Kitchen sinks (net_dhw_demand_sink)
        - Showers / bathroom (net_dhw_demand_bath)

    Inputs:
    ------
            - V_sec_i [m³]: House / appartment total volume (float)
            - t_m [Ms]: Month time length (numpy.ndarray (12,))
            - N_bath [-]: Number of showers/bathrooms (default = 1) (float)
            - N_sink [-]: Number of kitchen sinks (default = 1) (float)

    Outputs:
    -------
            - Net domestic hot water demand (Q_water_sec_i_net_m) [MJ]: Monthly net domestic hot water demand (numpy.ndarray (12,))
    """
    #  Domestic hot water need for each bath
    # --------------------------------------
    Q_water_bath_i_net_m = net_dhw_demand_bath(
        V_sec_i, t_m, N_bath)

    #  Domestic hot water need for each sink
    # --------------------------------------
    Q_water_sink_i_net_m = net_dhw_demand_sink(V_sec_i, t_m, N_sink)

    #  Domestic hot water need for the entire energetic sector
    # --------------------------------------------------------
    Q_water_sec_i_net_m = N_bath * Q_water_bath_i_net_m + N_sink * Q_water_sink_i_net_m
    return Q_water_sec_i_net_m


def net_dhw_demand_bath(V_sec_i, t_m, N_bath=1, r_water_bath_i_net=1):
    """
    Domestic hot water need for each bath in the energetic sector (monthly)

    Inputs:
    ------
        - V_sec_i [m³]: House / appartment total volume (float)
        - t_m [Ms]: Month time length (numpy.ndarray (12,))
        - N_bath [-]: Number of showers/bathrooms (default = 1) (float)
        - r_water_bath_i_net [-]: Reduction factor for pre-heating (default = 1) (float)

    Outputs:
    -------
        - Net domestic hot water demand for each bath (Q_water_bath_i_net_m) [MJ]: Monthly net domestic hot water demand (numpy.ndarray (12,))         
    """

    V_EPR = V_sec_i  # m³
    f_bath_i = 1 / N_bath
    Q_water_bath_i_net_m = r_water_bath_i_net * f_bath_i * \
        max(64, 64 + 0.220 * (V_EPR - 192)) * t_m  # MJ
    return Q_water_bath_i_net_m


def net_dhw_demand_sink(V_sec_i, t_m, N_sink=1, r_water_sink_i_net=1):
    """
    Domestic hot water need for each sink in the energetic sector (monthly)

    Inputs:
    ------
        - V_sec_i [m³]: House / appartment total volume (float)
        - t_m [Ms]: Month time length (numpy.ndarray (12,))
        - N_sink [-]: Number of kitchen sinks (default = 1) (float)
        - r_water_sink_i_net [-]: Reduction factor for pre-heating (default = 1) (float)

    Outputs:
    -------
        - Net domestic hot water demand for each bath (Q_water_bath_i_net_m) [MJ]: Monthly net domestic hot water demand (numpy.ndarray (12,))
    """
    V_EPR = V_sec_i  # m³
    f_sink_i = 1 / N_sink
    Q_water_sink_i_net_m = r_water_sink_i_net * f_sink_i * \
        max(16, 16 + 0.055 * (V_EPR - 192)) * t_m
    return Q_water_sink_i_net_m
