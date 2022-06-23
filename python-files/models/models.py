from typing import Union
from pydantic import BaseModel, Field
from functions.monthly_gains_and_losses import internal_gains

# Building
# -----------


class Building(BaseModel):
    pass

# Protected volume
# -----------------


class ProtectedVolume(BaseModel):
    pass

# K Volume
# -----------


class KVolume(BaseModel):
    pass

# PEB Unit
# -----------


class UnitPEB(BaseModel):
    pass

# Ventilation Zone
# -----------


class VentilationZone(BaseModel):
    """
    Les systèmes de ventilation sont subdivisés en quatre types différents (voir également les annexes VHR et VHNR au présent arrêté) : 
    * système A : ventilation naturelle, 
    * système B : ventilation mécanique simple flux par insufflation, 
    * système C : ventilation mécanique simple flux par extraction, 
    * système D : ventilation mécanique double flux. 
    """
    pass

# Energy Sector
# --------------


class EnergySector(BaseModel):
    V_sec_i: float = Field(...)
    t_m: list = Field(...)
    print(type(V_sec_i))
    print(type(t_m))
    Q_int_heat_sec_i_m = internal_gains(V_sec_i=V_sec_i, t_m=t_m)
    # Q_int_overh_sec_i_m = Field(default=internal_gains(V_sec_i=V_sec_i, t_m=t_m))
    # Q_int_cool_sec_i_m = Field(default=internal_gains(V_sec_i=V_sec_i, t_m=t_m))


# class EnergySector:
#     """
#     Transmission losses (monthly)
#     Inputs:
#             - H_trans_heat_sec_i [W/K]: Transmission heat transfer coefficient for heating (float)
#             - H_trans_overh_sec_i [W/K]: Transmission heat transfer coefficient for overheating (float)
#             - H_trans_cool_sec_i [W/K]: Transmission heat transfer coefficient for cooling (float)
#             - T_e_m [°C]: Monthly average outdoor temperature (numpy.ndarray (12,))
#             - t_m [Ms]: Month time length (numpy.ndarray (12,))
#     Outputs:
#             - Transmission losses [MJ]: Monthly transmission losses for heating, overheating and cooling (numpy.ndarray (12,))
#     """

#     def __init__(self, V_sec_i, t_m):
#         self.Q_int_heat_sec_i_m: list = internal_gains(V_sec_i=V_sec_i, t_m=t_m)
