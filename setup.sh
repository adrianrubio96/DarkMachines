#!/usr/bin/bash
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
source $ATLAS_LOCAL_ROOT_BASE/user/atlasLocalSetup.sh -2
lsetup "root 6.18.04-x86_64-centos7-gcc8-opt" --quiet
