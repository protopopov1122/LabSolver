# Copyright (c) 2017 Jevgenijs Protopopovs
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sympy
from sympy.parsing import sympy_parser
import json


def load_lab(path: str):
    with open(path) as fp:
        obj = json.load(fp)
    task = {
        'variables': dict(),
        'constants': dict(),
        'formulas': list(),
        'common': dict(),
        'measurements': list(),
        'symbols': dict(),
        'settings': {
            'B': 0.95,
            'extended': False
        }
    }
    for variable in obj['variables']:
        task['variables'][variable] = sympy.symbols(variable)
    for constant in obj['constants'].keys():
        if constant not in task['variables']:
            print('Unknown constant \'%s\'! Add it to variables section' % constant)
            return None
        task['constants'][task['variables'][constant]] = eval(str(obj['constants'][constant]))
    for formula in obj['formulas'].keys():
        task['formulas'].append((formula, sympy_parser.parse_expr(obj['formulas'][formula], local_dict=task['variables'])))
    for common in obj['common'].keys():
        if common not in task['variables']:
            print('Unknown variable \'%s\'! Add it to variables section' % common)
            return None
        cmn = obj['common'][common]
        task['common'][task['variables'][common]] = eval(str(cmn[0])), eval(str(cmn[1]))
    for experiment in obj['measurements']:
        expr = dict()
        for measurement in experiment:
            if measurement not in task['variables']:
                print('Unknown variable \'%s\'! Add it to variables section' % measurement)
                return None
            meas = experiment[measurement]
            eval_meas = []
            for m in meas[0]:
                eval_meas.append(eval(str(m)))
            expr[task['variables'][measurement]] = eval_meas, eval(str(meas[1]))
        task['measurements'].append(expr)
    if 'symbols' in obj:
        for symbol in obj['symbols'].keys():
            task['symbols'][symbol] = obj['symbols'][symbol]
    if 'settings' in obj:
        if 'B' in obj['settings']:
            task['settings']['B'] = obj['settings']['B']
        if 'round' in obj['settings']:
            task['settings']['round'] = obj['settings']['round']
        if 'extended' in obj['settings']:
            task['settings']['extended'] = obj['settings']['extended']
    return task