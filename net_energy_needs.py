import numpy as np


class NetHeatingNeeds:
    """
    Net heating needs (monthly)
    Inputs:
            - Q_solar_heat_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
            - Q_int_heat_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
            - Q_trans_heat_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
            - Q_vent_heat_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))
            - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
            - H_trans_heat_sec_i [W/K]: Transmission heat transfer coefficient (float)
            - H_vent_heat_sec_i [W/K]: Ventilation heat transfer coefficient (float)
    Outputs:
            - Heat balance ratio (gamma_heat_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))
            - Heating allowance factor (f_allow_heat_sec_i_m) [-]: Monthly heating allowance factor (numpy.ndarray (12,))
            - Utilization factor (eta_util_heat_sec_i_m) [-]: Monthly utilization factor (numpy.ndarray (12,))
            - Net heating demand [MJ]: Monthly net heating demand (numpy.ndarray (12,))
    """

    def __init__(self, Q_solar_heat_sec_i_m, Q_int_heat_sec_i_m, Q_trans_heat_sec_i_m, Q_vent_heat_sec_i_m, C_sec_i, H_trans_heat_sec_i, H_vent_heat_sec_i):
        # Inputs
        self.Q_solar_heat_sec_i_m = Q_solar_heat_sec_i_m
        self.Q_int_heat_sec_i_m = Q_int_heat_sec_i_m
        self.Q_trans_heat_sec_i_m = Q_trans_heat_sec_i_m
        self.Q_vent_heat_sec_i_m = Q_vent_heat_sec_i_m
        # Calculations
        self.gamma_heat_sec_i_m = self.heat_balance_ratio(
            Q_solar_heat_sec_i_m, Q_int_heat_sec_i_m, Q_trans_heat_sec_i_m, Q_vent_heat_sec_i_m)
        self.f_allow_heat_sec_i_m = self.heating_allowance_factor(
            self.gamma_heat_sec_i_m)
        self.eta_util_heat_sec_i_m = self.utilization_factor_heating(
            C_sec_i, H_trans_heat_sec_i, H_vent_heat_sec_i, self.gamma_heat_sec_i_m)
        self.Q_heat_net_sec_i_m = self.net_heating_demand(
            Q_solar_heat_sec_i_m, Q_int_heat_sec_i_m, Q_trans_heat_sec_i_m, Q_vent_heat_sec_i_m, self.eta_util_heat_sec_i_m, self.f_allow_heat_sec_i_m)

    def heat_balance_ratio(self, Q_solar_heat_sec_i_m, Q_int_heat_sec_i_m, Q_trans_heat_sec_i_m, Q_vent_heat_sec_i_m):
        """
        Heat balance ratio: Ratio between gains and losses 
        Inputs:
            - Q_solar_heat_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
            - Q_int_heat_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
            - Q_trans_heat_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
            - Q_vent_heat_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))

        Outputs:
            - Heat balance ratio (gamma_heat_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))
        """
        # Gain and losses
        Q_loss_heat_sec_i_m = Q_trans_heat_sec_i_m + Q_vent_heat_sec_i_m  # MJ
        Q_gain_heat_sec_i_m = Q_int_heat_sec_i_m + Q_solar_heat_sec_i_m  # MJ

        # Heat balance ratio (gamma_heat_sec_i_m)
        gamma_heat_sec_i_m = Q_gain_heat_sec_i_m / \
            Q_loss_heat_sec_i_m  # [-], monthly gain-loss rate
        return gamma_heat_sec_i_m

    def heating_allowance_factor(self, gamma_heat_sec_i_m):
        """
        Heating allowance factor {0, 1} -> if gamma_heat_sec_i_m < 2.5 then 1 otherwise 0
        Inputs:
            - Heat balance ratio (gamma_heat_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))

        Outputs:
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

    def utilization_factor_heating(self, C_sec_i, H_trans_heat_sec_i, H_vent_heat_sec_i, gamma_heat_sec_i_m):
        """
        Utilization factor [-]: fraction of heat gains to be discounted from net heating demand [0, 1]
        Inputs:
            - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
            - H_trans_heat_sec_i [W/K]: Transmission heat transfer coefficient (float)
            - H_vent_heat_sec_i [W/K]: Ventilation heat transfer coefficient (float)
            - gamma_heat_sec_i_m [-]: Monthly heat balance ratio (numpy.ndarray (12,))

        Outputs:
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

    def net_heating_demand(self, Q_solar_heat_sec_i_m, Q_int_heat_sec_i_m, Q_trans_heat_sec_i_m, Q_vent_heat_sec_i_m, eta_util_heat_sec_i_m, f_allow_heat_sec_i_m):
        """
        Net heating demand [MJ]: Monthly net heating demand (numpy.ndarray (12,))
        Inputs:
            - Q_solar_heat_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
            - Q_int_heat_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
            - Q_trans_heat_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
            - Q_vent_heat_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))
            - Utilization factor (eta_util_heat_sec_i_m) [-]: Monthly utilization factor (numpy.ndarray (12,))
            - Heating allowance factor (f_allow_heat_sec_i_m) [-]: Monthly heating allowance factor to be included when calculating net heating demand (numpy.ndarray (12,))

        Outputs:
            - Net heating demand [MJ]: Monthly net heating demand (numpy.ndarray (12,))
        """

        Q_loss_heat_sec_i_m = Q_trans_heat_sec_i_m + Q_vent_heat_sec_i_m  # MJ
        Q_gain_heat_sec_i_m = Q_int_heat_sec_i_m + Q_solar_heat_sec_i_m  # MJ

        # MJ, Net space heating demand
        Q_heat_net_sec_i_m = Q_loss_heat_sec_i_m - \
            eta_util_heat_sec_i_m*Q_gain_heat_sec_i_m

        # Applying allowance factor to heating needs
        Q_heat_net_sec_i_m = Q_heat_net_sec_i_m * f_allow_heat_sec_i_m

        return Q_heat_net_sec_i_m


