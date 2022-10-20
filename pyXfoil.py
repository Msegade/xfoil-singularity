from pathlib import Path
from subprocess import run, DEVNULL, PIPE, TimeoutExpired
import pandas as pd
from time import sleep
import numpy as np
import typer
import sys 
import os

def safeIncArange(start, stop, step):
        values = np.arange(start, stop+step, step)
        # Check overflow in np.arange
        if step < 0:
            if values[-1] < stop: values = values[:-1]
        elif step > 0:
            if values[-1] > stop: values = values[:-1]
        return values

def  analyzeFailure(alphaValuesi, results):

    aoaR = np.array([float(r[0]) for r in results])
    alphaValuesi = np.around(alphaValuesi, 3)
    if len(alphaValuesi) == 1:
        print("Last element could not be calculated")
        # To stop iterating
        converged = True
        failedElement = None
        return converged, failedElement

    alphaInc = round((alphaValuesi[0]-alphaValuesi[1])*-1, 3)

    # If it did not manage to converge a single AoA
    if len(aoaR) == 0:
        converged = False
        failedElement = alphaValuesi[0] + alphaInc
        print("Not a single value converged")
        return converged, round(failedElement, 3)
        

    ni = len(aoaR) 
    n = len(alphaValuesi) 
    if ni != n:
        if aoaR[-1] != alphaValuesi[-1]:
            converged = False
            failedElement = float(results[-1][0]) + alphaInc
            failedElement = round(failedElement, 3)
            print("Stoped at an intermediate value")
        elif aoaR[-1] == alphaValuesi[-1]:
            #converged = False            
            #failedElements = alphaVlauesi[~np.in1d(alphaValuesi, aoaR)]
            converged = True
            failedElement = None
            print("Intermediate value missing")
    else:
        converged = True
        failedElement = None
        print("Converged")
        
    return converged, failedElement

def parseResultsSingleRun():

    resultsFile = Path.cwd() / 'results.txt'

    # Results start at line 13
    with resultsFile.open('r') as f:
        line = f.readlines()[-1].split()

    return line[0], line[1], line[2], line[4]

def runXfoil(naca, re, alpha):


    inputLines=f'''
    {naca}
    oper
    visc
    {re}
    pacc
    ./results.txt
    ./polar.dump
    iter 500
    aseq {alpha} 

    quit
    '''

    # Running xfoil with old files may cause error
    clean()

    child = run(['xfoil'], input=str.encode(inputLines), stdout=PIPE, 
                stderr=PIPE)
    

    # Xfoil does not return any code, parse the output to stdout
    # If it could not process any point raise exception here
    #if 'Point written to dump file' not in child.stdout.decode('utf-8'):
    #    raise ConvergenceError('First point Failed')

def runXfoilSeq(naca, re, alphaI, alphaE, alphaInc):

    print(f"Runinng: {alphaI}, {alphaE}, {alphaInc}")
    pid = os.getpid()
    inputLines=f'''
    plop 
    g f 

    {naca}
    oper
    visc
    {re}
    pacc
    ./results-{pid}.txt
    ./polar-{pid}.dump
    iter 100
    aseq {alphaI} {alphaE} {alphaInc}

    quit
    '''

    # Running xfoil with old files may cause error
    clean()
    try:
        child = run(['xfoil'], input=str.encode(inputLines), stdout=DEVNULL, 
                    stderr=DEVNULL, timeout=10.0)
    except TimeoutExpired:
        print("Xfoil hanged")
        pass

    resultsFile = Path.cwd() / f'results-{pid}.txt'

    # Results start at line 13
    with resultsFile.open('r') as f:
        lines = f.readlines()[12:]

    ## alpha    CL        CD       CDp       CM     Top_Xtr  Bot_Xtr  Top_Itr  Bot_Itr
    ## ------ -------- --------- --------- -------- -------- -------- -------- --------
    ## -1.000  -0.0562   1.59641   0.10485   0.0027   1.0000   1.0000   1.0000 160.0000
    results = []
    for line in lines:
        l = line.split()
        results.append([l[0], l[1], l[2], l[4]])

    alphaValuesi = safeIncArange(alphaI, alphaE, alphaInc)
    ni = len(alphaValuesi)
    n = len(results)

    converged, failedElement = analyzeFailure(alphaValuesi, results)

    return converged, failedElement, results

class XfoilResults:

    def __init__(self, naca, re, alphai, alphae, alphainc):

        self.alphaValues = safeIncArange(alphai, alphae, alphainc)
        self.naca = naca
        self.re = re
        self.alphai = alphai
        self.alphae = alphae
        self.alphainc = alphainc

        self.df = pd.DataFrame(columns  = ['AoA', 'Cl', 'Cd', 'Cm'], dtype=float)
        self.converged = False

    def append(self, results):

        df = pd.DataFrame(results, columns=['AoA', 'Cl', 'Cd', 'Cm'], dtype=float)
        self.df = pd.concat([self.df, df])
        self.df.sort_values('AoA', inplace=True)


    def iterateXfoil(self):

            # Left sweep
            converged = False
            alphaValues = self.alphaValues
            while not converged:
                alphai = round(alphaValues[0], 6)
                alphae = round(alphaValues[-1], 6)
                converged, failedElement, results = runXfoilSeq(self.naca, self.re, 
                                                    alphai, alphae, self.alphainc)
                if not converged:
                    alphaValues = safeIncArange(failedElement, alphae, self.alphainc)
                self.append(results)

            # Right sweep
            converged = False
            alphaValues = np.flip(self.alphaValues)
            while not converged:
                alphai = round(alphaValues[0], 6)
                alphae = round(alphaValues[-1], 6)
                converged, failedElement, results = runXfoilSeq(self.naca, self.re, 
                                                    alphai, alphae, -self.alphainc)
                if not converged:
                    alphaValues = safeIncArange(failedElement, alphae, -self.alphainc)
                self.append(results)

def clean():

    cwd = Path.cwd()
    pid = os.getpid()
    (cwd / f'results-{pid}.txt').unlink(missing_ok=True)
    (cwd / f'polar-{pid}.dump').unlink(missing_ok=True)
    (cwd / ':00.bl').unlink(missing_ok=True)


cmd = typer.Typer()

@cmd.command()
def range(naca: str, re: float, alphai: float, alphae: float, alphainc: float):


    xResults = XfoilResults(naca, re, alphai, alphae, alphainc)
    xResults.iterateXfoil()
    clean()
    xResults.df.drop_duplicates(subset='AoA', keep='last', inplace=True)
    xResults.df.to_csv(f'Re_{re:.0f}.csv', index=False)

@cmd.command()
def value(naca: str, re: float, alpha):

    runXfoil(naca, re, alpha)
    results = parseResultsSingleRun()
    clean()
    print(results)

if __name__ == '__main__':
    cmd()
