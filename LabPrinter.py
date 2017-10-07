import sympy
import io

# Used to round to N significant digits
def round_to_n(x, n):
    string = ("%." + str(n-1) + "e") % x
    return float(string)


def print_short_direct_measurement(doc, variable: sympy.Symbol, measurement):
    doc.write((r'\( %s_{av}=%s \)' % (sympy.latex(variable), measurement['result'])))
    doc.write('\n\n')

    doc.write((r'\( \delta_{%s}=%s \)' % (format(variable), measurement['measurement_error'])))
    doc.write('\n\n')

    doc.write((r'\( {\beta}=%s \) \( t_{\beta}(\infty)=%s\)' % (
        measurement['distrib']['B'], measurement['distrib']['tB_Inf']
    )))
    doc.write('\n\n')

    doc.write((r'\( \Delta %s=\frac{\delta %s}{3}*t_{\beta}(\infty)=\frac{%s}{3}*%s=%s \)' % (
        sympy.latex(variable), sympy.latex(variable),
        measurement['measurement_error'],
        measurement['distrib']['tB_Inf'],
        measurement['error']
    )))
    doc.write('\n\n')

    doc.write((r'\( \varepsilon=\frac{\Delta %s}{%s_{av}}*100\%%=\frac{%s}{%s}*100\%%=%s\%% \)' % (
        sympy.latex(variable), sympy.latex(variable),
        measurement['error'], measurement['result'],
        measurement['epsilon']
    )))
    doc.write('\n\n')

    doc.write((r'\( %s=(%s \pm %s) \) \( \varepsilon=%s\%% \) on \( {\beta}=%s \)' % (
        sympy.latex(variable),
        measurement['result'], measurement['error'],
        measurement['epsilon'], measurement['distrib']['B']
    )))


def print_long_direct_measurement(doc, variable: sympy.Symbol, measurement):
    variable_latex = sympy.latex(variable)
    doc.write((r'\( %s_{av}=\frac{1}{n}\displaystyle\sum_{i=1}^{n} %s_{i}=\frac{' % (
        variable_latex, variable_latex
    )))
    meas = measurement['measurements']
    for index, source_val in enumerate(meas):
        doc.write(str(source_val))
        if index + 1 < len(meas):
            doc.write('+')
    doc.write((r'}{%s}=\frac{%s}{%s}=%s \)' % (len(meas),
                                             format(sum(meas)),
                                             format(len(meas)),
                                             format(measurement['result']))))
    doc.write('\n\n')

    doc.write((r'\( S_{%s}=\sqrt{\frac{\displaystyle\sum_{i=1}^{n} (%s_{i} - %s_{av})^2}{n*(n-1)}}=\sqrt{\frac{' % (
        variable_latex, variable_latex, variable_latex
    )))
    for index, source_val in enumerate(meas):
        doc.write(('%s^2' % (source_val - measurement['result'])))
        if index + 1 < len(meas):
            doc.write('+')
    doc.write(('}{%s*%s}}=%s \)' % (
        len(meas), len(meas) - 1, measurement['S']
    )))
    doc.write('\n\n')

    distrib = measurement['distrib']
    doc.write((r'\( {\beta}=%s \) \( t_{\beta}(%s)=%s \) \( t_{\beta}(\infty)=%s\)' % (
        distrib['B'], len(meas), distrib['tB_N'], distrib['tB_Inf']
    )))
    doc.write('\n\n')

    doc.write((r'\( \Delta %s_{S}=S_{%s}*t_{\beta}(n)=%s*%s=%s \)' % (
        variable_latex, variable_latex,
        measurement['S'], distrib['tB_N'], measurement['delta']['XS']
    )))
    doc.write('\n\n')

    doc.write((r'\( \Delta %s_{\delta}=\frac{\delta %s}{3}*t_{\beta}(\infty)=\frac{%s}{3}*%s=%s \)' % (
        variable_latex, variable_latex,
        measurement['measurement_error'], distrib['tB_Inf'],
        measurement['delta']['XD']
    )))
    doc.write('\n\n')

    delta_Xs = measurement['delta']['XS']
    delta_Xd = measurement['delta']['XD']
    delta_X = measurement['error']
    if delta_Xs > 3 * delta_Xd:
        doc.write((r'\( \Delta %s_{S}>3*\Delta %s_{\delta} \Rightarrow \Delta %s=\Delta %s_{S}=%s \)' % (
            variable_latex, variable_latex,
            variable_latex, variable_latex,
            delta_X
        )))
    elif delta_Xd > 3 * delta_Xs:
        doc.write((r'\( \Delta %s_{\delta}>3*\Delta %s_{S} \Rightarrow \Delta %s=\Delta %s_{\delta}=%s \)' % (
            variable_latex, variable_latex,
            format(variable), variable_latex,
            delta_X
        )))
    else:
        doc.write((r'\( \Delta %s=\sqrt{%s_{S}^2+%s_{\delta}^2}=\sqrt{%s^2+%s^2}=%s \)' % (
            variable_latex, variable_latex, variable_latex,
            delta_Xs, delta_Xd, delta_X
        )))
    doc.write('\n\n')

    doc.write((r'\( \varepsilon=\frac{\Delta %s}{%s_{av}}*100\%%=\frac{%s}{%s}*100\%%=%s\%% \)' % (
        variable_latex, variable_latex,
        delta_X, measurement['result'],
        measurement['epsilon']
    )))
    doc.write('\n\n')

    doc.write((r'\( %s=(%s \pm %s) \) \( \varepsilon=%s\%% \) on \( {\beta}=%s \)' % (
        sympy.latex(variable),
        measurement['result'], delta_X,
        measurement['epsilon'], distrib['B']
    )))


