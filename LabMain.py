# Copyright (c) 2017 Jevgenijs Protopopovs
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Physics lab solver
#
# This script is able to process physics lab measurements
# and calculate some results and create report. Generally, results may be displayed
# in two different ways: simple structure and TeX document
# Use simple structure to view evaluation results or use
# TeX document to get full report. TeX document may be converted
# into PDF using online 'tex to pdf' services or LaTex package
#
# Run this file with two parameters:
#   1. path to JSON - see sample.json to understand its format
#   2. action:
#       * print - print raw result
#       * tex - print TeX to console
#       * path to file - save TeX to file
#
# Script is written on Python 3. Configure it before run.
# On Windows best way to get this work is using Python from Anaconda
# distribution
# On Linux just install sympy and scipy packages and run this script

import sys
from LabSolver import evaluate
from LabPrinter import print_lab
from LabLoader import load_lab


def main(path: str, action: str):
    task = load_lab(path)
    if task is None:
        return
    if action != 'print':
        task['settings']['extended'] = True
    result = evaluate(formulas=task['formulas'],
                      common_measurements=task['common'],
                      experiments=task['measurements'],
                      constants=task['constants'],
                      settings=task['settings'])
    if action == 'print':
        print(result)
    elif action == 'tex':
        print(print_lab(result))
    else:
        with open(action, 'w') as fp:
            print_lab(result, fp)
        print('Saved report to file \'%s\'. Now you may use any TeX to PDF converter to get PDF.' % action)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Pass input JSON and output TeX file as arguments!')
    else:
        main(sys.argv[1], sys.argv[2])