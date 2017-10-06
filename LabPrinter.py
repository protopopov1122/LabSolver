import sympy
import pylatex
from pylatex.utils import NoEscape


def print_short_direct_measurement(doc: pylatex.Document, variable: sympy.Symbol, measurement):
    print('%s %s' % (variable, measurement))
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