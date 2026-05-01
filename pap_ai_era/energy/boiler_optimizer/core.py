import numpy as np

class BoilerState:
    """
    Represents the operational state of a boiler.
    """
    def __init__(self, fuel_flow, air_flow, feedwater_flow, feedwater_temp, 
                 steam_flow=None, steam_temp=None, steam_pressure=None, 
                 flue_temp=None, o2=None):
        self.fuel_flow = fuel_flow # TPH
        self.air_flow = air_flow # TPH or Nm3/h
        self.feedwater_flow = feedwater_flow # TPH
        self.feedwater_temp = feedwater_temp # Celsius
        
        # Outputs (can be measured or predicted)
        self.steam_flow = steam_flow
        self.steam_temp = steam_temp
        self.steam_pressure = steam_pressure
        self.flue_temp = flue_temp
        self.o2 = o2

    def to_dict(self):
        return self.__dict__

class Boiler:
    """
    Boiler Digital Twin core.
    """
    def __init__(self, config, model=None):
        self.config = config
        self.model = model

    def calculate_efficiency(self, state):
        """
        Calculates thermal efficiency using the Direct Method.
        Efficiency = (Steam Energy - Feedwater Energy) / Fuel Energy
        """
        # Simplified enthalpies (h = Cp * T) or use steam tables
        # For demo, using linear approximations
        cp_steam = 2.1 # kJ/kg-K
        cp_water = 4.18 # kJ/kg-K
        
        useful_heat = state.steam_flow * (2800) # Roughly h_g at 60 bar
        feedwater_heat = state.feedwater_flow * cp_water * state.feedwater_temp
        
        fuel_cv = self.config.get("fuel", {}).get("CV", 4000) # kcal/kg
        fuel_energy = state.fuel_flow * fuel_cv * 4.1868 # Convert to kJ
        
        if fuel_energy <= 0:
            return 0.0
        
        return (useful_heat - feedwater_heat) / fuel_energy

    def simulate(self, controls, disturbances):
        """
        Runs the simulation using the attached model.
        """
        if self.model:
            return self.model.predict(controls, disturbances)
        return self._basic_physics_simulate(controls, disturbances)

    def _basic_physics_simulate(self, controls, disturbances):
        """
        Fallback first-principles model.
        """
        fuel = controls.get("fuel_flow", 10)
        air = controls.get("air_flow", 100)
        fw_temp = disturbances.get("feedwater_temp", 105)
        
        # Empirical heuristics for demonstration
        steam_flow = fuel * 7.5 * (1 - (air/fuel - 12)**2 * 0.01) # Peak efficiency at air/fuel=12
        o2 = max(0.5, (air/fuel - 11.5) * 0.8)
        flue_temp = 140 + (fuel * 2) + (o2 * 10)
        
        return BoilerState(
            fuel_flow=fuel,
            air_flow=air,
            feedwater_flow=steam_flow * 1.02, # accounting for blowdown
            feedwater_temp=fw_temp,
            steam_flow=steam_flow,
            steam_temp=485,
            steam_pressure=64,
            flue_temp=flue_temp,
            o2=o2
        )
