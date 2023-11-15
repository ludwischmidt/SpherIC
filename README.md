# Readme

This is a basic Readme for the SpherIC package. This version of SpherIC
contains edits by Michael Ryan (mryan4@uci.edu). 

For SpherIC documentation, see doc/spherIC.pdf.

# Primary edits
1. Added gizmo hdf5 output (using the `-ogh` flag). If `MBH`>0, this will 
	include a central Black Hole (as `PartType5` particle). Since the gadget
	binary file does not include one, this will lead to a difference in the
	initial particle velocities seen by GIZMO (as seen by comparing 
	snapshot_000).
2. Black hole particle affected by translation (the `-dx/dy/dz` and 
	`-dvx/dvy/dvz` arguments)
3. Fixed gadget binary not being written under certain compilers due to 
	improper use of assert

**WARNING**: The gizmo output does not currently support the `-nostarpot`
option.

# Compiling Notes
Since we now include hdf5 output, the hdf5 libraries need to be included. This
has been accomplished by switching the default compiler from gcc to h5cc. 

Note that depending on your compiler (for example, the version of `gcc` 
provided in conda), the `assert(expression)` statement may or may not actually
run `expression`. Since much of the output files were written using 
`assert(fwrite(...) == # of writes)`, this can result in SpherIC writing 0-byte
output files. This has been "fixed" for the gadget binary output and is not an
issue for the gizmo output, but does still affect e.g. the ascii output. 