class NetDHWNeeds:
    """
    Domestic hot water needs (monthly)
    Domestic hot water needs are calulatedin function of the volume of the house.
    Only 2 points are considered:
        - Kitchen sinks (net_dhw_demand_sink)
        - Showers / bathroom (net_dhw_demand_bath)

    Inputs:
            - V_sec_i [m³]: House / appartment total volume (float)
            - N_bath [-]: Number of showers/bathrooms (default = 1) (float)
            - N_sink [-]: Number of kitchen sinks (default = 1) (float)
            - t_m [Ms]: Month time length (numpy.ndarray (12,))

    Outputs:
            - Net domestic hot water demand (Q_water_sec_i_net_m) [MJ]: Monthly net domestic hot water demand (numpy.ndarray (12,))         
    """

    def __init__(self, V_sec_i, t_m):
        N_bath = 1  # Number of showers/bathrooms (default = 1) (float)
        N_sink = 1  # Number of kitchen sinks (default = 1) (float)
        r_water_bath_i_net = 1  # Reduction factor (default = 1) (float)
        r_water_sink_i_net = 1  # Reduction factor (default = 1) (float)
        Q_water_bath_i_net_m = self.net_dhw_demand_bath(
            V_sec_i, r_water_bath_i_net, N_bath, t_m)
        Q_water_sink_i_net_m = self.net_dhw_demand_sink(
            V_sec_i, r_water_sink_i_net, N_sink, t_m)
        self.Q_water_sec_i_net_m = self.net_dhw_demand(
            N_bath, Q_water_bath_i_net_m, N_sink, Q_water_sink_i_net_m)

    def net_dhw_demand_bath(self, V_sec_i, r_water_bath_i_net, N_bath, t_m):

        V_EPR = V_sec_i  # m³
        f_bath_i = 1 / N_bath
        Q_water_bath_i_net_m = r_water_bath_i_net * f_bath_i * \
            max(64, 64 + 0.220 * (V_EPR - 192)) * t_m  # MJ
        return Q_water_bath_i_net_m

    def net_dhw_demand_sink(self, V_sec_i, r_water_sink_i_net, N_sink, t_m):
        V_EPR = V_sec_i  # m³
        f_sink_i = 1 / N_sink
        Q_water_sink_i_net_m = r_water_sink_i_net * f_sink_i * \
            max(16, 16 + 0.055 * (V_EPR - 192)) * t_m
        return Q_water_sink_i_net_m

    def net_dhw_demand(self, N_bath, Q_water_bath_i_net_m, N_sink, Q_water_sink_i_net_m):
        Q_water_sec_i_net_m = N_bath * Q_water_bath_i_net_m + N_sink * Q_water_sink_i_net_m
        return Q_water_sec_i_net_m


