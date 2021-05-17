# python 3
# this class combines all basic features of a generic player
import numpy as np
import pulp

Capa = 60
Pmax = 10
rho_c = 0.95
rho_d = 0.95
delta_t = 0.5
#prices = 100*np.random.rand(48)
#scenario_data = np.random.rand(73, 50)

class Player:

    def __init__(self):
        # some player might not have parameters
        self.parameters = 0
        self.horizon = 48

    def set_scenario(self, scenario_data):
        self.data = scenario_data

    def set_prices(self, prices):
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

            var_name = "battery_load_+" + str(t)
            variables[t]["battery_load_+"] = pulp.LpVariable(var_name, 0, Pmax)

            var_name = "battery_load_-" + str(t)
            variables[t]["battery_load_-"] = pulp.LpVariable(var_name, 0, Pmax)

            #stock = delta_t * pulp.lpSum([ (rho_c * variables[s]["battery_load_+"] - (variables[s]["battery_load_-"] * (1/rho_d) ) ) for s in range(t) ] )

            constraint_name = "stock_positif" + str(t)
            my_lp_problem += delta_t * pulp.lpSum([ (rho_c * variables[s]["battery_load_+"] - (variables[s]["battery_load_-"] * (1/rho_d) ) ) for s in range(t) ] ) >= 0, constraint_name

            constraint_name = "stock_ne_depasse_pas_la_capacite" + str(t)
            my_lp_problem += delta_t * pulp.lpSum([ (rho_c * variables[s]["battery_load_+"] - (variables[s]["battery_load_-"] * (1/rho_d) ) ) for s in range(t) ] ) <= Capa, constraint_name

        my_lp_problem.setObjective(pulp.lpSum( [ ( ( self.prices[t] - (rho_c * rho_d * delta_t * self.prices[self.horizon-1]) ) * variables[t]["battery_load_+"] ) - ( self.prices[t] - ( delta_t * self.prices[self.horizon-1] ) * variables[t]["battery_load_-"] )  for t in range(self.horizon)] ))
        my_lp_problem.solve()

        battery_load = []

        for t in range(self.horizon):
            battery_load.append( variables[t]["battery_load_+"].value - variables[t]["battery_load_-"].value)

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

"""
Industrial_consumer = Player()
Industrial_consumer.set_prices(prices)
Industrial_consumer.set_scenario(scenario_data)
print(Industrial_consumer.compute_all_load())
"""
