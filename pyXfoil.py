from pathlib import Path
from subprocess import run, DEVNULL, PIPE
import typer

class ConvergenceError(Exception):
    pass

def clean():

    cwd = Path.cwd()
    (cwd / 'results.txt').unlink(missing_ok=True)
    (cwd / 'polar.dump').unlink(missing_ok=True)
    (cwd / ':00.bl').unlink(missing_ok=True)

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
    a {alpha}

    quit
    '''

    # Running xfoil with old files may cause error
    clean()

    child = run(['xfoil'], input=str.encode(inputLines), stdout=DEVNULL, 
                stderr=PIPE)
    # Xfoil does not return any code, writes to stderr if it is not converged
    if child.stderr.decode('utf-8'):
        raise ConvergenceError

def parseResults():

    resultsFile = Path.cwd() / 'results.txt'

    with resultsFile.open('r') as f:
       line = f.readlines()[-1].split()

    # alpha CL CD CDp CM ...
    return line[1], line[2], line[4]


cmd = typer.Typer()

@cmd.command()
def main(naca: str, re: float, alpha: float):
    runXfoil(naca, re, alpha)
    cl, cd, cm = parseResults()
    clean()
    print(cl, cd, cm)

if __name__ == '__main__':
    cmd()
