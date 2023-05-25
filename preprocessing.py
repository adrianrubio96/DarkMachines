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


def passSelection(variables):
    # Channel 1
    if variables['HT'][0]<600.: return False
    if variables['MET'][0]<200.: return False
    if variables['MET'][0]/variables['HT'][0]<0.2: return False
    #print(variables['tlv_j'].at(0))
    # Checking if the leading jet or bjet have pT>200GeV
    if variables['tlv_j'].at(0).Pt()<200. and variables['tlv_b'].at(0).Pt()<200.: return False
    # Count jets with Pt>50GeV
    #Njets = sum([1 for value in variables['isJet'] if value==1])
    Njets = sum([1 for j in variables['tlv_j'] if j.Pt()>50.])
    Njets += sum([1 for b in variables['tlv_b'] if b.Pt()>50.])
    #print('Njets: ',Njets)
    if Njets<4: return False
    return True

def main():

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p","--process", dest="process", help="Comma-separated list of the processes to run")
    parser.add_option("-l","--labels", dest="labels", default="", help="Comma-separated list of the processes to associate a label")
    parser.add_option("-v","--version", dest="version", default="", help="Version of the ntuples")
    parser.add_option("-i","--input", dest="input", default="", help="Input path")
    (options, sys.argv[1:]) = parser.parse_args(sys.argv[1:])
    
    process = options.process

    # Reading parser info
    if options.version != "": version = options.version
    if options.input != "": INPUT_PATH = options.input

    # Define output paths
    #INPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/v1/fullStats/'
    #OUTPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/v1/channel1/%s/' % version
    OUTPUT_PATH = INPUT_PATH.replace('fullStats','channel1/%s/' % version)
    print('Output path: ',OUTPUT_PATH)

    # Open TFile
    f = TFile.Open(INPUT_PATH+process_csv[process].replace('.csv','.root'), "READ")
    # Read tree
    tree = f.Get("mytree")
    list_branches = [key.GetName() for key in tree.GetListOfBranches()]
    variables = {}
    for v in sorted(list_branches):
        vartype_ = tree.GetBranch(v).GetListOfLeaves().At(0).GetTypeName()
        if 'tlv' in v:
            variables[v] = ROOT.std.vector(ROOT.Math.PtEtaPhiEVector)()
            tree.SetBranchAddress(v, variables[v])
        else:
            if "VecOps" in vartype_:
                if "int" in str(vartype_):
                    variables[v] = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))()
                    tree.SetBranchAddress(v,variables[v])
                elif "float" in str(vartype_):
                    variables[v] = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))()
                    tree.SetBranchAddress(v,variables[v])
            else:
                if 'int' in vartype_:
                    variables[v] = array('i',[0])
                    tree.SetBranchAddress(v,variables[v])
                elif 'float' in vartype_ or 'Float' in vartype_:
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
            vartype_ = tree.GetBranch(v).GetListOfLeaves().At(0).GetTypeName()
            if 'tlv' in v:
                var[i][v] = ROOT.std.vector(ROOT.Math.PtEtaPhiEVector)()
            else:
                if "VecOps" in vartype_:
                    if "int" in str(vartype_):
                        var[i][v] = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))()
                    elif "float" in str(vartype_):
                        var[i][v] = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))()
                    for x in variables[v]: var[i][v].push_back(x)
                else:
                    if 'int' in vartype_:
                        var[i][v] = array('i',[0])
                    elif 'float' in vartype_ or 'Float' in vartype_:
                        var[i][v] = array('f',[0.])

                    var[i][v] = variables[v][0]
                
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

    # Create acceptance folder if it does not exist
    acceptance_path = '/lhome/ific/a/adruji/DarkMachines/DataPreparation/acceptance/csv/'
    if not os.path.exists(acceptance_path+version):
        print("Creating folder for acceptance ...")
        os.makedirs(acceptance_path+version)

    # Writing acceptance info
    nevents = len(var_light)
    with open('%s/%s/%s_acceptance.csv' % (acceptance_path, version, process), 'w+') as csv:
        csv.write('Process,Events,PassedEvents,Acceptance\n')
        csv.write('%s,%d,%d,%s\n' % (process,int(tree.GetEntries()),nevents,float(nevents)/float(tree.GetEntries())))

    # Create fullStats folder if it does not exist
    if not os.path.exists(OUTPUT_PATH+'fullStats/'):
        print("Creating folder for fullStats ...")
        os.makedirs(OUTPUT_PATH+'fullStats/')

    # Write tree with full statistics
    treename = 'tree'
    #load(var_light,OUTPUT_PATH+'fullStats/'+process_csv[process].replace('.csv','.root'),treename)

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
        #load(var_train,OUTPUT_PATH+'train/'+process_csv[process].replace('.csv','_%s.root' % str(n)),treename)
        #load(var_val,OUTPUT_PATH+'val/'+process_csv[process].replace('.csv','_%s.root' % str(n)),treename)
        #load(var_test,OUTPUT_PATH+'test/'+process_csv[process].replace('.csv','_%s.root' % str(n)),treename)

    # Save numpy arrays useful for unsupervised training

    # Create folders for numpy arrays
    OUTPUT_PATH_arrays = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/arrays/v1/channel1/%s/' % version
    folders = ['','fullStats','train','val','test']
    for folder in folders:
        if not os.path.exists(OUTPUT_PATH_arrays+folder+'/'):
            print("Creating folder for %s samples..." % folder)
            os.makedirs(OUTPUT_PATH_arrays+folder+'/')

    # Create numpy arrays 
    ## For signal
    if ('susy' in process) or ('gluino' in process):
        # Full stats
        load_numpy(var_light,OUTPUT_PATH_arrays+'fullStats/'+process_csv[process].replace('.csv','.npy'), is_signal=True)
        # Only test for signal
        load_numpy(var_light,OUTPUT_PATH_arrays+'test/'+process_csv[process].replace('.csv','.npy'), is_signal=True)
    ## For background, create train, val, test arrays
    else:
        # Full stats
        load_numpy(var_light,OUTPUT_PATH_arrays+'fullStats/'+process_csv[process].replace('.csv','.npy'), is_signal=False)
        
        # Spliting in train, val, test
        var_train = dict((k, var_light[k]) for k in range(0,int(nevents*TRAIN_FRAC)))
        var_val = dict((k, var_light[k+int(nevents*TRAIN_FRAC)]) for k in range(0,int(nevents*VAL_FRAC)))
        var_test = dict((k, var_light[k+int(nevents*TRAIN_FRAC)+int(nevents*VAL_FRAC)]) for k in range(0,int(nevents*TEST_FRAC)))

        load_numpy(var_train,OUTPUT_PATH_arrays+'train/'+process_csv[process].replace('.csv','.npy'), is_signal=False)
        load_numpy(var_val,OUTPUT_PATH_arrays+'val/'+process_csv[process].replace('.csv','.npy'), is_signal=False)
        load_numpy(var_test,OUTPUT_PATH_arrays+'test/'+process_csv[process].replace('.csv','.npy'),  is_signal=False)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- Total of %s seconds ---" % (time.time() - start_time))