def print_direct_measurements(doc, measurements: dict):
    for variable in measurements.keys():
        doc.write((r'\subsubsection{Calculating \( %s \)}' % sympy.latex(variable)))
        doc.write('\n\n')
        doc.write('\( \)')
        doc.write('\n\n')
        measurement = measurements[variable]
        if measurement['type'] == 'short':
            print_short_direct_measurement(doc, variable, measurement)
        else:
            print_long_direct_measurement(doc, variable, measurement)


def print_formula(doc, formula: str, experiment: dict, common: dict):
    rnd = lambda x: round_to_n(x, experiment['round']) if 'round' in experiment else x
    result = experiment['formulas'][formula]
    doc.write((r'\( %s=%s \)' % (sympy.latex(formula), sympy.latex(result['formula']))))
    doc.write('\n\n')

    for diff in result['differentials']:
        doc.write((r'\( \Delta %s_{%s}=\frac{\delta %s}{\delta %s}*\Delta %s=%s*%s=%s*%s=%s \)' % (
            sympy.latex(formula), sympy.latex(diff['symbol']),
            sympy.latex(formula), sympy.latex(diff['symbol']),
            sympy.latex(diff['symbol']),
            sympy.latex(diff['differential']),
            experiment['average'][diff['symbol']]['error'] if diff['symbol'] in experiment['average'] \
                else common[diff['symbol']]['error'],
            diff['differential_value'],
            experiment['average'][diff['symbol']]['result'] if diff['symbol'] in experiment['average'] \
                else common[diff['symbol']]['result'],
            diff['result']
        )))
        doc.write('\n\n')

    src = '\( \Delta %s=\sqrt{' % sympy.latex(formula)
    for index, diff in enumerate(result['differentials']):
        src += '\Delta %s_{%s}^2' % (
            sympy.latex(formula), sympy.latex(diff['symbol'])
        )
        if index + 1 < len(result['differentials']):
            src += '+'
    src += '}=\sqrt{'
    for index, diff in enumerate(result['differentials']):
        src += '%s' % (
            rnd(diff['result']**2)
        )
        if index + 1 < len(result['differentials']):
            src += '+'
    src += '}=%s \)' % result['delta']

    doc.write((src))
    doc.write('\n\n')

    doc.write((r'\( \varepsilon=\frac{\Delta %s}{%s_{av}}*100\%%=\frac{%s}{%s}*100\%%=%s\%% \)' % (
        sympy.latex(formula), sympy.latex(formula),
        result['delta'], result['result'],
        result['epsilon']
    )))
    doc.write('\n\n')

    doc.write((r'\( %s=(%s \pm %s) \) \( \varepsilon=%s\%% \) on \( {\beta}=%s \)' % (
        sympy.latex(formula),
        result['result'], result['delta'],
        result['epsilon'], result['B']
    )))


def print_indirect_measurements(doc, experiment: dict, common: dict):
    for formula in experiment['formulas'].keys():
        doc.write('\subsubsection{Calculating \( %s \)}' % formula)
        doc.write('\n\n')
        doc.write('\( \)')
        doc.write('\n\n')
        print_formula(doc, formula, experiment,common)


def print_measurement_data(doc, experiment: dict, common: dict, constants: dict):
    for variable in common.keys():
        doc.write((r'\( %s=%s \pm %s \)' % (
            sympy.latex(variable),
            common[variable]['result'],
            common[variable]['measurement_error']
        )))
        doc.write('\n\n')

    for variable in experiment['average'].keys():
        doc.write((r'\( %s=%s \pm %s \)' % (
            sympy.latex(variable),
            experiment['average'][variable]['result'],
            experiment['average'][variable]['measurement_error']
        )))
        doc.write('\n\n')

    for variable in constants.keys():
        doc.write((r'\( %s=%s \)' % (
            sympy.latex(variable),
            constants[variable]
        )))
        doc.write('\n\n')

def print_experiment(doc, experiment: dict, common: dict, constants: dict):
    doc.write('\n\n')
    doc.write(r'\section{Experiment}')
    doc.write('\n\n')
    doc.write(r'\subsection{Measurement data and constants}')
    doc.write('\n\n')
    doc.write('\( \)')
    doc.write('\n\n')
    print_measurement_data(doc, experiment, common, constants)
    doc.write(r'\subsection{Direct measurements}')
    doc.write('\n\n')
    print_direct_measurements(doc, experiment['average'])
    doc.write(r'\subsection{Indirect measurements}')
    doc.write('\n\n')
    doc.write('\( \)')
    doc.write('\n\n')
    print_indirect_measurements(doc, experiment, common)


def print_common_measurements(doc, results: dict):
    doc.write('\section{Common}')
    doc.write('\n\n')
    doc.write('\subsection{Direct measurements}')
    doc.write('\n\n')
    print_direct_measurements(doc, results['common'])

def print_lab(results: dict, output = None):
    if output is None:
        output = io.StringIO()
        retout =  True
    else:
        retout = False
    output.write(r'\documentclass{article}')
    output.write('\n\n')
    output.write(r'\begin{document}')
    output.write('\n\n')
    print_common_measurements(output, results)
    for experiment in results['result']:
        print_experiment(output, experiment, results['common'], results['constants'])
    output.write('\n\n')
    output.write(r'\end{document}')
    if retout:
        return output.getvalue()