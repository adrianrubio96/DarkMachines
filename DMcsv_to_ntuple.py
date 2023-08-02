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
    parser.add_option("-c","--chan", dest="channel", default="", help="Channel to run")
    (options, sys.argv[1:]) = parser.parse_args(sys.argv[1:])

    # Reading parser info: version
    if options.version != "": version = options.version
    else: 
        print("[WARNING] Please provide a version")
        sys.exit()
    if options.input != "": INPUT_PATH = options.input
    else: 
        print("[WARNING] Please provide an input path")
        sys.exit()
    if options.channel != "": channel = options.channel
    else: 
        print("[WARNING] Please provide a channel")
        sys.exit()
    if options.process != "": process = options.process
    else:
        print("[WARNING] Please provide a process")
        sys.exit()
    
    # Reading parser info: splitting large csv inputs
    INPUT_CSV = process_csv[process]
    print("[INFO] Reading the csv input %s" % INPUT_CSV)

    # Defining writing paths and tree
    OUTPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/DarkMachines/DarkMachines_ntuples/%s/%s/' % (version,channel)
    OUTPUT_FILE = OUTPUT_PATH+INPUT_CSV.replace('.csv','.root')
    treename = 'mytree'
    
    # Create TFile
    outfile = TFile.Open(OUTPUT_FILE, 'RECREATE')
    # Create TTree 
    tree = TTree(treename,'Tree for transformers')
    
    # Organise objects reading
    i = 0
    #N_objs = { i : []}
    objs = {}
    var = {}
     
    # Start of time monitoring
    start = time.time()
    t = 0

    # Reading csv
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
            eventID = event.split(';')[0]
            processID = event.split(';')[1]
            w = event.split(';')[2]
            met = ROOT.Math.PtEtaPhiEVector(float(event.split(';')[3])/1000.,0.,float(event.split(';')[4]),float(event.split(';')[3])/1000.)
    
            # Get objects info
            objects = event.split(';')[5:]
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
            
            for obj in objects:
                # Read object name
                otype = obj.split(',')[0].replace('+','p').replace('-','m')
                # Read object kinematics
                kins = obj.split(',')[1:]
                if len(kins)==0: continue
                # Define TLorentzVector
                lvec = ROOT.Math.PtEtaPhiEVector(float(kins[1])/1000.,float(kins[2]),float(kins[3]),float(kins[0])/1000.)
                # Save kinematics
                try:
                    objs[otype].append(lvec)
                except:
                    objs[otype]=[]
                    objs[otype].append(lvec)
                
                Nobjs += 1
    
                # Sort objects by Pt
                objs[otype] = sortByPt(objs[otype])
                
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
            var['isPositron'] = isPositron(objs)
            var['isMuon'] = isMuon(objs)
            var['isAntiMuon'] = isAntimuon(objs)
            var['isMET'] = isMET(objs)
            var['isPhoton'] = isPhoton(objs)
            # Define label variables
            #for l in sorted(process_csv):
            #    var[i]['label_'+l] = labels(process, l)
            # Insert useful info
            var['MCweight'] = float(w)
            # Insert TLorentzVector variables
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
            
            i+=1 
            #if i > 10: break
            #break
    
    # Save Tree
    tree.Write()
    outfile.Write()
    outfile.Close()


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- Total of %s seconds ---" % (time.time() - start_time))