class OverHeatingRisk:
    """
    Overheating risk (yearly)
    Inputs:
            - Q_solar_overh_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
            - Q_int_overh_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
            - Q_trans_overh_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
            - Q_vent_overh_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))
            - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
            - H_trans_overh_sec_i [W/K]: Transmission heat transfer coefficient (float)
            - H_vent_overh_sec_i_m [W/K]: Monthly ventilation heat transfer coefficient (numpy.ndarray (12,))
    Outputs:
            - Heat balance ratio (gamma_overh_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))            
            - Utilization factor (eta_util_overh_sec_i_m) [-]: Monthly utilization factor (numpy.ndarray (12,))
            - Yearly overheating degree (I_overh_sec_i) [Kh]: Yearly overheating degree (float)
    """

    def __init__(self, Q_solar_overh_sec_i_m, Q_int_overh_sec_i_m, Q_trans_overh_sec_i_m, Q_vent_overh_sec_i_m, C_sec_i, H_trans_overh_sec_i, H_vent_overh_sec_i_m):
        self.gamma_overh_sec_i_m = self.heat_balance_ratio(
            Q_solar_overh_sec_i_m, Q_int_overh_sec_i_m, Q_trans_overh_sec_i_m, Q_vent_overh_sec_i_m)
        self.eta_util_overh_sec_i_m = self.utilization_factor_overheating(
            C_sec_i, H_trans_overh_sec_i, H_vent_overh_sec_i_m, self.gamma_overh_sec_i_m)
        self.I_overh_sec_i = self.yearly_overheating_degree(
            Q_int_overh_sec_i_m, Q_solar_overh_sec_i_m, self.eta_util_overh_sec_i_m, H_trans_overh_sec_i, H_vent_overh_sec_i_m)
        self.p_cool_sec_i = self.active_cooling_probability(self.I_overh_sec_i)
        self.f_cool_sec_i = self.time_fraction_over_25C(self.I_overh_sec_i)

    def heat_balance_ratio(self, Q_solar_overh_sec_i_m, Q_int_overh_sec_i_m, Q_trans_overh_sec_i_m, Q_vent_overh_sec_i_m):
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

    def utilization_factor_overheating(self, C_sec_i, H_trans_overh_sec_i, H_vent_overh_sec_i_m, gamma_overh_sec_i_m):
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

    def yearly_overheating_degree(self, Q_int_overh_sec_i_m, Q_solar_overh_sec_i_m, eta_util_overh_sec_i_m, H_trans_overh_sec_i, H_vent_overh_sec_i_m):
        f_cool_geo_sec_i_m = 0
        Q_gain_overh_sec_i_m = Q_int_overh_sec_i_m + Q_solar_overh_sec_i_m  # MJ
        Q_excess_norm_sec_i_m = ((1 - eta_util_overh_sec_i_m) * (1 - f_cool_geo_sec_i_m) *
                                 Q_gain_overh_sec_i_m) / (H_trans_overh_sec_i + H_vent_overh_sec_i_m) * 1_000 / 3.6  # Kh
        I_overh_sec_i = np.sum(Q_excess_norm_sec_i_m)  # Kh
        return I_overh_sec_i

    def active_cooling_probability(self, I_overh_sec_i):
        I_overh_thresh = 1_000  # Kh
        I_overh_max = 6_500  # Kh
        p_cool_sec_i = max(
            0, min((I_overh_sec_i - I_overh_thresh)/(I_overh_max - I_overh_thresh), 1))  # [-]
        return p_cool_sec_i

    def time_fraction_over_25C(self, I_overh_sec_i):
        I_overh_max = 6_500  # Kh
        f_cool_sec_i = max(0, min(0.05 * I_overh_sec_i/I_overh_max, 1))  # [-]
        return f_cool_sec_i


