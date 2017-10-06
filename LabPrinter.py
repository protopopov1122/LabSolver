import sympy
import pylatex
from pylatex.utils import NoEscape


def print_short_direct_measurement(doc: pylatex.Document, variable: sympy.Symbol, measurement):
    doc.append(NoEscape(r'\( %s_{vid}=%s \)' % (sympy.latex(variable), measurement['result'])))
    doc.append('\n')

    doc.append(NoEscape(r'\( \delta_{%s}=%s \)' % (format(variable), measurement['measurement_error'])))
    doc.append('\n')

    doc.append(NoEscape(r'\( {\beta}=%s \) \( t_{\beta}(\infty)=%s\)' % (
        measurement['distrib']['B'], measurement['distrib']['tB_Inf']
    )))
    doc.append('\n')

    doc.append(NoEscape(r'\( \Delta %s=\frac{\delta %s}{3}*t_{\beta}(\infty)=\frac{%s}{3}*%s=%s \)' % (
        sympy.latex(variable), sympy.latex(variable),
        measurement['measurement_error'],
        measurement['distrib']['tB_Inf'],
        measurement['error']
    )))
    doc.append('\n')

    doc.append(NoEscape(r'\( \varepsilon=\frac{\Delta %s}{%s_{vid}}*100\%%=\frac{%s}{%s}*100\%%=%s\%% \)' % (
        sympy.latex(variable), sympy.latex(variable),
        measurement['error'], measurement['result'],
        measurement['epsilon']
    )))
    doc.append('\n')

    doc.append(NoEscape(r'\( %s=(%s \pm %s) \) \( \varepsilon=%s\%% \) on \( {\beta}=%s \)' % (
        sympy.latex(variable),
        measurement['result'], measurement['error'],
        measurement['epsilon'], measurement['distrib']['B']
    )))


def print_long_direct_measurement(doc: pylatex.Document, variable: sympy.Symbol, measurement):
    print('%s %s' % (variable, measurement))
    variable_latex = sympy.latex(variable)
    doc.append(NoEscape(r'\( %s_{vid}=\frac{1}{n}\displaystyle\sum_{i=1}^{n} %s_{i}=\frac{' % (
        variable_latex, variable_latex
    )))
    meas = measurement['measurements']
    for index, source_val in enumerate(meas):
        doc.append(source_val)
        if index + 1 < len(meas):
            doc.append('+')
    doc.append(NoEscape(r'}{%s}=\frac{%s}{%s}=%s \)' % (len(meas),
                                             format(sum(meas)),
                                             format(len(meas)),
                                             format(measurement['result']))))
    doc.append('\n')

    doc.append(NoEscape(r'\( S_{%s}=\sqrt{\frac{\displaystyle\sum_{i=1}^{n} (%s_{i} - %s_{vid})^2}{n*(n-1)}}=\sqrt{\frac{' % (
        variable_latex, variable_latex, variable_latex
    )))
    for index, source_val in enumerate(meas):
        doc.append(NoEscape('%s^2' % (source_val - measurement['result'])))
        if index + 1 < len(meas):
            doc.append('+')
    doc.append(NoEscape('}{%s*%s}}=%s \)' % (
        len(meas), len(meas) - 1, measurement['S']
    )))
    doc.append('\n')

    distrib = measurement['distrib']
    doc.append(NoEscape(r'\( {\beta}=%s \) \( t_{\beta}(%s)=%s \) \( t_{\beta}(\infty)=%s\)' % (
        distrib['B'], len(meas), distrib['tB_N'], distrib['tB_Inf']
    )))
    doc.append('\n')

    doc.append(NoEscape(r'\( \Delta %s_{S}=S_{%s}*t_{\beta}(n)=%s*%s=%s \)' % (
        variable_latex, variable_latex,
        measurement['S'], distrib['tB_N'], measurement['delta']['XS']
    )))
    doc.append('\n')

    doc.append(NoEscape(r'\( \Delta %s_{\delta}=\frac{\delta %s}{3}*t_{\beta}(\infty)=\frac{%s}{3}*%s=%s \)' % (
        variable_latex, variable_latex,
        measurement['measurement_error'], distrib['tB_Inf'],
        measurement['delta']['XD']
    )))
    doc.append('\n')

    delta_Xs = measurement['delta']['XS']
    delta_Xd = measurement['delta']['XD']
    delta_X = measurement['error']
    if delta_Xs > 3 * delta_Xd:
        doc.append(NoEscape(r'\( \Delta %s_{S}>3*\Delta %s_{\delta} \Rightarrow \Delta %s=\Delta %s_{S}=%s \)' % (
            variable_latex, variable_latex,
            variable_latex, variable_latex,
            delta_X
        )))
    elif delta_Xd > 3 * delta_Xs:
        doc.append(NoEscape(r'\( \Delta %s_{\delta}>3*\Delta %s_{S} \Rightarrow \Delta %s=\Delta %s_{\delta}=%s \)' % (
            variable_latex, variable_latex,
            format(variable), variable_latex,
            delta_X
        )))
    else:
        doc.append(NoEscape(r'\( \Delta %s=\sqrt{%s_{S}^2+%s_{\delta}^2}=\sqrt{%s^2+%s^2}=%s \)' % (
            variable_latex, variable_latex, variable_latex,
            delta_Xs, delta_Xd, delta_X
        )))
    doc.append('\n')

    doc.append(NoEscape(r'\( \varepsilon=\frac{\Delta %s}{%s_{vid}}*100\%%=\frac{%s}{%s}*100\%%=%s\%% \)' % (
        variable_latex, variable_latex,
        delta_X, measurement['result'],
        measurement['epsilon']
    )))
    doc.append('\n')

    doc.append(NoEscape(r'\( %s=(%s \pm %s) \) \( \varepsilon=%s\%% \) pie \( {\beta}=%s \)' % (
        sympy.latex(variable),
        measurement['result'], delta_X,
        measurement['epsilon'], distrib['B']
    )))


def print_direct_measurements(doc: pylatex.Document, measurements: dict):
    for variable in measurements.keys():
        with doc.create(pylatex.Subsubsection(NoEscape(r'Calculating \( %s \)' % sympy.latex(variable)))):
            measurement = measurements[variable]
            if measurement['type'] == 'short':
                print_short_direct_measurement(doc, variable, measurement)
            else:
                print_long_direct_measurement(doc, variable, measurement)


def print_experiment(doc: pylatex.Document, experiment: dict):
    with doc.create(pylatex.Section('Experiment')):
        with doc.create(pylatex.Subsection('Direct measurements')):
            print_direct_measurements(doc, experiment['average'])
        with doc.create(pylatex.Subsection('Indirect measurements')):
            pass


def print_lab(results: list):
    doc = pylatex.Document('Report')
    for experiment in results:
        print_experiment(doc, experiment)
    doc.generate_pdf('/home/eugene/1.pdf')
    doc.generate_tex('/home/eugene/1.tex')