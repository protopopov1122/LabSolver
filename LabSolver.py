# Physics lab solver
# Author: Eugene Protopopov
# License: WTFPL

# This script is able to process physics lab measurements
# and calculate some results and create report. Generally, results may be displayed
# in two different ways: simple structure and TeX document
# Use simple structure to view evaluation results or use
# TeX document to get full report. TeX document may be converted
# into PDF using online 'tex to pdf' services or LaTex package

# There are two ways to run this script:
#   * Command line interface - run without command line arguments.
#       It's quite easy but not flexible. Also if you want to
#       run script multiple times with same data, it's not the best
#       scenario.
#   * Custom main function - run with argument 'custom'

# Script is written on Python 3. Configure it before run.
# On Windows best way to get this work is using Python from Anaconda
# distribution:
# Run Anaconda Prompt->python->import LabSolver->LabSolver.custom_main() or simply main()
# On Linux just install sympy and scipy packages and run this script

# To define custom main:
# Now go to the 'custom_main' function at the bottom and follow instructions
# there to configure this script

import math
import sympy
import sys
from scipy.stats import t as student
from LabPrinter import print_lab
from LabParser import parse


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
                           avg_common: dict,
                           avg_results: {sympy.Symbol: {str: float}},
                           settings: dict):
    rnd = lambda x: round_to_n(x, settings['round']) if 'round' in settings else x
    differential = rnd(formula.diff(variable).evalf(subs=values))
    result = {
        'result': rnd(differential * (avg_results[variable]['error'] if variable in avg_results else avg_common[variable]['error']))
    }
    if settings['extended']:
        result['symbol'] = variable
        result['differential'] = formula.diff(variable)
        result['differential_value'] = differential
        result['partial_error'] = rnd(avg_results[variable]['error'] if variable in avg_results else avg_common[variable]['error'])
    return result


# Calculate given formula value and error with given variables and constants
def evaluate_formula(formula: sympy.Expr,
                     avg_common: dict,
                     avg_results: {sympy.Symbol: {str: float}},
                     constants: {sympy.Symbol: float},
                     settings: dict):
    rnd = lambda x: round_to_n(x, settings['round']) if 'round' in settings else x
    values = dict()
    for variable in avg_results.keys():
        values[variable] = avg_results[variable]['result']
    for variable in constants.keys():
        values[variable] = constants[variable]
    for variable in avg_common.keys():
        values[variable] = avg_common[variable]['result']
    result = rnd(formula.evalf(subs=values))
    differentials = [evaluate_partial_error(formula, variable, values, avg_common, avg_results, settings) for variable in avg_results.keys()]
    differentials.extend(evaluate_partial_error(formula, variable, values, avg_common, avg_results, settings) for variable in avg_common.keys())
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
                        common_measurements: dict,
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
        results['formulas'][formula[0]] = evaluate_formula(formula[1], common_measurements, avg_results, constants, settings)
    if settings['extended'] and settings['round']:
        results['round'] = settings['round']
    return results


def evaluate_common_measurements(measurements: {sympy.Symbol: ([float], float)},
                                 settings):
    avg_common = dict()
    for variable in measurements.keys():
        avg_common[variable] = evaluate_average_result(measurements, variable, settings)
    return avg_common


# Evaluate experiments
def evaluate(formulas: [(str, sympy.Expr)],
             common_measurements: {sympy.Symbol: ([float], float)},
             experiments: [{sympy.Symbol: ([float], float)}],
             constants: {sympy.Symbol: float},
             settings: dict):
    avg_common = evaluate_common_measurements(common_measurements, settings)
    results = [evaluate_experiment(formulas, avg_common, experiment, constants, settings) for experiment in experiments]
    result = {
        'common': avg_common,
        'result': results
    }
    if settings['extended']:
        result['constants'] = constants
    return result


# Print results
def evaluate_print(formulas: [(str, sympy.Expr)],
                 common_measurements: {sympy.Symbol: ([float], float)},
                 experiments: [{sympy.Symbol: ([float], float)}],
                 constants: {sympy.Symbol: float},
                 settings: dict):
    settings['extended'] = False
    result = evaluate(formulas, common_measurements, experiments, constants, settings)
    print(result)

