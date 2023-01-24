## Preprocessing created ntuples from DarkMachines
## -- "channel 1" specified in DarkMachines paper applied to create light ntuples
## -- Directories structure in the appropriate way
## Need to coincide with format required by Partucle_transformer code


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

#process_csv = {
#                 'ttbar' : 'ttbar_10fb.root',
#                 'Zjets' : 'z_jets_10fb.root',
#                 #'ttH'   : 'ttbarHiggs_10fb.root'
#                 'wtop' : 'wtop_10fb.root'
#}

INPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/fullStats/'
OUTPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/channel1/'

def passSelection(variables):
    # Channel 1
    if variables['HT'][0]<600.: return False
    if variables['MET'][0]<200.: return False
    if variables['MET'][0]/variables['HT'][0]<0.2: return False
    #print(variables['tlv_j'].at(0))
    if (len(variables['tlv_j'])+len(variables['tlv_b']))<4: return False
    if variables['tlv_j'].at(0).Pt()<200. and variables['tlv_b'].at(0).Pt()<200.: return False
    return True

def main():

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p","--process", dest="process", help="Comma-separated list of the processes to run")
    parser.add_option("-l","--labels", dest="labels", default="", help="Comma-separated list of the processes to associate a label")
    (options, sys.argv[1:]) = parser.parse_args(sys.argv[1:])
    
    process = options.process

    # Open TFile
    f = TFile.Open(INPUT_PATH+process_csv[process].replace('.csv','.root'), "READ")
    # Read tree
    tree = f.Get("mytree")
    list_branches = [key.GetName() for key in tree.GetListOfBranches()]
    variables = {}
    for v in sorted(list_branches):

        if 'tlv' in v:
            variables[v] = ROOT.std.vector(ROOT.Math.PtEtaPhiEVector)()
            tree.SetBranchAddress(v, variables[v])
        else:
            if "VecOps" in vartype[v]:
                if "int" in str(vartype[v]):
                    variables[v] = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))()
                    tree.SetBranchAddress(v,variables[v])
                if "float" in str(vartype[v]):
                    variables[v] = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))()
                    tree.SetBranchAddress(v,variables[v])
            else:
                if vartype[v]=='int':
                    variables[v] = array('i',[0])
                    tree.SetBranchAddress(v,variables[v])
                if vartype[v]=='float':
                    variables[v] = array('f',[0.])
                    tree.SetBranchAddress(v,variables[v])
    
    # Apply selection 
    var = {}
    i=0
    # Start of time monitoring
    start = time.time()
    t = 0
    for n in range(0,tree.GetEntries()):
        # Set monitoring time
        if (time.time()-start) > t:
            print("Reading during more than %s minutes..." % (t/60))
            t+=300
        if n%100000==0: print('Event ' +str(n))

        tree.GetEntry(n)
        if not passSelection(variables): continue
        var[i]={}
        for v in sorted(list_branches):
            
            if 'tlv' in v:
                var[i][v] = ROOT.std.vector(ROOT.Math.PtEtaPhiEVector)()
            else:
                if "VecOps" in vartype[v]:
                    if "int" in str(vartype[v]):
                        var[i][v] = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))()
                    if "float" in str(vartype[v]):
                        var[i][v] = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))()
                    for x in variables[v]: var[i][v].push_back(x)
                else:
                    if vartype[v]=='int':
                        var[i][v] = array('i',[0])
                    if vartype[v]=='float':
                        var[i][v] = array('f',[0.])

                    var[i][v] = variables[v][0]
                    #print(v)
                    #print(variables[v][0])
                    #print(var[i][v])
    
                
        i+=1
        #if i>900: break

    # Select only variable useful for training
    var_light = {}
    for i in range(0,len(var)):
        var_light[i] = {}
        for v in sorted(list_branches):
            if 'tlv' not in v: var_light[i][v] = var[i][v]

        # Define additional variables for the training
        ## Labeling each process
        #for l in sorted(process_csv):
        #    if l[-1].isdigit(): continue
        #    var_light[i]['label_%s' % l] = labels(process, l)
        ## Labeling signal and bkg
        if ('susy' in process) or ('gluino' in process):
            var_light[i]['label_background'] = int(0)
            var_light[i]['label_signal'] = int(1)
        else:
            var_light[i]['label_background'] = int(1)
            var_light[i]['label_signal'] = int(0)

    # Writing acceptance info
    nevents = len(var_light)
    acceptance_path = '/lhome/ific/a/adruji/DarkMachines/DataPreparation/acceptance/'
    with open('%s/%s_acceptance.csv' % (acceptance_path,process), 'w+') as csv:
        csv.write('Process,Events,PassedEvents,Acceptance\n')
        csv.write('%s,%d,%d,%s\n' % (process,int(tree.GetEntries()),nevents,float(nevents)/float(tree.GetEntries())))

    # Create fullStats folder if it does not exist
    if not os.path.exists(OUTPUT_PATH+'fullStats/'):
        print("Creating folder for fullStats ...")
        os.makedirs(OUTPUT_PATH+'fullStats/')

    # Write tree with full statistics
    treename = 'tree'
    load(var_light,OUTPUT_PATH+'fullStats/'+process_csv[process].replace('.csv','.root'),treename)

    # Create folders for final ntuples: train, val, test folders
    folders = ['train','val','test']
    for folder in folders:
        if not os.path.exists(OUTPUT_PATH+folder+'/'):
            print("Creating folder for %s samples..." % folder)
            os.makedirs(OUTPUT_PATH+folder+'/')
    
    # Create 3 different trees: train, val, test
    TRAIN_FRAC = 80./100.
    VAL_FRAC = 10./100.
    TEST_FRAC = 10./100.
    
    ## Split each train/val/test ntuples in 2 smaller ones
    split_number=2
    min_events_per_file = 10
    number_of_files = int(float(nevents)/float(min_events_per_file))
    
    if number_of_files < 2: 
        print( "THIS PROCESS HASS ONLY %d EVENTS IN TOTAL. NO SEVERAL NTUPLES CAN BE CREATED FROM IT" % nevents)
        split_number=1

    events_per_split = int(float(nevents)/float(split_number))

    # Print relevant numbers for the split
    print("--Print relevant numbers for the split--")
    print('nevents=%s' % str(nevents))
    print('split_number=%d' % split_number)
    print('events_per_split=%d' % events_per_split)
    print('events_per_split*TRAIN_FRAC=%d' % (int(events_per_split*TRAIN_FRAC)))
    print('events_per_split*VAL_FRAC=%d' % (int(events_per_split*VAL_FRAC)))
    print('events_per_split*TEST_FRAC=%d' % (int(events_per_split*TEST_FRAC)))

    for n in range(split_number):   
        start_event = n*events_per_split
        # Monitoring numbers
        print('split %d' % n)
        print('start_event=%d' %start_event)     

        # Filling dictionaries
        var_train = dict((k, var_light[start_event+k]) for k in range(0,int(events_per_split*TRAIN_FRAC)))
        var_val = dict((k, var_light[start_event+k+int(events_per_split*TRAIN_FRAC)]) for k in range(0,int(events_per_split*VAL_FRAC)))
        var_test = dict((k, var_light[start_event+k+int(events_per_split*TRAIN_FRAC)+int(events_per_split*VAL_FRAC)]) for k in range(0,int(events_per_split*TEST_FRAC)))

        # Create ntuple with n label
        load(var_train,OUTPUT_PATH+'train/'+process_csv[process].replace('.csv','_%s.root' % str(n)),treename)
        load(var_val,OUTPUT_PATH+'val/'+process_csv[process].replace('.csv','_%s.root' % str(n)),treename)
        load(var_test,OUTPUT_PATH+'test/'+process_csv[process].replace('.csv','_%s.root' % str(n)),treename)

    
    

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- Total of %s seconds ---" % (time.time() - start_time))