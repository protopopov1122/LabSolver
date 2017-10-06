# Physics lab solver
# Author: Eugene Protopopov
# License: WTFPL
#
# You should edit only main function on the bottom of the file
# and then run it

import math
import sympy
from scipy.stats import t as student
from LabPrinter import print_lab


# Used to round to N significant digits
def round_to_n(x, n):
    string = ("%." + str(n-1) + "e") % x
    return float(string)

# Students t-distribution calculator
# I am not a mathematician so I don't have a clue how
# it works, but it gives results almost equal to tabular values
def eval_student(B: float, n: int):
    return student.ppf(1 - (1.0 - B) / 2, n - 1) # Magic formula. I don't know what it means, but it works


# Evaluates average value and error for variables with multiple measurements
def long_evaluate_average(source: ([float], float),
                          variable: sympy.Symbol,
                          settings: dict):
    rnd = lambda x: round_to_n(x, settings['round']) if 'round' in settings else x
    source_vals = [rnd(val) for val in source[0]]
    error = rnd(source[1])
    average = rnd(sum(source_vals) / len(source_vals))
    S = rnd(math.sqrt(sum([(x-average)**2 for x in source_vals]) / (len(source_vals) * (len(source_vals) - 1))))
    B = settings['B']
    tB_from_N = rnd(eval_student(B, len(source_vals)))
    tB_from_Inf = rnd(eval_student(B, 10000)) # 10000 measurements is almost infinity for our case
    delta_Xs = rnd(S * tB_from_N)
    delta_Xd = rnd(error / 3 * tB_from_Inf)
    if delta_Xs > 3 * delta_Xd:
        delta_X = delta_Xs
    elif delta_Xd > 3 * delta_Xs:
        delta_X = delta_Xd
    else:
        delta_X = rnd(math.sqrt(delta_Xs**2 + delta_Xd**2))
    epsilon = rnd(delta_X / average * 100)
    result = {
        'result': average,
        'error': delta_X,
        'epsilon': epsilon
    }
    if settings['extended']:
        result['type'] = 'long'
        result['measurements'] = source_vals
        result['measurement_error'] = error
        result['delta'] = {
            'XS': delta_Xs,
            'XD': delta_Xd
        }
        result['distrib'] = {
            'B': B,
            'tB_N': tB_from_N,
            'tB_Inf': tB_from_Inf
        }
        result['S'] = S
    return result


# Evaluates average value and error for variables with only one measurement
def short_evaluate_average(source: ([float], float), variable: sympy.Symbol, settings: dict):
    rnd = lambda x: round_to_n(x, settings['round']) if 'round' in settings else x
    average = rnd(source[0][0])
    error = rnd(source[1])
    B = settings['B']
    tB_from_Inf = rnd(eval_student(B, 10000))
    delta_X = rnd(error / 3 * tB_from_Inf)
    epsilon = rnd(delta_X / average * 100)
    result = {
        'result': average,
        'error': delta_X,
        'epsilon': epsilon
    }
    if settings['extended']:
        result['measurement_error'] = error
        result['type'] = 'short'
        result['distrib'] = {
            'B': B,
            'tB_Inf': tB_from_Inf
        }
    return result


# Facade for two above functions which decides which calculation should be performed
def evaluate_average_result(experiment: {sympy.Symbol: ([float], float)},
                            variable: sympy.Symbol,
                            settings: dict):
    res = experiment[variable]
    if len(res[0]) == 1:
        return short_evaluate_average(res, variable, settings)
    else:
        return long_evaluate_average(res, variable, settings)


# Calculate partial differential from formula, evaluate its value and calculate error
def evaluate_partial_error(formula: sympy.Expr,
                           variable: sympy.Symbol,
                           values: {sympy.Symbol: float},
                           avg_results: {sympy.Symbol: {str: float}},
                           settings: dict):
    rnd = lambda x: round_to_n(x, settings['round']) if 'round' in settings else x
    differential = rnd(formula.diff(variable).evalf(subs=values))
    result = {
        'result': rnd(differential * avg_results[variable]['error'])
    }
    if settings['extended']:
        result['symbol'] = variable
        result['differential'] = formula.diff(variable)
        result['differential_value'] = differential
        result['partial_error'] = rnd(avg_results[variable]['error'])
    return result


# Calculate given formula value and error with given variables and constants
def evaluate_formula(formula: sympy.Expr,
                     avg_results: {sympy.Symbol: {str: float}},
                     constants: {sympy.Symbol: float},
                     settings: dict):
    rnd = lambda x: round_to_n(x, settings['round']) if 'round' in settings else x
    values = dict()
    for variable in avg_results.keys():
        values[variable] = avg_results[variable]['result']
    for variable in constants.keys():
        values[variable] = constants[variable]
    result = rnd(formula.evalf(subs=values))
    differentials = [evaluate_partial_error(formula, variable, values, avg_results, settings) for variable in avg_results.keys()]
    delta = rnd(math.sqrt(sum(partial['result']**2 for partial in differentials)))
    epsilon = rnd(delta / result * 100)
    data = {
        'result': result,
        'delta': delta,
        'epsilon': epsilon
    }
    if settings['extended']:
        data['formula'] = formula
        data['differentials'] = differentials
        data['values'] = values
        data['B'] = settings['B']
    return data


# Calculate each experiment measurement average values, errors and
# formula results based on given values and constants
def evaluate_experiment(formulas: [(str, sympy.Expr)],
                        experiment: {sympy.Symbol: ([float], float)},
                        constants: {sympy.Symbol: float},
                        settings: dict):
    avg_results = dict()
    for variable in experiment.keys():
        avg_results[variable] = evaluate_average_result(experiment, variable, settings)
    results = {
        'average': avg_results,
        'formulas': dict()
    }
    for formula in formulas:
        results['formulas'][formula[0]] = evaluate_formula(formula[1], avg_results, constants, settings)
    if settings['extended'] and settings['round']:
        results['round'] = settings['round']
    return results


# Evaluate experiments
def evaluate(formulas: [(str, sympy.Expr)],
             experiments: [{sympy.Symbol: ([float], float)}],
             constants: {sympy.Symbol: float},
             settings: dict):
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
    formulas = [(sympy.symbols('B'), B)]   # Tuple: formula name, formula

    # Define results of all your measurements
    # Each measurement is dictionary which keys are variables from
    # first block and tuple
    # Tuple consists of measurement result array and measurement instrument error
    experiments = [
        {I: ([1], 0.025),
         phi: ([22, 24], 1),
         R: ([0.18], 0.005)}
    ]

    # Define used constants. They don't have errors so are used as is
    constants = {
        n: 3,
        mu: 12.57e-7
    }

    # Just some settings. Currently only B value
    settings = {
        'B': 0.95,
        'extended': True,
        'round': 4
    }

    # Evaluate that!
    result = evaluate(formulas, experiments, constants, settings)
    print_lab(result)


if __name__ == '__main__':
    main()