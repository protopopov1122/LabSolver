import sympy
from sympy.parsing import sympy_parser


def parse_variables():
    raw = input('Define variable and constant names that you will use. Split them by spaces: ').split()
    vars = dict()
    for var in raw:
        vars[var] = sympy.symbols(var)
    return vars


def parse_constants(vars):
    print('Now define constant values. When finished press ENTER')
    cnsts = dict()
    while True:
        line = input('Enter constant and value(template is A=B): ')
        if not line:
            break
        raw = line.split('=')
        if len(raw) != 2:
            print('That is not a valid constant definition')
            continue
        name = raw[0]
        raw_value = raw[1]
        if name not in vars:
            print('I do not know constant \'%s\'. Possible names: %s' % (
                name,
                ', '.join(str(var) for var in vars.keys())
            ))
            continue
        else:
            try:
                cnsts[name] = float(raw_value)
            except:
                print('Enter valid floating point number!')
    return cnsts


def parse_formulas(vars):
    print('Define used formulas. When finished press ENTER')
    frms = []
    while True:
        line = input('Enter formula(template is A=B): ')
        if not line:
            break
        raw = line.split('=')
        if len(raw) != 2:
            print('That is not a formula!')
        name = raw[0].strip()
        try:
            form = sympy_parser.parse_expr(raw[1], local_dict=vars)
            frms.append((sympy.symbols(name), form))
        except:
            print('Formula parsing error')
    return frms

def parse_measurement(variables):
    try:
        line = input('Enter variable, measurements(divided by commas without spaces) and precision. '
                     'Split these by spaces: ')
        if not line:
            return None
        raw = line.split(' ')
        if len(raw) != 3:
            print('That is not a valid measurement!')
            return None, None, None
        raw_name = raw[0]
        raw_values = raw[1].split(',')
        raw_prec = raw[2]
        if raw_name not in variables:
            print('I do not know variable \'%s\'. Possible names: %s' % (
                raw_name,
                ', '.join(str(var) for var in variables.keys())
            ))
            return None, None, None
        values = [float(val) for val in raw_values]
        prec = float(raw_prec)
        return variables[raw_name], values, prec
    except:
        print('Enter valid floating-point numbers!')
        return None, None, None


def parse_measurements(vars):
    meas = dict()
    while True:
        ms = parse_measurement(vars)
        if ms is None:
            break
        elif ms[0] is not None:
            meas[ms[0]] = ms[1], ms[2]
    return meas


def parse_experiments(vars):
    print('Now enter experiment results')
    exps = []
    while True:
        rs = input('Do you want to enter %s experiment results[y/N]:' % (len(exps) + 1))
        if rs == 'y':
            print('Enter %s experiment results as a set of measurements' % (len(exps) + 1))
            res = parse_measurements(vars)
            exps.append(res)
        else:
            return exps


def parse_settings():
    settings = {
        'extended': False
    }
    try:
        line = input('Enter B value or press ENTER(by default it will be 0.95): ')
        if line:
            settings['B'] = float(line)
        else:
            settings['B'] = 0.95
    except:
        print('Entered value is invalid. Setting B to 0.95')
    try:
        line = input('Enter precision as significant digit count or press ENTER(by default it will be maximal): ')
        if line:
            settings['round'] = int(line)
    except:
        print('Entered value is invalid. Setting maximal precision')
    return settings


def parse():
    variables = parse_variables()
    constants = parse_constants(variables)
    formulas = parse_formulas(variables)
    print('Enter common measurements you performed only once for all experiments')
    common = parse_measurements(variables)
    exps = parse_experiments(variables)
    settings = parse_settings()
    return formulas, common, exps, constants, settings