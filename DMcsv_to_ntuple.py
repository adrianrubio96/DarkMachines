import ROOT
from ROOT import TLorentzVector as tlv
from ROOT import TFile,TTree
from ROOT import std

import csv
import numpy as np
from array import array
import sys, os
import time

from utils.variables import *
from utils.utils import *


INPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/GenerativeModels/linked_DarkMachines_input/'

def main():
    
    # Define parser arguments
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-p","--process", dest="process", help="Comma-separated list of the processes to run")
    (options, sys.argv[1:]) = parser.parse_args(sys.argv[1:])
    
    process = options.process
    INPUT_CSV = process_csv[process]

    # Read csv
    with open(INPUT_PATH+INPUT_CSV) as f:
        # save events 
        events = f.readlines()
        total_events = len(events)
        i = 0

        # Organise objects reading
        N_objs = { i : []}
        objs = {}
        var = {}
         
        # Start of time monitoring
        start = time.time()
        t = 0

        # Reading csv
        debug = False
        for event in events:
            # Set monitoring time
            if (time.time()-start) > t:
                print("Reading during more than %s minutes..." % (t/60))
                t+=300
            if i%100000==0: print('Event ' +str(i))

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
            objs[i]={
                    'j' : [],
                    'b' : [], 
                    'ep' : [],
                    'em' : [],
                    'mp' : [],
                    'mm' : [],
                    'g' : [],
                    'met' : []
                   }
            
            objs[i]['met'].append(met)
            
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
                    objs[i][otype].append(lvec)
                except:
                    objs[i][otype]=[]
                    objs[i][otype].append(lvec)
                debugPrint(debug, objs[i][otype])
                
                Nobjs += 1

                # Sort objects by Pt
                debugPrint(debug, "sorting objs[i][otype]: ")
                objs[i][otype] = sortByPt(objs[i][otype],debug)
                debugPrint(debug, objs[i][otype])
            
            if debug: print('Point 1')
            # Define variables
            N_objs[i] = Nobjs
            var[i]={}
            var[i]['HT'] = H_T(objs[i])
            var[i]['MET'] = MET(objs[i])
            var[i]['obj_px'] = px(objs[i])
            var[i]['obj_py'] = py(objs[i])
            var[i]['obj_pz'] = pz(objs[i])
            var[i]['obj_Energy'] = Energy(objs[i])
            var[i]['obj_eta'] = eta(objs[i])
            var[i]['obj_phi'] = phi(objs[i])
            var[i]['obj_charge'] = charge(objs[i])  
            var[i]['isChargedObject'] = isCharged(objs[i])
            var[i]['isNeutralObject'] = isNeutral(objs[i])
            var[i]['isJet'] = isJet(objs[i])
            var[i]['isBJet'] = isBJet(objs[i])
            var[i]['isLepton'] = isLepton(objs[i])
            var[i]['isPhoton'] = isPhoton(objs[i])
            # Define label variables
            #for l in sorted(process_csv):
            #    var[i]['label_'+l] = labels(process, l)
            # Insert useful info
            var[i]['MCweight'] = float(w)
            # Insert TLorentzVector variables
            if debug: print('Point 2')
            for otype in sorted(objs[0]):
                otype = otype.replace('+','p').replace('-','m')
                var[i]['tlv_%s' % otype] = ROOT.std.vector(ROOT.Math.PtEtaPhiEVector)()
                if len(objs[i][otype])==0: var[i]['tlv_%s' % otype].push_back(ROOT.Math.PtEtaPhiEVector(0.,0.,0.,0.))
                else:
                    for lv in objs[i][otype]:
                        var[i]['tlv_%s' % otype].push_back(lv)
                
            #if debug: break
            i+=1 
            #if i > 5500000: break
            #break
        print("ALL EVENTS HAVE BEEN READ!")

    OUTPUT_PATH = '/lustre/ific.uv.es/grid/atlas/t3/adruji/GenerativeModels/DarkMachines_ntuples/fullStats/'
    OUTPUT_FILE = OUTPUT_PATH+INPUT_CSV.replace('.csv','.root')
    treename = 'mytree'
    load(var, OUTPUT_FILE, treename)



if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- Total of %s seconds ---" % (time.time() - start_time))
