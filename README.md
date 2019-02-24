# N3XT Energy-Delay Model
This script takes the output of a general-purpose zsim architectural simulation (an HDF5 file), and outputs energy and execution time (delay) statistics based on a provided configuration.

`parse.py` is the main program. It imports ``TechConfig.py``, where the energy characteristics are defined.

To use it, run:

``parse.py <zsim-output.h5>``

## zsim output files
You may have noticed that zsim actually generates multiple ``.h5`` files; among these are ``zsim.h5`` and ``zsim-ev.h5``. The difference between the two is that ``zsim.h5`` contains periodic stats taken throughout the simulation, while ``zsim-ev.h5`` contains only stats taken upon the simulation's completion (e.g., the final row of ``zsim.h5``).

Thus, supplying ``zsim-ev.h5`` to `parse.py` will result in somewhat faster parsing + processing. (``parse.py`` always uses only the final row in each file.)

## Troubleshooting
If you run into issues, ensure that the configuration specified in `TechConfig.py` matches that of the zsim configuration (e.g., same number of cores, number/configuration of cache levels, etc.)
