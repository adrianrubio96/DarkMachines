# Data preparation for Particle Transformers
This repository belongs to a High Energy Physics project, which is based on the DarkMachines initiative. The project aims the development of new Machine Learning techniques in the context of event classification for which the DarkMachines dataset is used in order to compare with existing techniques that have already been tested.

DarkMachines challenge: https://arxiv.org/abs/2105.14027

The new techniques to be used are called Transformers and Graph Neural Networks, which have shown an incredible performance in other areas of Particle Physics such as jet-tagging. The code to be used can be found in this repository: https://github.com/jet-universe/particle_transformer

The codes found here allow these algorithm to be fed by the DarkMachines datasets, which is originally in csv format. The workflow consists of 2 steps:
1. Convert csv files into ROOT ntuples using just low-level variables.
2. Apply a particular pre-selection in order to obtain lighter ntuples.

## Set up
In order to run this code in the IFIC machines, the required setup is inside the `setup.sh` bash script.
This only runs the basic ATLAS and ROOT (6.18.04) setting up.

## From CSV to ROOT ntuples

Run the command:
```
python DMcsv_to_ntuple.py -p ttbar -i /lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/linked_DarkMachines_input/ -v vX
```
where vX denotes the version of the ntuples (v0, v1, ...).

Since some of the backgrounds are very heavy, the longest csv files are already splitted (njets_10fb_01.csv, njets_10fb_02.csv, etc.) in the input directory. This is necessary for `multijets`, `gamjets`, `Zjets` and `Wjets`. On the contrary, the signal samples have already low statistics, so it would be convenient to merge them already with the `hadd` command.

## Light ntuples

In this step, the particular channel is specified by applying the preselection:
```
python preprocessing.py -p ttbar -v vXY -i /lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/vX/fullStats/
```
where now the version format requires two digits (X is the same as in the previous step and Y denotes the light version). The input path now is the output path of the following step. 

Two different outputs are created with this script. On one side, the full statistics passing the preselection for each of the files is saved in the subdirectory `channel1/vXY/fullStats/`. On the other side, the same files are saved by splitting them in train/val/test sets (80/10/10).

### Merging into signal vs background

Now that all files are light, we proceed to the merging of the files corresponding to the same process. Subsequently, all the files corresponding to background and signal will be merged into two files named `background_10fb.root` and `signal_10fb.root`. These final steps are done with the following command:
```
python signal_vs_background.py -i /lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/vX/fullStats/vXY/channel1/
```

This will create an output subdirectoy `channel1/vXY/signal_vs_bkg/` with the `train`, `val` and `test` sets, which contain the final ntuples to be read for the training.

Plots for the different input variables are obtained for each of the sets using the `plot_variables.py` script of the "[ROOTplotting repository](https://github.com/adrianrubio96/ROOTplotting/tree/DarkMachines)" (in the DarkMachines branch). 