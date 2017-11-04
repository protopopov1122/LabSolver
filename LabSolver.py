# Copyright (c) 2017 Jevgenijs Protopopovs
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math
import sympy
from scipy.stats import t as student


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
             symbols: {str, str},
             settings: dict):
    avg_common = evaluate_common_measurements(common_measurements, settings)
    results = [evaluate_experiment(formulas, avg_common, experiment, constants, settings) for experiment in experiments]
    result = {
        'common': avg_common,
        'result': results
    }
    if settings['extended']:
        result['constants'] = constants
    result['symbols'] = symbols
    return result