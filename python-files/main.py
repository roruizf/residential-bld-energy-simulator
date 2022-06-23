import numpy as np
from models.models import EnergySector


def main():
    V_sec_i = 10    
    t_m = (np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])*(24*3600)/1_000_000).tolist()
    energy_sector_1 = EnergySector(V_sec_i, t_m)
    return energy_sector_1
    
if __name__ == "__main__":
    energy_sector_1 = main()
    print(energy_sector_1.Q_int_heat_sec_i_m)
    print(type(energy_sector_1.Q_int_heat_sec_i_m))
    