class NetCoolingNeeds:
    """
    Net cooling needs (monthly)
    Inputs:
            - Q_solar_cool_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
            - Q_int_cool_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
            - Q_trans_cool_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
            - Q_vent_cool_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))
            - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
            - H_trans_cool_sec_i [W/K]: Transmission heat transfer coefficient (float)
            - H_vent_cool_sec_i_m [W/K]: Monthly ventilation heat transfer coefficient (numpy.ndarray (12,))
            - p_cool_sec_i [-]: Probability of active cooling (float)
    Outputs:
            - Heat balance ratio (lambda_cool_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))
            - cooling allowance factor (f_allow_cool_sec_i_m) [-]: Monthly cooling allowance factor (numpy.ndarray (12,))
            - Utilization factor (eta_util_cool_sec_i_m) [-]: Monthly utilization factor (numpy.ndarray (12,))
            - Net cooling demand [MJ]: Monthly net cooling demand (numpy.ndarray (12,))
    """

    def __init__(self, Q_solar_cool_sec_i_m, Q_int_cool_sec_i_m, Q_trans_cool_sec_i_m, Q_vent_cool_sec_i_m, C_sec_i, H_trans_cool_sec_i, H_vent_cool_sec_i_m, p_cool_sec_i):
        # Inputs
        self.Q_solar_cool_sec_i_m = Q_solar_cool_sec_i_m
        self.Q_int_cool_sec_i_m = Q_int_cool_sec_i_m
        self.Q_trans_cool_sec_i_m = Q_trans_cool_sec_i_m
        self.Q_vent_cool_sec_i_m = Q_vent_cool_sec_i_m
        # Calculations
        self.lambda_cool_sec_i_m = self.heat_balance_ratio(
            Q_solar_cool_sec_i_m, Q_int_cool_sec_i_m, Q_trans_cool_sec_i_m, Q_vent_cool_sec_i_m)
        self.f_allow_cool_sec_i_m = self.cooling_allowance_factor(
            self.lambda_cool_sec_i_m)
        self.eta_util_cool_sec_i_m = self.utilization_factor_cooling(
            C_sec_i, H_trans_cool_sec_i, H_vent_cool_sec_i_m, self.lambda_cool_sec_i_m)
        self.Q_cool_net_sec_i_m = self.net_cooling_demand(
            Q_solar_cool_sec_i_m, Q_int_cool_sec_i_m, Q_trans_cool_sec_i_m, Q_vent_cool_sec_i_m, self.eta_util_cool_sec_i_m, self.f_allow_cool_sec_i_m, p_cool_sec_i)

    def heat_balance_ratio(self, Q_solar_cool_sec_i_m, Q_int_cool_sec_i_m, Q_trans_cool_sec_i_m, Q_vent_cool_sec_i_m):
        """
        Heat balance ratio: Ratio between gains and losses 
        Inputs:
            - Q_solar_cool_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
            - Q_int_cool_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
            - Q_trans_cool_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
            - Q_vent_cool_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))

        Outputs:
            - Heat balance ratio (lambda_cool_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))
        """
        # Gain and losses
        Q_loss_cool_sec_i_m = Q_trans_cool_sec_i_m + Q_vent_cool_sec_i_m  # MJ
        Q_gain_cool_sec_i_m = Q_int_cool_sec_i_m + Q_solar_cool_sec_i_m  # MJ

        # Heat balance ratio (lambda_cool_sec_i_m)
        lambda_cool_sec_i_m = Q_loss_cool_sec_i_m / \
            Q_gain_cool_sec_i_m  # [-], monthly loss-gain rate
        return lambda_cool_sec_i_m

    def cooling_allowance_factor(self, lambda_cool_sec_i_m):
        """
        Cooling allowance factor {0, 1} -> if lambda_cool_sec_i_m < 2.5 then 1 otherwise 0
        Inputs:
            - Heat balance ratio (lambda_cool_sec_i_m) [-]: Monthly heat balance ratio (numpy.ndarray (12,))

        Outputs:
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

    def utilization_factor_cooling(self, C_sec_i, H_trans_cool_sec_i, H_vent_cool_sec_i_m, lambda_cool_sec_i_m):
        """
        Utilization factor [-]: fraction of heat gains to be discounted from net cooling demand [0, 1]
        Inputs:
            - C_sec_i [J/K]: Effective heat capacity of the energy sector (float)
            - H_trans_cool_sec_i [W/K]: Transmission heat transfer coefficient (float)
            - H_vent_cool_sec_i_m [W/K]: Monthly ventilation heat transfer coefficient (numpy.ndarray (12,))
            - lambda_cool_sec_i_m [-]: Monthly heat balance ratio (numpy.ndarray (12,))

        Outputs:
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

    def net_cooling_demand(self, Q_solar_cool_sec_i_m, Q_int_cool_sec_i_m, Q_trans_cool_sec_i_m, Q_vent_cool_sec_i_m, eta_util_cool_sec_i_m, f_allow_cool_sec_i_m, p_cool_sec_i):
        """
        Net cooling demand [MJ]: Monthly net cooling demand (numpy.ndarray (12,))
        Inputs:
            - Q_solar_cool_sec_i_m [MJ]: Monthly solar gains per thermal zone (numpy.ndarray (12,))
            - Q_int_cool_sec_i_m [MJ]: Monthly internal gains per thermal zone (numpy.ndarray (12,))
            - Q_trans_cool_sec_i_m [MJ]: Monthly transmission losses thermal zone (numpy.ndarray (12,))
            - Q_vent_cool_sec_i_m [MJ]: Monthly ventilation losses per thermal zone (numpy.ndarray (12,))
            - Utilization factor (eta_util_cool_sec_i_m) [-]: Monthly utilization factor (numpy.ndarray (12,))
            - Cooling allowance factor (f_allow_cool_sec_i_m) [-]: Monthly cooling allowance factor to be included when calculating net cooling demand (numpy.ndarray (12,))

        Outputs:
            - Net cooling demand [MJ]: Monthly net cooling demand (numpy.ndarray (12,))
        """

        Q_loss_cool_sec_i_m = Q_trans_cool_sec_i_m + Q_vent_cool_sec_i_m  # MJ
        Q_gain_cool_sec_i_m = Q_int_cool_sec_i_m + Q_solar_cool_sec_i_m  # MJ

        # MJ, Net space cooling demand
        Q_cool_net_princ_sec_i_m = Q_gain_cool_sec_i_m - \
            eta_util_cool_sec_i_m*Q_loss_cool_sec_i_m

        # Applying allowance factor to cooling needs
        Q_cool_net_princ_sec_i_m = Q_cool_net_princ_sec_i_m * f_allow_cool_sec_i_m

        #
        f_cool_geo_sec_i_m = 0
        Q_cool_net_sec_i_m = p_cool_sec_i * \
            (1 - f_cool_geo_sec_i_m) * Q_cool_net_princ_sec_i_m
        return Q_cool_net_sec_i_m
