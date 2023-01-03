
import ROOT
from ROOT import TLorentzVector as tlv
from ROOT import TFile,TTree
from ROOT import addressof
from ROOT import std

import csv
import numpy as np
from array import array

vartype = {
    'HT' : 'float',
    'MET' : 'float',
    'MCweight' : 'float',
    'label_Zjets' : 'int',
    'label_ttbar' : 'int',
    'label_wtop' : 'int',
    'isChargedObject' : 'vector<int,ROOT::Detail::VecOps::RAdoptAllocator<int> >*',
    'isNeutralObject' : 'vector<int,ROOT::Detail::VecOps::RAdoptAllocator<int> >*',
    'isJet' : 'vector<int,ROOT::Detail::VecOps::RAdoptAllocator<int> >*',
    'isBJet' : 'vector<int,ROOT::Detail::VecOps::RAdoptAllocator<int> >*',
    'isLepton' : 'vector<int,ROOT::Detail::VecOps::RAdoptAllocator<int> >*',
    'isPhoton' : 'vector<int,ROOT::Detail::VecOps::RAdoptAllocator<int> >*',
    'obj_Energy' : 'vector<float,ROOT::Detail::VecOps::RAdoptAllocator<float> >*',
    'obj_px' : 'vector<float,ROOT::Detail::VecOps::RAdoptAllocator<float> >*',
    'obj_py' : 'vector<float,ROOT::Detail::VecOps::RAdoptAllocator<float> >*',
    'obj_pz' : 'vector<float,ROOT::Detail::VecOps::RAdoptAllocator<float> >*',
    'obj_eta' : 'vector<float,ROOT::Detail::VecOps::RAdoptAllocator<float> >*',
    'obj_phi' : 'vector<float,ROOT::Detail::VecOps::RAdoptAllocator<float> >*',
    'obj_charge' : 'vector<float,ROOT::Detail::VecOps::RAdoptAllocator<float> >*'
}

high_level_vars = {
    'obj_eta' : 'vector<int,ROOT::Detail::VecOps::RAdoptAllocator<int> >*',
    'obj_phi' : 'vector<int,ROOT::Detail::VecOps::RAdoptAllocator<int> >*'
}


def labels(process, label):
    if process == label: return int(1)
    else: return int(0)

def eta(objs):
    l = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            #print(obj.Eta())
            l.push_back(obj.Eta())
    return l

def phi(objs):
    l = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            l.push_back(obj.Phi())
    return l

def H_T(objs):
    HT = 0.
    for obj in sorted(objs):
        if obj=='j' or obj=='b':
            for jet in objs[obj]:
               HT += jet.Pt()
    return HT

def MET(objs):
    return float(objs['met'][0].Pt())

def isJet(objs):
    l = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            if otype=='j' or otype=='b': l.push_back(int(1))
            else: l.push_back(int(0))
    return l

def isBJet(objs):
    l = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            if otype=='b': l.push_back(int(1))
            else: l.push_back(int(0))
    return l

def isLepton(objs):
    l = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            if otype.startswith('e') or otype.startswith('m'): l.push_back(int(1))
            else: l.push_back(int(0))
    return l

def isPhoton(objs):
    l = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            if otype=='g': l.push_back(int(1))
            else: l.push_back(int(0))
    return l

def isCharged(objs):
    l = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            if otype.startswith('e') or otype.startswith('m'): l.push_back(int(1))
            else: l.push_back(int(0))
    return l

def isNeutral(objs):
    l = ROOT.std.vector(int,ROOT.Detail.VecOps.RAdoptAllocator(int))()
    for otype in sorted(objs):
        for obj in objs[otype]:
            if '+' in otype or '-' in otype: l.push_back(int(0))
            else: l.push_back(int(1))
    return l

def charge(objs):
    l = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            if '+' in otype: l.push_back(1.)
            elif '-' in otype: l.push_back(-1.)
            else: l.push_back(0.)
    return l

def px(objs):
    l = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            l.push_back(obj.Px())
    return l

def py(objs):
    l = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            l.push_back(obj.Py())
    return l

def pz(objs):
    l = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            l.push_back(obj.Pz())
    return l

def Energy(objs):
    l = ROOT.std.vector(float,ROOT.Detail.VecOps.RAdoptAllocator(float))() #ROOT.std.vector(float)()
    for otype in sorted(objs):
        for obj in objs[otype]:
            l.push_back(obj.E())
    return l