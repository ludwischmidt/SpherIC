# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: darknanograv
#     language: python
#     name: darknanograv
# ---

# %% [markdown]
# # run_spheric
#
# This file represents a notebook/script used to run and test spheric.
#
# Note that this notebook has been paired with a python script file in the `percent` format using `jupytext`.  Use that file for comparing revisions. See [Collaborating on notebooks with git](https://github.com/mwouts/jupytext#collaborating-on-notebooks-with-git) for more details.

# %% [markdown]
# # SpherIC documentation

# %% [markdown]
# So far, the only documentation for SpherIC beyond the [original paper](https://arxiv.org/abs/1301.3137) appears to be in-code comments and the CLI help menu (Note the nonstandard `-help` and `-version` options are not mentioned). These have been duplicated here:
#
# ```
# -halo               : generate a dark matter halo
# -Nhalo <value>      : number of halo particles
# -Mhalo <value>      : total mass of the halo (default Mhalo = 1)
# -a <value>          : alpha parameter in the halo density profile
# -b <value>          : beta parameter in the halo density profile
# -c <value>          : gamma parameter in the halo density profile
# -rs <value>         : scale radius (default rs = 1)
# -rcutoff <value>    : cutoff radius for cutoff halo models (i.e. beta >= 3)
# -king               : generate a stellar component with a King profile
# -hernquist          : generate a stellar component with a Hernquist profile
# -plummer            : generate a stellar component with a Plummer profile
# -Nstar <value>      : number of star particles
# -Mstar <value>      : total stellar mass 
# -rc <value>         : king core radius
# -rt <value>         : king tidal radius
# -rhern <value>      : scale radius for Hernquist profile
# -rp <value>         : scale radius for Plummer profile
# -MBH <value>        : mass of black hole (default MBH = 0)
# -name <value>       : name of the output file
# -dx/dy/dz <value>   : position offset for the initial conditions (default All = 0)
# -dvx/dvy/dvz <value>: velocity offset for the initial conditions (default All = 0)
# -ogr                : set this flag for outputting grid in r in an ASCII file
# -ogdf               : set this flag for outputting grid for distribution function in an ASCII file
# -ogb                : set this flag for generating a GADGET2 initial conditions binary file
# -ogh                : set this flag for generating a GIZMO initial conditions HDF5 file
# -otb                : set this flag for generating a TIPSY initial conditions binary file
# -oift               : set this flag to write positions for IFRIT binary file 
# -opfs               : set this flag to write a table of density profiles in an ASCII file
# -nostarpot          : set this flag for excluding the stellar potential 
# -randomseed <value> : set this flag for setting a value for a random seed (default: random value)
# -dorvirexact        : set this flag for calculating rvir exactly via N^2 sum - Warning: time consuming for large N!
# ```
#
# From running and code analysis, I think the `rs` parameter actually defaults to `-1` aka no default.

# %% [markdown]
# # Imports

# %%
import numpy as np
import subprocess
from pathlib import Path

# %% [markdown]
# # Definitions

# %%

# %% [markdown]
# ## Options class

# %%
import inspect
import numbers

