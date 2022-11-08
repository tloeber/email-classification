This directory includes additional files needed to run everything locally for easier debugging and quicker iteration.

# Environment files:
Note: Unfortunately, the conda environment files are platform-dependent, because there does not seem to be a way to separate explicitly installed packages from all installed packages (as Pipenv does). While "conda list" has the "--from-history" option, it does not include packages installed with pip. 

(Thus, a good option is to try avoiding pip if possible, but for the packages needed here this did not work.)
