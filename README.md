# Physics Lab Solver
This is simple lab solver that may be used to evaluate lab measurements.
See sample.json and sample.json.commented as lab definition sample.
You can print out result as Python dictionary on stdout or print TeX document
I wrote it to simplify university lab calculations.

Use:
```bash
python LabMain.py sample.json print # Prints lab evaluation final results
python LabMain.py sample.json tex # Prints TeX result to stdout
python LabMain.py sample.json somefile.tex # Print TeX result to 'somefile.txt'
```

### Author & License
Author: Jevgenijs Protopopovs

License: MIT License