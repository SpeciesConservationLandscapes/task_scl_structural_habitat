Species Conservation Landscapes structural habitat task
-------------------------------------------------------

Task for characterizing species habitat from a remote-sensing point of view, i.e. areas that look like 
good habitat for a species based on physical characteristics: vegetation height and land cover. 
Structural habitat output is the basis for calculating 
[effective potential habitat](https://github.com/SpeciesConservationLandscapes/task_scl_eff_pot_hab), 
which incorporates human impacts and species-specific patch size and dispersal distance parameters.

## Usage

*All parameters may be specified in the environment as well as the command line.*

```
/app # python task.py --help
usage: task.py [-h] [-d TASKDATE] [-s SPECIES] [--scenario SCENARIO] [--overwrite]

optional arguments:
  -h, --help            show this help message and exit
  -d TASKDATE, --taskdate TASKDATE
  -s SPECIES, --species SPECIES
  --scenario SCENARIO
  --overwrite           overwrite existing outputs instead of incrementing
```

### License
Copyright (C) 2022 Wildlife Conservation Society
The files in this repository  are part of the task framework for calculating 
Human Impact Index and Species Conservation Landscapes (https://github.com/SpeciesConservationLandscapes) 
and are released under the GPL license:
https://www.gnu.org/licenses/#GPL
See [LICENSE](./LICENSE) for details.
