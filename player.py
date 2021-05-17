# python 3
# this class combines all basic features of a generic player
import numpy as np
import pulp
import random as rd
import pandas as pd
import os 


prices = 100*np.random.rand(48)

class Player:
    
    def __init__(self):
        # some player might not have parameters
        self.parameters = 0
        self.horizon = 48        
        self.Capa = 60
        self.Pmax = 10
        self.rho_c = 0.95
        self.rho_d = 0.95
        self.delta_t = 0.5

    def set_scenario(self, scenario_data):
        #scenario_data = 40+60*np.random.rand(48)
        data = pd.read_csv(os.path.join(os.getcwd(),"indus_cons_scenarios.csv"),sep=";",decimal=".")
        scenario_data = np.array(data["cons (kW)"])
        self.data = scenario_data
        
        
    def set_prices(self, prices):
        prices = 100*np.random.rand(48)
        self.prices = prices
        

    def compute_all_load(self):
        load = np.zeros(self.horizon)
        for time in range(self.horizon):
            load[time] = self.compute_load(time)
        return load
    

    def compute_battery_load(self):

        my_lp_problem = pulp.LpProblem("My_LP_Problem", pulp.LpMinimize)
        variables = {}

        for t in range(self.horizon):
            variables[t] = {}

            var_name = "battery_load_plus" + str(t)
            variables[t]["battery_load_plus"] = pulp.LpVariable(var_name, 0, self.Pmax)

            var_name = "battery_load_moins" + str(t)
            variables[t]["battery_load_moins"] = pulp.LpVariable(var_name, 0, self.Pmax)

            #stock = delta_t * pulp.lpSum([ (rho_c * variables[s]["battery_load_+"] - (variables[s]["battery_load_-"] * (1/rho_d) ) ) for s in range(t) ] )

            constraint_name = "stock_positif" + str(t)
            my_lp_problem += self.delta_t * pulp.lpSum([ (self.rho_c * variables[s]["battery_load_plus"] - (variables[s]["battery_load_moins"] * (1/self.rho_d) ) ) for s in range(t) ] ) >= 0, constraint_name

            constraint_name = "stock_ne_depasse_pas_la_capacite" + str(t)
            my_lp_problem += self.delta_t * pulp.lpSum([ (self.rho_c * variables[s]["battery_load_plus"] - (variables[s]["battery_load_moins"] * (1/self.rho_d) ) ) for s in range(t) ] ) <= self.Capa, constraint_name

        my_lp_problem.setObjective(pulp.lpSum( [ ( ( self.prices[t] - (self.rho_c * self.rho_d * self.delta_t * self.prices[self.horizon-1]) ) * variables[t]["battery_load_plus"] ) - ( self.prices[t] - ( self.delta_t * self.prices[self.horizon-1] ) * variables[t]["battery_load_moins"] )  for t in range(self.horizon)] ))
        my_lp_problem.solve()

        battery_load = []

        for t in range(self.horizon):
            battery_load.append( variables[t]["battery_load_plus"].value() - variables[t]["battery_load_moins"].value())

        return battery_load

    def take_decision(self, time):
        battery_load = self.compute_battery_load()
        return battery_load[time]

    def compute_load(self, time):
        load = self.take_decision(time)
        # do stuff ?
        load += self.data[time]
        return load

    def reset(self):
        # reset all observed data
        pass

if __name__ == "__main__":
    Industrial_consumer = Player()
    Industrial_consumer.set_prices(prices)
    Industrial_consumer.set_scenario(scenario_data)
    print(Industrial_consumer.compute_all_load())
