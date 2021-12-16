import pandas as pd


class SolarGains:
    def __init__(self):
        pass

    # def solar_gains_heating(self):


class InternalGains:
    """
    Internal gains (monthly)
    Inputs:
            - V_sec_i [m³]: House / appartment total volume (float)
            - t_m [Ms]: Month time length (numpy.ndarray (12,))
    Outputs:
            - Internal gains [MJ]: Monthly internal gains for heating, overheating and cooling (numpy.ndarray (12,))
    """

    def __init__(self, V_sec_i, t_m):
        # V_sec_i [m³]: House / appartment total volume (float)
        self.Q_int_heat_sec_i_m = self.internal_gains(V_sec_i, t_m)
        self.Q_int_overh_sec_i_m = self.Q_int_heat_sec_i_m
        self.Q_int_cool_sec_i_m = self.Q_int_heat_sec_i_m

    def internal_gains(self, V_sec_i, t_m):
        V_EPR = V_sec_i  # m³
        if V_EPR <= 192:
            Q_int_sec_i_m = (1.41 * V_EPR + 78) * V_sec_i/V_EPR * t_m  # MJ
        else:
            Q_int_sec_i_m = (0.67 * V_EPR + 220) * V_sec_i/V_EPR * t_m  # MJ
        return Q_int_sec_i_m


class TransmissionLosses:
    """
    Transmission losses (monthly)
    Inputs:
            - H_trans_heat_sec_i [W/K]: Transmission heat transfer coefficient for heating (float)
            - H_trans_overh_sec_i [W/K]: Transmission heat transfer coefficient for overheating (float)
            - H_trans_cool_sec_i [W/K]: Transmission heat transfer coefficient for cooling (float)
            - T_e_m [°C]: Monthly average outdoor temperature (numpy.ndarray (12,))
            - t_m [Ms]: Month time length (numpy.ndarray (12,))
    Outputs:
            - Transmission losses [MJ]: Monthly transmission losses for heating, overheating and cooling (numpy.ndarray (12,))
    """

    def __init__(self, H_trans_heat_sec_i, H_trans_overh_sec_i, H_trans_cool_sec_i, T_e_m, t_m):
        self.H_trans_heat_sec_i = H_trans_heat_sec_i
        self.H_trans_overh_sec_i = H_trans_overh_sec_i
        self.H_trans_cool_sec_i = H_trans_cool_sec_i

        self.Q_trans_heat_sec_i_m = self.transmission_losses_heating(
            self.H_trans_heat_sec_i, T_e_m, t_m)
        self.Q_trans_overh_sec_i_m = self.transmission_losses_overheating(
            self.H_trans_overh_sec_i, T_e_m, t_m)
        self.Q_trans_cool_sec_i_m = self.transmission_losses_cooling(
            self.H_trans_cool_sec_i, T_e_m, t_m)

    def transmission_losses_heating(self, H_trans_heat_sec_i, T_e_m, t_m):
        Q_trans_heat_sec_i_m = H_trans_heat_sec_i * (18 - T_e_m) * t_m  # MJ
        return Q_trans_heat_sec_i_m

    def transmission_losses_overheating(self, H_trans_overh_sec_i, T_e_m, t_m):
        Q_trans_overh_sec_i_m = H_trans_overh_sec_i * \
            (23 - (T_e_m + 1)) * t_m  # MJ
        return Q_trans_overh_sec_i_m

    def transmission_losses_cooling(self, H_trans_cool_sec_i, T_e_m, t_m):
        Q_trans_cool_sec_i_m = H_trans_cool_sec_i * \
            (23 - (T_e_m + 1)) * t_m  # MJ
        return Q_trans_cool_sec_i_m


class VentilationLosses:
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

    def __init__(self, H_vent_heat_sec_i, H_vent_overh_sec_i_m, H_vent_cool_sec_i_m, T_e_m, t_m):
        self.H_vent_heat_sec_i = H_vent_heat_sec_i
        self.H_vent_overh_sec_i_m = H_vent_overh_sec_i_m
        self.H_vent_cool_sec_i_m = H_vent_cool_sec_i_m

        self.Q_vent_heat_sec_i_m = self.ventilation_losses_heating(
            self.H_vent_heat_sec_i, T_e_m, t_m)
        self.Q_vent_overh_sec_i_m = self.ventilation_losses_overheating(
            self.H_vent_overh_sec_i_m, T_e_m, t_m)
        self.Q_vent_cool_sec_i_m = self.ventilation_losses_cooling(
            self.H_vent_cool_sec_i_m, T_e_m, t_m)

    def ventilation_losses_heating(self, H_vent_heat_sec_i, T_e_m, t_m):
        Q_vent_heat_sec_i_m = H_vent_heat_sec_i * (18 - T_e_m) * t_m  # MJ
        return Q_vent_heat_sec_i_m

    def ventilation_losses_overheating(self, H_vent_overh_sec_i_m, T_e_m, t_m):
        Q_vent_overh_sec_i_m = H_vent_overh_sec_i_m * \
            (23 - (T_e_m + 1)) * t_m  # MJ
        return Q_vent_overh_sec_i_m

    def ventilation_losses_cooling(self, H_vent_cool_sec_i_m, T_e_m, t_m):
        Q_vent_cool_sec_i_m = H_vent_cool_sec_i_m * \
            (23 - (T_e_m + 1)) * t_m  # MJ
        return Q_vent_cool_sec_i_m
