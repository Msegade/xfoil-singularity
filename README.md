# Uso

Build the container:

`sudo singularity build --sandbox xfoil.sif xfoil.def`

Execute the container:

`singularity exec xfoil.sif python pyXfoil.py <nacaXXXX> <Reynolds> <AoA>`
