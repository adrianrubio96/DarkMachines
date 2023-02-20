import ROOT
from ROOT import TLorentzVector as tlv
from ROOT import TFile,TTree
from ROOT import addressof
from ROOT import std
import time

import csv
import numpy as np
from array import array

process_csv = {
                 ### Signal
                 ## SUSY
                 'stop_susy' : 'stop_10fb.csv',
                 'stop_susy_01' : 'stop_01_10fb.csv',
                 'stop_susy_02' : 'stop_02_10fb.csv',
                 'stop_susy_03' : 'stop_03_10fb.csv',
                 'stop_susy_04' : 'stop_04_10fb.csv',
                 'Zp_susy' : 'Zp_technicol_10fb.csv',
                 'Zp_susy_01' : 'Zp_technicol_01_10fb.csv',
                 'Zp_susy_02' : 'Zp_technicol_02_10fb.csv',
                 'Zp_susy_03' : 'Zp_technicol_03_10fb.csv',
                 'Zp_susy_04' : 'Zp_technicol_04_10fb.csv',
                 'Zp_susy_05' : 'Zp_technicol_05_10fb.csv',
                 'gluino' : 'gluino_10fb.csv',
                 'gluino_01' : 'gluino_01_10fb.csv',
                 'gluino_02' : 'gluino_02_10fb.csv',
                 'gluino_03' : 'gluino_03_10fb.csv',
                 'gluino_04' : 'gluino_04_10fb.csv',
                 'gluino_05' : 'gluino_05_10fb.csv',
                 'gluino_06' : 'gluino_06_10fb.csv',
                 'gluino_07' : 'gluino_07_10fb.csv',

                 ### Background
                 ## tt+X
                 'ttbar' : 'ttbar_10fb.csv',
                 'ttH'   : 'ttbarHiggs_10fb.csv',
                 'ttW' : 'ttbarW_10fb.csv',
                 'ttZ' : 'ttbarZ_10fb.csv',
                 'ttgam' : 'ttbarGam_10fb.csv',
                 'ttWW' : 'ttbarWW_10fb.csv',

                 ## V+jets
                 'Zjets' : 'z_jets_10fb.csv',
                 'Wjets' : 'w_jets_10fb.csv',

                 'Zjets_00' : 'z_jets_10fb_00.csv',
                 'Zjets_01' : 'z_jets_10fb_01.csv',
                 'Zjets_02' : 'z_jets_10fb_02.csv',
                 'Zjets_03' : 'z_jets_10fb_03.csv',
                 'Zjets_04' : 'z_jets_10fb_04.csv',
                 'Zjets_05' : 'z_jets_10fb_05.csv',

                 'Wjets_00' : 'w_jets_10fb_00.csv',
                 'Wjets_01' : 'w_jets_10fb_01.csv',
                 'Wjets_02' : 'w_jets_10fb_02.csv',
                 'Wjets_03' : 'w_jets_10fb_03.csv',
                 'Wjets_04' : 'w_jets_10fb_04.csv',
                 'Wjets_05' : 'w_jets_10fb_05.csv',
                 'Wjets_06' : 'w_jets_10fb_06.csv',
                 'Wjets_07' : 'w_jets_10fb_07.csv',
                 'Wjets_08' : 'w_jets_10fb_08.csv',
                 'Wjets_09' : 'w_jets_10fb_09.csv',
                 'Wjets_10' : 'w_jets_10fb_10.csv',
                 'Wjets_11' : 'w_jets_10fb_11.csv',
                 'Wjets_12' : 'w_jets_10fb_12.csv',
                 'Wjets_13' : 'w_jets_10fb_13.csv',
                 'Wjets_14' : 'w_jets_10fb_14.csv',
                 'Wjets_15' : 'w_jets_10fb_15.csv',

                 ## single-top
                 'singletop' : 'single_top_10fb.csv',
                 'singletopbar' : 'single_topbar_10fb.csv',
                 'wtop' : 'wtop_10fb.csv',
                 'wtopbar' : 'wtopbar_10fb.csv',
                 'ztop' : 'ztop_10fb.csv',
                 'ztopbar' : 'ztopbar_10fb.csv',

                 ## Diboson
                 'WW' : 'ww_10fb.csv',
                 'ZW' : 'zw_10fb.csv',
                 'ZZ' : 'zz_10fb.csv',

                 ## Others
                 '2gam' : '2gam_10fb.csv',
                 '4top' : '4top_10fb.csv',
                 'Wgam' : 'Wgam_10fb.csv',
                 'Zgam' : 'Zgam_10fb.csv',
                 'atop' : 'atop_10fb.csv',
                 'atopbar' : 'atopbar_10fb.csv',
                 'gamjets' : 'gam_jets_10fb.csv',
                 'multijets' : 'njets_10fb.csv',
                 'singleHiggs' : 'single_higgs_10fb.csv',

                 'gamjets_00' : 'gam_jets_10fb_00.csv',
                 'gamjets_01' : 'gam_jets_10fb_01.csv',
                 'gamjets_02' : 'gam_jets_10fb_02.csv',
                 'gamjets_03' : 'gam_jets_10fb_03.csv',
                 'gamjets_04' : 'gam_jets_10fb_04.csv',
                 'gamjets_05' : 'gam_jets_10fb_05.csv',
                 'gamjets_06' : 'gam_jets_10fb_06.csv',
                 'gamjets_07' : 'gam_jets_10fb_07.csv',
                 'gamjets_08' : 'gam_jets_10fb_08.csv',
                 'gamjets_09' : 'gam_jets_10fb_09.csv',
                 'gamjets_10' : 'gam_jets_10fb_10.csv',
                 'gamjets_11' : 'gam_jets_10fb_11.csv',

                 'multijets_00' : 'njets_10fb_00.csv',
                 'multijets_01' : 'njets_10fb_01.csv',
                 'multijets_02' : 'njets_10fb_02.csv',
                 'multijets_03' : 'njets_10fb_03.csv',
                 'multijets_04' : 'njets_10fb_04.csv',
                 'multijets_05' : 'njets_10fb_05.csv',
                 'multijets_06' : 'njets_10fb_06.csv',
                 'multijets_07' : 'njets_10fb_07.csv',
                 'multijets_08' : 'njets_10fb_08.csv',
                 'multijets_09' : 'njets_10fb_09.csv',
                 'multijets_10' : 'njets_10fb_10.csv',
                 'multijets_11' : 'njets_10fb_11.csv',
                 'multijets_12' : 'njets_10fb_12.csv',
                 'multijets_13' : 'njets_10fb_13.csv',
                 'multijets_14' : 'njets_10fb_14.csv',
                 'multijets_15' : 'njets_10fb_15.csv',
                 'multijets_16' : 'njets_10fb_16.csv',
                 'multijets_17' : 'njets_10fb_17.csv',
                 'multijets_18' : 'njets_10fb_18.csv',
                 'multijets_19' : 'njets_10fb_19.csv',
                 'multijets_20' : 'njets_10fb_20.csv',
                 'multijets_21' : 'njets_10fb_21.csv',
                 'multijets_22' : 'njets_10fb_22.csv',
                 'multijets_23' : 'njets_10fb_23.csv',
                 'multijets_24' : 'njets_10fb_24.csv',
                 'multijets_25' : 'njets_10fb_25.csv',
                 'multijets_26' : 'njets_10fb_26.csv',
                 'multijets_27' : 'njets_10fb_27.csv',
                 'multijets_28' : 'njets_10fb_28.csv'

}

