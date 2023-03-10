import ROOT
from ROOT import TLorentzVector as tlv
from ROOT import TFile,TTree
from ROOT import std

import csv
import numpy as np
from array import array
import sys, os
from utils.variables import *
from utils.utils import *

#INPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/v1/channel1/v10/'
#OUTPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/v1/channel1/v10/signal_vs_bkg/'


def main(): 

    # Parse the input arguments
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i","--input", dest="input", default="", help="Input path")

    # Read the input arguments
    (options, sys.argv[1:]) = parser.parse_args(sys.argv[1:])
    if options.input != "": INPUT_PATH = options.input

    # Define output path
    OUTPUT_PATH = INPUT_PATH+'signal_vs_bkg'

    # Create output directory
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    
    # Loop over train/val/test subdirs
    for dataset in ['train','val','test']:
        
        print("Processing %s dataset" % dataset)

        # Create a list to store the ntuple names
        bkg_ntuples_0 = []
        signal_ntuples_0 = []
        bkg_ntuples_1 = []
        signal_ntuples_1 = []

        # Loop over all root files in INPUT_PATH 
        for ntuple in os.listdir(os.path.join(INPUT_PATH, dataset)):

            # Skip ntuples corresponding to parallelisation of processes
            if sum(c.isdigit() for c in ntuple)==5: # 5 digits in the name: _10fb_XX_Y.root where XX indicates the parallelisation
                print('Skipping ntuple %s' % ntuple)
                continue
    
            # Open the root file 
            f = ROOT.TFile(os.path.join(INPUT_PATH, dataset, ntuple))
    
            # Check the TFile contains a TTree
            if not f.GetListOfKeys().Contains("tree"):
                print("For ntuple %s, TTree does not exist" % ntuple)
                continue

            #if 'Zp' in ntuple or 'gluino' in ntuple: continue
        
            # Access to its TTree 
            t = f.Get("tree")
    
            # Define variable to store values in
            label_signal = array('i',[0])
    
            # Loop over tree entries
            t.SetBranchAddress("label_signal", label_signal)
            print(ntuple)
            isOne = False
            for i in range(t.GetEntries()):
                t.GetEntry(i)
                # Get the value of the branch "label_signal" and decide if it is bkg or signal  
                if label_signal[0]==1:
                    isOne = True
                    signal_ntuples_0.append(ntuple) if '_0.root' in ntuple else signal_ntuples_1.append(ntuple)
                    break

            if not isOne:
                bkg_ntuples_0.append(ntuple) if '_0.root' in ntuple else bkg_ntuples_1.append(ntuple)
               
            f.Close()

        # Create output directory
        if not os.path.exists(OUTPUT_PATH+dataset+'/'):
            print("Creating folder for %s samples..." % dataset)
            os.makedirs(OUTPUT_PATH+dataset+'/')
            

        # Merge ntuples into background.root or signal.root ntuples

        os.system("hadd -f {0} {1}".format(os.path.join(OUTPUT_PATH+'/'+dataset, 'background_10fb_0.root'), " ".join([os.path.join(INPUT_PATH+'/'+dataset, bkg) for bkg in bkg_ntuples_0])))
        os.system("hadd -f {0} {1}".format(os.path.join(OUTPUT_PATH+'/'+dataset, 'background_10fb_1.root'), " ".join([os.path.join(INPUT_PATH+'/'+dataset, bkg) for bkg in bkg_ntuples_1])))
        os.system("hadd -f {0} {1}".format(os.path.join(OUTPUT_PATH+'/'+dataset, 'signal_10fb_0.root'), " ".join([os.path.join(INPUT_PATH+'/'+dataset, sig) for sig in signal_ntuples_0])))
        os.system("hadd -f {0} {1}".format(os.path.join(OUTPUT_PATH+'/'+dataset, 'signal_10fb_1.root'), " ".join([os.path.join(INPUT_PATH+'/'+dataset, sig) for sig in signal_ntuples_1])))
            

if __name__ == '__main__':
    main()
