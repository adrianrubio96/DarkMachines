import ROOT
from ROOT import TLorentzVector as tlv
from ROOT import TFile,TTree
from ROOT import std

import csv
from csv import DictReader
import linecache
import numpy as np
from array import array
import sys, os
import time

from utils.variables import *
from utils.utils import *


def main():
    
    # Define parser arguments
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p","--process", dest="process", help="Comma-separated list of the processes to run")
    parser.add_option("-v","--version", dest="version", default="", help="Version of the ntuples")
    parser.add_option("-i","--input", dest="input", default="", help="Input path")
    (options, sys.argv[1:]) = parser.parse_args(sys.argv[1:])

    # Reading parser info: version
    if options.version != "":
        version = options.version
    if options.input != "":
        INPUT_PATH = options.input
    
    # Reading parser info: splitting large csv inputs
    ## Format: -p PROCESS:TOTAL_SPLIT:SPLIT_NUMBER
    ## Example: -p Zjets:3:2  --> Select process Zjets, which is divided in 3 pieces and the 2nd one is selected
    process = options.process.split(":")[0]
    INPUT_CSV = process_csv[process]
    TOTAL_SPLIT=0
    SPLIT_NUMBER=0
    if len(options.process.split(":")) > 1:
        TOTAL_SPLIT=int(options.process.split(":")[1])
        SPLIT_NUMBER=int(options.process.split(":")[2])
        print("Reading the part %d/%d of the csv input %s " % (SPLIT_NUMBER, TOTAL_SPLIT, INPUT_CSV))
    else: 
        print("Reading the whole csv input %s" % INPUT_CSV)

    # Defining writing paths and tree
    if TOTAL_SPLIT == 0: 
        OUTPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/%s/chan1/' % version
        OUTPUT_FILE = OUTPUT_PATH+INPUT_CSV.replace('.csv','.root')
    else:
        OUTPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/%s/parallel_splits/' % version
        OUTPUT_FILE = OUTPUT_PATH+INPUT_CSV.replace('.csv','_%s_%s.root' % (TOTAL_SPLIT, SPLIT_NUMBER))
    treename = 'mytree'
    
    # Create TFile
    outfile = TFile.Open(OUTPUT_FILE, 'RECREATE')
    # Create TTree 
    tree = TTree(treename,'Tree for transformers')
    
    # Read csv
    #with open(INPUT_PATH+INPUT_CSV, 'r') as f:
    #    # save events 
    #    #events = f.readlines()

    #    # pass the file object to DictReader() to get the DictReader object
    #    csv_dict_reader = DictReader(f)
    #    print(csv_dict_reader)
    #    #rows = list(csv_dict_reader)
    #    #total_events = len(rows)
    #    total_events = sum(1 for row in csv_dict_reader)
    #    print(total_events)  

    #    # select events to run
    #    if TOTAL_SPLIT != 0:
    #        starting_event = float(SPLIT_NUMBER-1)/float(TOTAL_SPLIT)*float(total_events)
    #        ending_event = float(SPLIT_NUMBER)/float(TOTAL_SPLIT)*float(total_events)
    #        print("Reading from event %d to event %s " % (int(starting_event), int(ending_event)))

    # Organise objects reading
    i = 0
    #N_objs = { i : []}
    objs = {}
    var = {}
     
    # Start of time monitoring
    start = time.time()
    t = 0

    # Reading csv
    debug = False

    # iterate over each line as a ordered dictionary
    #for event in csv_dict_reader:
    #    print(event)
    
    #for n_event in range(int(starting_event), int(ending_event)):
    #while True:
    with open(INPUT_PATH+INPUT_CSV, 'r') as f:
        #event = events[n_event]
        #event = linecache.getline(INPUT_PATH+INPUT_CSV,n_event+1) 
        for event in f:
            n_event=i
            # Set monitoring time
            if (time.time()-start) > t:
                print("Reading during more than %s minutes..." % (t/60))
                t+=300
            if i%10000==0: print('Event ' +str(n_event))
    
            # Get event info
            debugPrint(debug, "event: "+event)
            eventID = event.split(';')[0]
            debugPrint(debug, "eventID: "+eventID)
            processID = event.split(';')[1]
            debugPrint(debug, "processID: "+processID)
            w = event.split(';')[2]
            debugPrint(debug, "w: "+w)
            met = ROOT.Math.PtEtaPhiEVector(float(event.split(';')[3])/1000.,0.,float(event.split(';')[4]),float(event.split(';')[3])/1000.)
            debugPrint(debug, "met")
            debugPrint(debug, met)
    
            # Get objects info
            objects = event.split(';')[5:]
            debugPrint(debug, "objects")
            debugPrint(debug, objects)
            objs={
                    'j' : [],
                    'b' : [], 
                    'ep' : [],
                    'em' : [],
                    'mp' : [],
                    'mm' : [],
                    'g' : [],
                    'met' : []
                   }
            
            objs['met'].append(met)
            
            Nobjs = 1
            
            if debug: print('Point 0')
            for obj in objects:
                # Read object name
                debugPrint(debug, "obj: "+obj)
                otype = obj.split(',')[0].replace('+','p').replace('-','m')
                # Read object kinematics
                kins = obj.split(',')[1:]
                debugPrint(debug, 'kins: ')
                debugPrint(debug, kins)
                if len(kins)==0: continue
                # Define TLorentzVector
                debugPrint(debug, "lvec: ")
                lvec = ROOT.Math.PtEtaPhiEVector(float(kins[1])/1000.,float(kins[2]),float(kins[3]),float(kins[0])/1000.)
                debugPrint(debug, lvec)
                # Save kinematics
                debugPrint(debug, "objs[i][otype]: ")
                try:
                    objs[otype].append(lvec)
                except:
                    objs[otype]=[]
                    objs[otype].append(lvec)
                debugPrint(debug, objs[otype])
                
                Nobjs += 1
    
                # Sort objects by Pt
                debugPrint(debug, "sorting objs[otype]: ")
                objs[otype] = sortByPt(objs[otype],debug)
                debugPrint(debug, objs[otype])
                
            if debug: print('Point 1')
            # Define variables
            #N_objs = Nobjs
            var={}
            var['HT'] = H_T(objs)
            var['MET'] = MET(objs)
            var['obj_px'] = px(objs)
            var['obj_py'] = py(objs)
            var['obj_pz'] = pz(objs)
            var['obj_Energy'] = Energy(objs)
            var['obj_eta'] = eta(objs)
            var['obj_phi'] = phi(objs)
            var['obj_charge'] = charge(objs)  
            var['isChargedObject'] = isCharged(objs)
            var['isNeutralObject'] = isNeutral(objs)
            var['isJet'] = isJet(objs)
            var['isBJet'] = isBJet(objs)
            var['isLepton'] = isLepton(objs)
            var['isElectron'] = isElectron(objs)
            var['isMuon'] = isMuon(objs)
            var['isMET'] = isMET(objs)
            var['isPhoton'] = isPhoton(objs)
            # Define label variables
            #for l in sorted(process_csv):
            #    var[i]['label_'+l] = labels(process, l)
            # Insert useful info
            var['MCweight'] = float(w)
            # Insert TLorentzVector variables
            if debug: print('Point 2')
            for otype in sorted(objs):
                otype = otype.replace('+','p').replace('-','m')
                var['tlv_%s' % otype] = ROOT.std.vector(ROOT.Math.PtEtaPhiEVector)()
                if len(objs[otype])==0: var['tlv_%s' % otype].push_back(ROOT.Math.PtEtaPhiEVector(0.,0.,0.,0.))
                else:
                    for lv in objs[otype]:
                        var['tlv_%s' % otype].push_back(lv)
    
    
            # Define branches in output tree
            if i==0:
                print("Defining tree branches...")
                variables = {}
                for v in sorted(var):
                    if "LorentzVector" in str(type(var[v])):
                        variables[v] = ROOT.std.vector(ROOT.Math.PtEtaPhiEVector)()
                        tree.Branch(v,variables[v])
                    elif "VecOps" in str(type(var[v])):
                        if "int" in str(type(var[v])):
                            variables[v] = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))()
                            tree.Branch(v,variables[v])
                        if "float" in str(type(var[v])):
                            variables[v] = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))()
                            tree.Branch(v,variables[v])
                    else:
                        if type(var[v]) is int :
                            variables[v] = array('i',[0])
                            tree.Branch(v,variables[v],str(v+"/I"))
                        if type(var[v]) is float :
                            variables[v] = array('f',[0.])
                            tree.Branch(v,variables[v],str(v+"/F"))  
                    
            
            # Writing event "i" into tree
            #print("Filling tree...")
            for v in sorted(var):
                if "vector" in str(type(var[v])) :
                    variables[v].clear()
                    for x in var[v]: variables[v].push_back(x)
                else :
                    variables[v][0]=var[v]
                
            tree.Fill()

            #print(variables)
    
            #if debug: break
            
            i+=1 
            #if i > 10: break
            #break
    
    # Save Tree
    tree.Write()
    outfile.Write()
    outfile.Close()
    
    #if TOTAL_SPLIT == 0: 
    #    OUTPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/fullStats/'
    #    OUTPUT_FILE = OUTPUT_PATH+INPUT_CSV.replace('.csv','.root')
    #else:
    #    OUTPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/parallel_splits/'
    #    OUTPUT_FILE = OUTPUT_PATH+INPUT_CSV.replace('.csv','_%s_%s.root' % (TOTAL_SPLIT, SPLIT_NUMBER))
    #treename = 'mytree'
    #load(var, OUTPUT_FILE, treename)



if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- Total of %s seconds ---" % (time.time() - start_time))