class SphericOptions:
    halo = True        # generate a dark matter halo
    Nhalo = 1e5        # number of halo particles
    Mhalo = 1          # total mass of the halo (default Mhalo = 1)
    alpha = 1          # alpha parameter in the halo density profile
    beta = 3           # beta parameter in the halo density profile
    gamma = 1          # gamma parameter in the halo density profile
    rs = 1             # scale radius (default rs = 1)
    rcutoff = 100      # cutoff radius for cutoff halo models (i.e. beta >= 3)
    king = False       # generate a stellar component with a King profile
    hernquist = False  # generate a stellar component with a Hernquist profile
    plummer = False    # generate a stellar component with a Plummer profile
    Nstar = 0          # number of star particles
    Mstar = 0          # total stellar mass 
    rc = np.nan        # king core radius
    rt = np.nan        # king tidal radius
    rhern = np.nan     # scale radius for Hernquist profile
    rp = np.nan        # scale radius for Plummer profile
    MBH = 0            # mass of black hole (default MBH = 0)
    name = ""          # name of the output file
    dx,dy,dz = 0,0,0   # position offset for the initial conditions (default All = 0)
    dvx,dvy,dvz = 0,0,0# velocity offset for the initial conditions (default All = 0)
    ogr = False        # set this flag for outputting grid in r in an ASCII file
    ogdf = False       # set this flag for outputting grid for distribution function in an ASCII file
    ogb = False        # set this flag for generating a GADGET2 initial conditions binary file
    ogh = False        # set this flag for generating a GIZMO initial conditions HDF5 file
    otb = False        # set this flag for generating a TIPSY initial conditions binary file
    oift = False       # set this flag to write positions for IFRIT binary file 
    opfs = False       # set this flag to write a table of density profiles in an ASCII file
    nostarpot = False  # set this flag for excluding the stellar potential 
    randomseed = -1     # set this flag for setting a value for a random seed (default: random value)
    dorvirexact = False# set this flag for calculating rvir exactly via N^2 sum - Warning: time consuming for large N!
    
    
    def __init__(self,*,name=None,randomseed=-1,**kwargs):
        if name is None:
            name = "runs/IC"
        self.name = name
        self.randomseed = randomseed
        self.__dict__.update(kwargs)
        if self.Nstar < 1:
            self.Mstar = 0

    def generateOptionString(self):
        # Determine attributes programmatically since maybe options will change in future
        # Code pulled from https://stackoverflow.com/a/9058322
        attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a)))
        attributes = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]
        optStr = ""
        for a in attributes:
            match a:
                case (_,bool()):
                    if a[1]:
                        optStr = optStr + f"-{a[0]} "
                case ("a"|"alpha",x):
                    optStr = optStr + f"-a {a[1]} "
                case ("b"|"beta",x):
                    optStr = optStr + f"-b {a[1]} "
                case ("c"|"gamma",x):
                    optStr = optStr + f"-c {a[1]} "
                case ("Mhalo",1):
                    pass
                case ("randomseed", -1):
                    pass
                case (("MBH"|"Nstar"|"Mstar"|"dx"|"dy"|"dz"|"dvx"|"dvy"|"dvz"),0): # Deal with default 0 values
                    pass
                case (_,numbers.Number()):
                    if not np.isnan(a[1]):
                        optStr = optStr + f"-{a[0]} {a[1]} "
                case _:
                    optStr = optStr + f"-{a[0]} {a[1]} "
        return optStr


# %% [markdown]
#

# %%

# %%

# %%

# %% [markdown]
# ## Run spheric

# %%
def spheric(opts=None):
    if opts is None:
        opts = SphericOptions()
    cmd = "./spheric"
    args = opts.generateOptionString()
    p = subprocess.run([cmd,*args.split()],capture_output=True)
    if p.returncode:
        return None
    # This generates a filename called {opts.name}.out which is a text file. We'll change it to {opts.name}_out.txt
    Path(f"{opts.name}.out").rename(f"{opts.name}_out.txt")
    print(f"Changing filename {opts.name}.out to {opts.name}_out.txt")
    return p


# %% [markdown]
# # Testing

# %% [markdown]
# ## Generate test file

# %%
so = SphericOptions(MBH=10,dx=-5,ogb=True,Nhalo=1e4,ogh=True)
print(f"Using spheric options: {so.generateOptionString()}")
comproc = spheric(so)
print(comproc.stderr.decode())

# %% [markdown]
# ## Load in IC file using yt

# %%
import yt

ic = yt.load("runs/IC-gizmo.hdf5")

# %%
import matplotlib as mpl
import matplotlib.pyplot as plt

ad = ic.all_data()
x = ad["PartType1","particle_position_x"]
y = ad["PartType1","particle_position_y"]
z = ad["PartType1","particle_position_z"]

try:
    sx = ad["PartType4","particle_position_x"]
    sy = ad["PartType4","particle_position_y"]
    sz = ad["PartType4","particle_position_z"]
except:
    sx = None
    sy = None
    sz = None

try:
    bhx = ad["PartType5","particle_position_x"]
    bhy = ad["PartType5","particle_position_y"]
    bhz = ad["PartType5","particle_position_z"]
except:
    bhx = None
    bhy = None
    bhz = None

fig = plt.figure(figsize=(12,3))
ax = fig.add_subplot(1,3,1)
ax.plot(x,y,'.')
if sx is not None:
    ax.plot(sx,sy,'.')
if bhx is not None:
    ax.plot(bhx,bhy,'.')
ax.set_xlabel("x")
ax.set_ylabel("y")
ax = fig.add_subplot(1,3,2)
ax.plot(x,z,'.')
if sx is not None:
    ax.plot(sx,sz,'.')
if bhx is not None:
    ax.plot(bhx,bhy,'.')
ax.set_xlabel("x")
ax.set_ylabel("z")
ax = fig.add_subplot(1,3,3)
ax.plot(z,y,'.')
if sx is not None:
    ax.plot(sz,sy,'.')
if bhx is not None:
    ax.plot(bhx,bhy,'.')
ax.set_xlabel("z")
ax.set_ylabel("y")
fig.subplots_adjust(wspace=0.4)

# %%
print(ad.quantities.center_of_mass(use_gas=False,use_particles=True))
print(ad.quantities.center_of_mass(use_gas=False,use_particles=True,particle_type="PartType1"))
ad["PartType5","Coordinates"]

# %%

# %%
