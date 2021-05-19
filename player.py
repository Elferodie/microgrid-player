# python 3
# this class combines all basic features of a generic player
import numpy as np
import pulp
import pandas as pd
import os


class Player:

    def __init__(self):
        # some player might not have parameters
        self.Capa = 60
        self.Pmax = 10
        self.rho_c = 0.95
        self.rho_d = 0.95
        self.delta_t = 0.5
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

            var_name = "battery_load_plus" + str(t)
            variables[t]["battery_load_plus"] = pulp.LpVariable(var_name, 0, self.Pmax)

            var_name = "battery_load_moins" + str(t)
            variables[t]["battery_load_moins"] = pulp.LpVariable(var_name, 0, self.Pmax)

            stock = self.delta_t * pulp.lpSum([(self.rho_c * variables[s]["battery_load_plus"] - (
                    variables[s]["battery_load_moins"] * (1 / self.rho_d))) for s in
                                               range(t+1)])

            constraint_name = "stock_positif" + str(t)
            my_lp_problem += stock >= 0, constraint_name

            constraint_name = "stock_ne_depasse_pas_la_capacite" + str(t)
            my_lp_problem += stock <= self.Capa, constraint_name

        #my_lp_problem.setObjective(pulp.lpSum([((self.prices[t] - (
        #            self.rho_c * self.rho_d * self.delta_t * self.prices[self.horizon - 1])) * variables[t][
        #                                            "battery_load_plus"]) - (self.prices[t] - (
        #            self.delta_t * self.prices[self.horizon - 1]) * variables[t]["battery_load_moins"]) for t in
        #                                       range(self.horizon)]))
        my_lp_problem.setObjective( pulp.lpSum(
            [self.prices[t] * self.delta_t * (variables[t]["battery_load_plus"] - variables[t]["battery_load_moins"])
             for t in
             range(self.horizon)]) - self.rho_d * stock * self.prices[self.horizon-1])

        my_lp_problem.solve()

        battery_load = []

        for t in range(self.horizon):
            battery_load.append(variables[t]["battery_load_plus"].varValue - variables[t]["battery_load_moins"].varValue)

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
    #prices = 100 * np.random.rand(48)
    prices = 100 * np.ones(48)
    prices[0] = 10
    prices[20] = 150
    data = pd.read_csv(os.path.join(os.getcwd(), "indus_cons_scenarios.csv"), sep=";", decimal=".")
    scenario_data = np.array(data["cons (kW)"])
    Industrial_consumer = Player()
    Industrial_consumer.set_prices(prices)
    Industrial_consumer.set_scenario(scenario_data)
    print(Industrial_consumer.compute_battery_load())
