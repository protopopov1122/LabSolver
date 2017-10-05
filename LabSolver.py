# Physics lab solver
# Author: Eugene aka Father
# License: WTFPL
#
# You should edit only main function on the bottom of the file
# and then run it

import math
import sympy
from scipy.stats import t as student


# Students t-distribution calculator
# I am not a mathematician so I don't have a clue how
# it works, but it gives results almost equal to tabular values
def eval_student(B: float, n: int):
    return student.ppf(1 - (1.0 - B) / 2, n - 1) # Magic formula. I don't know what it means, but it works


# Evaluates average value and error for variables with multiple measurements
def long_evaluate_average(source: ([float], float),
                          variable: sympy.Symbol,
                          settings: {str: float}):
    source_vals = source[0]
    error = source[1]
    average = sum(source_vals) / len(source_vals)
    S = math.sqrt(sum([(x-average)**2 for x in source_vals]) / (len(source_vals) * (len(source_vals) - 1)))
    B = settings['B']
    tB_from_N = eval_student(B, len(source_vals))
    tB_from_Inf = eval_student(B, 10000) # 10000 measurements is almost infinity for our case
    delta_Xs = S * tB_from_N
    delta_Xd = error / 3 * tB_from_Inf
    if delta_Xs > 3 * delta_Xd:
        delta_X = delta_Xs
    elif delta_Xd > 3 * delta_Xs:
        delta_X = delta_Xd
    else:
        delta_X = math.sqrt(delta_Xs**2 + delta_Xd**2)
    epsilon = delta_X / average * 100
    return {
        'result': average,
        'error': delta_X,
        'epsilon': epsilon
    }


# Evaluates average value and error for variables with only one measurement
def short_evaluate_average(source: ([float], float), variable: sympy.Symbol, settings: {str: float}):
    average = source[0][0]
    error = source[1]
    B = settings['B']
    tB_from_Inf = eval_student(B, 10000)
    delta_X = error / 3 * tB_from_Inf
    epsilon = delta_X / average * 100
    return {
        'result': average,
        'error': delta_X,
        'epsilon': epsilon
    }


# Facade for two above functions which decides which calculation should be performed
def evaluate_average_result(experiment: {sympy.Symbol: ([float], float)},
                            variable: sympy.Symbol,
                            settings: {str: float}):
    res = experiment[variable]
    if len(res[0]) == 1:
        return short_evaluate_average(res, variable, settings)
    else:
        return long_evaluate_average(res, variable, settings)


# Calculate partial differential from formula, evaluate its value and calculate error
def evaluate_partial_error(formula: sympy.Expr,
                           variable: sympy.Symbol,
                           values: {sympy.Symbol: float},
                           avg_results: {sympy.Symbol: {str: float}}):
    differential = formula.diff(variable).evalf(subs=values)
    return differential * avg_results[variable]['error']


# Calculate given formula value and error with given variables and constants
def evaluate_formula(formula: sympy.Expr,
                     avg_results: {sympy.Symbol: {str: float}},
                     constants: {sympy.Symbol: float}):
    values = dict()
    for variable in avg_results.keys():
        values[variable] = avg_results[variable]['result']
    for variable in constants.keys():
        values[variable] = constants[variable]
    result = formula.evalf(subs=values)
    delta = math.sqrt(sum([evaluate_partial_error(formula, variable, values, avg_results)**2 for variable in avg_results.keys()]))
    epsilon = delta / result * 100
    return {
        'result': result,
        'delta': delta,
        'epsilon': epsilon
    }


# Calculate each experiment measurement average values, errors and
# formula results based on given values and constants
def evaluate_experiment(formulas: [(str, sympy.Expr)],
                        experiment: {sympy.Symbol: ([float], float)},
                        constants: {sympy.Symbol: float},
                        settings: {str: float}):
    avg_results = dict()
    for variable in experiment.keys():
        avg_results[variable] = evaluate_average_result(experiment, variable, settings)
    results = {
        'average': avg_results
    }
    for formula in formulas:
        results[formula[0]] = evaluate_formula(formula[1], avg_results, constants)
    return results


# Evaluate experiments
def evaluate(formulas: [(str, sympy.Expr)],
             experiments: [{sympy.Symbol: ([float], float)}],
             constants: {sympy.Symbol: float},
             settings: {str: float}):
    return [evaluate_experiment(formulas, experiment, constants, settings) for experiment in experiments]


# Main function
# Change only this code to evaluate lab
def main():
    # Define used variables and constants
    phi = sympy.symbols('phi')
    R = sympy.symbols('R')
    I = sympy.symbols('I')
    n = sympy.symbols('n')
    mu = sympy.symbols('mu')

    # Define used formulas using variables from above block
    # And add them to formula list
    B = (mu * n * I) / (2 * R * sympy.tan(sympy.rad(phi)))
    formulas = [('B', B)]   # Tuple: formula name, formula

    # Define results of all your measurements
    # Each measurement is dictionary which keys are variables from
    # first block and tuple
    # Tuple consists of measurement result array and measurement instrument error
    experiments = [
        {I: ([1.5], 0.025),
         phi: ([65], 0.25),
         R: ([0.18], 0.005)}
    ]

    # Define used constants. They don't have errors so are used as is
    constants = {
        n: 3,
        mu: 12.57e-7
    }

    # Just some settings. Currently only B value
    settings = {
        'B': 0.95
    }

    # Evaluate that!
    print(evaluate(formulas, experiments, constants, settings))


if __name__ == '__main__':
    main()