# TeX to console
def evaluate_tex_stdout(formulas: [(str, sympy.Expr)],
             common_measurements: {sympy.Symbol: ([float], float)},
             experiments: [{sympy.Symbol: ([float], float)}],
             constants: {sympy.Symbol: float},
             settings: dict):
    settings['extended'] = True
    result = evaluate(formulas, common_measurements, experiments, constants, settings)
    print(print_lab(result))


# TeX to file
def evaluate_tex_file(filename: str):
    def evl(formulas: [(str, sympy.Expr)],
             common_measurements: {sympy.Symbol: ([float], float)},
             experiments: [{sympy.Symbol: ([float], float)}],
             constants: {sympy.Symbol: float},
             settings: dict):
        settings['extended'] = True
        result = evaluate(formulas, common_measurements, experiments, constants, settings)
        out = open(filename, 'w')
        print_lab(result, out)
        out.flush()
        out.close()
    return evl


# Custom main function
# Edit code there to define your measurements, formulas
# and generate results
def custom_main():
    # Define used variables and constants
    phi = sympy.symbols('phi')
    R = sympy.symbols('R')
    I = sympy.symbols('I')
    n = sympy.symbols('n')
    mu = sympy.symbols('mu')

    # Define formulas using variables from above block
    # And add them to the formula list
    # These formulas will be applied to all your experiments
    B = (mu * n * I) / (2 * R * sympy.tan(sympy.rad(phi)))
    formulas = [(sympy.symbols('B'), B)]   # Tuple: formula name, formula

    # Define results of all your experiments
    # 'Experiment' consists of multiple variable measurements
    # Each variable measurement consists of value array and precision

    # Common measurements are performed one time and then used in all calculations
    common_measurements = {R: ([0.18], 0.005)}

    # Describe your measurements, formulas will be applied to each of them
    experiments = [
        {I: ([1], 0.025), phi: ([22, 24], 1)},
        {I: ([2.4], 0.025), phi: ([44, 46], 1)},
        {I: ([3.5], 0.025), phi: ([56, 58], 1)},
        {I: ([4.6], 0.025), phi: ([62], 1)},
        {I: ([5], 0.025), phi: ([64], 1)}
    ]

    # Define used constants. They don't have precision so are used as is
    constants = {
        n: 3,
        mu: 12.57e-7
    }

    # Each experiment + common measurements + constants must provide
    # complete information to calculate each formula you defined
    # Otherwise, it will not work

    # Just some settings.
    # You may remove 'round' parameter to get
    # maximal precision
    settings = {
        'B': 0.95,
        'extended': False, # If you want to process results manually
                           # switch 'extended' to True to be able to get complete info
        'round': 4
    }

    # Calculate results and handle them four different ways
    # Just uncomment one of them

    # 1. Print only results as a Python structure
    #    May be used just to view final experiment results
    # evaluate_print(formulas, common_measurements, experiments, constants, settings)

    # 2. Print results as TeX document to console
    #    Not so useful, but you may copy results from console
    #    See also option below this one
    # evaluate_tex_stdout(formulas, common_measurements, experiments, constants, settings)

    # 3. Save results as TeX document somewhere
    #    In my opinion it's the best option to get complete visual report.
    #    Do not forget to convert TeX to PDF via some external service
    # evaluate_tex_file('some_file_name.tex')(formulas, common_measurements, experiments, constants, settings)

    # 4. Do some custom processing
    #    No results will be printed so you should
    #    write some code to process them
    #    The same structure is printed on type 1, except for 'extended' flag,
    #    you may redefine it
    # result = evaluate(formulas, common_measurements, experiments, constants, settings)


def main():
    formulas, common, experiments, constants, settings = parse()
    while True:
        line = input('Select result save display type:\n'
                     '1. Display brief results\n'
                     '2. Display TeX markup\n'
                     '3. Save TeX markup to file - Recommended\n'
                     '>>> ')
        if line == '1':
            print(evaluate(formulas, common, experiments, constants, settings))
            break
        elif line == '2':
            settings['extended'] = True
            print(print_lab(evaluate(formulas, common, experiments, constants, settings)))
            break
        elif line == '3':
            fname = input('Enter file name: ')
            evaluate_tex_file(fname)(formulas, common, experiments, constants, settings)
            break
        else:
            print('There is not option \'%s\'' % line)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'custom':
        custom_main()
    else:
        main()