# Introduction
This repository corresponds to a High Energy Physics project, which is based on the DarkMachines initiative. The project aims the development of new Machine Learning techniques in the context of event classification for which the DarkMachines dataset is used in order to compare with existing techniques that have already been tested.

DarkMachines challenge: https://arxiv.org/abs/2105.14027

The new techniques to be used are called Transformers and Graph Neural Networks, which have shown an incredible performance in other areas of Particle Physics such as jet-tagging. The code to be used can be found in this repository: https://github.com/jet-universe/particle_transformer

The codes found here allow these algorithm to be fed by the DarkMachines datasets, which is originally in csv format. The workflow consists of 2 steps:
1. Convert csv files into ROOT ntuples using just low-level variables.
2. Define higher level variables and apply a particular pre-selection in order to obtain lighter ntuples.

# Set up
In order to run this code in the IFIC machines, the required setup is inside the `setup.sh` bash script.

`source setup.sh`

This only runs the basic ATLAS and ROOT (6.18.04) setting up.