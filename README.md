# Uso

Build the container:

`sudo singularity build xfoil.def`

Calculate only one value:

`singularity exec xfoil.sif python pyXfoil.py value -- <nacaXXXX> <Reynolds> <AoA>`

Calculate for a range of values:

`singularity exec xfoil.sif python pyXfoil.py range -- <nacaXXXX> <Reynolds> <AoA-start> <AoA-stop> <AoA-step>`