def debugPrint(debug,message):
    if debug: print(message)

def sortByPt(list_objs,debug):
    list_sorted = list_objs
    isSorted = False
    if len(list_objs)<=1: isSorted=True
    while not isSorted:
        list_aux = list_sorted
        for i in range(0,len(list_objs)-1):
            list_sorted = sortTwoByPt(list_sorted,i,debug)
        if list_aux==list_sorted: isSorted=True
    return list_sorted

def sortTwoByPt(list_objs, i,debug):
    list_out = []
    debugPrint(debug,'list_objs')
    debugPrint(debug,str(list_objs[i].Pt()) + " " + str(list_objs[i+1].Pt()))
    if list_objs[i].Pt()>=list_objs[i+1].Pt():
        list_out = list_objs
    else: 
        for j in range(0,len(list_objs)):
            if j==i:list_out.append(list_objs[j+1])
            elif j==i+1: list_out.append(list_objs[j-1])
            else: list_out.append(list_objs[j])
    debugPrint(debug,'list_out')
    debugPrint(debug,str(list_out[i].Pt()) + " " + str(list_out[i+1].Pt()))
    return list_out

def load(var, OUTPUT_FILE, treename):
    print("Writing new tree...")
    # Create TFile
    outfile = TFile.Open(OUTPUT_FILE, 'RECREATE')
    # Create TTree 
    tree = TTree(treename,'Tree for transformers')
    # Define branches
    variables = {}
    for v in sorted(var[0]):
        if "LorentzVector" in str(type(var[0][v])):
            variables[v] = ROOT.std.vector(ROOT.Math.PtEtaPhiEVector)()
            tree.Branch(v,variables[v])
        elif "VecOps" in str(type(var[0][v])):
            if "int" in str(type(var[0][v])):
                variables[v] = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))()
                tree.Branch(v,variables[v])
            if "float" in str(type(var[0][v])):
                variables[v] = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))()
                tree.Branch(v,variables[v])
        else:
            if type(var[0][v]) is  int :
                variables[v] = array('i',[0])
                tree.Branch(v,variables[v],str(v+"/I"))
            if type(var[0][v]) is float :
                variables[v] = array('f',[0.])
                tree.Branch(v,variables[v],str(v+"/F"))

    # Fill tree
    start = time.time()
    t=0
    print("Filling tree...")
    for n in range(0,len(var)):
        # Set monitoring time
        if (time.time()-start) > t:
            print("Writing during more than %s minutes..." % (t/60))
            t+=300
        # Fill branches
        for v in sorted(var[0]):
            if "vector" in str(type(var[n][v])):
                variables[v].clear()
                for x in var[n][v]: variables[v].push_back(x)
            else :
                variables[v][0]=var[n][v]     

        tree.Fill()

    # Save Tree
    tree.Write()
    outfile.Write()
    outfile.Close()
