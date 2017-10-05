import math
import sympy
from scipy.stats import t as student


def eval_student(B: float, n: int):
    return student.ppf(1 - (1.0 - B) / 2, n - 1) # Magic formula. I don't know what it means, but it works


# Evaluates average value and error for variables with multiple measurements
def long_evaluate_average(source: ([float], float), variable: sympy.Symbol, settings: {str: float}):
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
        'epsilon': epsilon,
        'B': B
    }


def short_evaluate_average(source: ([float], float), variable: sympy.Symbol, settings: {str: float}):
    average = source[0][0]
    error = source[1]
    B = settings['B']
    tB_from_Inf = round(student.ppf(1 - (1.0 - B) / 2, 10000), 4)
    delta_X = error / 3 * tB_from_Inf
    epsilon = delta_X / average * 100
    return {
        'result': average,
        'error': delta_X,
        'epsilon': epsilon,
        'B': B
    }


def evaluate_average_result(experiment: {sympy.Symbol: ([float], float)},
                            variable: sympy.Symbol,
                            settings: {str: float}):
    res = experiment[variable]
    if len(res[0]) == 1:
        return short_evaluate_average(res, variable, settings)
    else:
        return long_evaluate_average(res, variable, settings)


def evaluate_partial_error(formula: sympy.Expr,
                           variable: sympy.Symbol,
                           values: {sympy.Symbol: float},
                           avg_results: {sympy.Symbol: {str: float}}):
    differential = formula.diff(variable).evalf(subs=values)
    return differential * avg_results[variable]['error']

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


def evaluate(formulas: [(str, sympy.Expr)],
             experiments: [{sympy.Symbol: ([float], float)}],
             constants: {sympy.Symbol: float},
             settings: {str: float}):
    return [evaluate_experiment(formulas, experiment, constants, settings) for experiment in experiments]


def main():
    phi = sympy.symbols('phi')
    R = sympy.symbols('R')
    I = sympy.symbols('I')
    n = sympy.symbols('n')
    mu = sympy.symbols('mu')

    B = (mu * n * I) / (2 * R * sympy.tan(phi))
    formulas = [('B', B)]

    experiments = [
        {I: ([1], 0.025),
         phi: ([math.radians(22), math.radians(24)], math.radians(1)),
         R: ([0.18], 0.005)}
    ]

    constants = {
        n: 3,
        mu: 12.57e-7
    }

    settings = {
        'B': 0.95
    }
    print(evaluate(formulas, experiments, constants, settings))


if __name__ == '__main__':
    main()