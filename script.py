import numpy as np
from subprocess import run, PIPE
import pandas as pd 
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

#reynolds = np.logspace(4, 8, num=1000)
reynolds = np.arange(10000, 20000000, 10000)

def runReynolds(rey):
        rey = round(rey, 1)
        print(f'Calculating: Re = {rey}')
        arguments = ['range', '--', 'naca0010', str(rey), '-15.0', '15.0', '0.1']
        child = run(['singularity', 'exec', 'xfoil.sif', 'python', 'pyXfoil.py'] + arguments,
                    stdout = PIPE)

Parallel(n_jobs=2)(delayed(runReynolds)(rey) for rey in reynolds)

#aoas = np.linspace(-15.0, 15.0, 10)

#results = []
#for rey in reynolds:
#    for aoa in aoas:
#        print(f'Calculating: Re = {rey}, AoA = {aoa}')
#        arguments = ['--', 'naca0010', str(rey), str(aoa)]
#        child = run(['singularity', 'exec', 'xfoil.sif', 'python', 'pyXfoil.py'] + arguments,
#                    stdout = PIPE)
#        res = [float(b) for b in child.stdout.split()]
#        results.append([rey, aoa] + res)
#
#df = pd.DataFrame(results, columns=['Re', 'AoA', 'Cl', 'Cd', 'Cm'])
#df.to_csv('results.csv')
