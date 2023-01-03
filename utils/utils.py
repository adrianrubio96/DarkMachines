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
                 ## tt+X
                 #'ttbar' : 'ttbar_10fb.csv',
                 'ttH'   : 'ttbarHiggs_10fb.csv',
                 'ttW' : 'ttbarW_10fb.csv',
                 'ttZ' : 'ttbarZ_10fb.csv',
                 'ttgam' : 'ttbarGam_10fb.csv',
                 'ttWW' : 'ttbarWW_10fb.csv',

                 ## V+jets
                 'Zjets' : 'z_jets_10fb.csv',
                 'Wjets' : 'w_jets_10fb.csv',

                 ## single-top
                 'singletop' : 'single_top_10fb.csv',
                 'singletopbar' : 'single_topbar_10fb.csv',
                 #'wtop' : 'wtop_10fb.csv',
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
                 'singleHiggs' : 'single_higgs_10fb.csv'
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
        for v in sorted(var[0]):
            if "vector" in str(type(var[n][v])) :
                variables[v].clear()
                for x in var[n][v]: variables[v].push_back(x)
            else :
                #print(v)
                #try:
                variables[v][0]=var[n][v]
                #print(v)
                #print(var[n][v])
                #print(variables[v][0])
                #except:
                #    variables[v][0]=var[n][v]
                

        tree.Fill()

    # Save Tree
    tree.Write()
    outfile.Write()
    outfile.Close()
