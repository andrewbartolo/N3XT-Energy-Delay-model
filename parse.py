#!/usr/bin/env python3

import h5py
import numpy as np
import sys, os

from TechConfig import *


tc = TechConfig()

csvHeaderFields = ['tCompute', 'tMem', 'tTotal', 'eActive', 'eIdle', 'eCache',
                   'eMemory', 'llcMPKI', 'nInstrs', 'nMemRds', 'nMemWrs']


class SimResults:
    def __init__(self, h5FilePath):
        # Prefer to pass in the zsim-ev.h5 file over zsim.h5, as we only need
        # the last (eventual) row, and it's faster to deserialize.
        f = h5py.File(h5FilePath, 'r')
        ds = f['stats']['root']
        final = ds[-1]
        
        # Pull core name out of .h5 header (positional)
        # This is needed for accessing .h5 fields related to the CPU core itself
        fieldNames = final.dtype.names
        coreName = fieldNames[4]

################################################################################
#####################################  Core  ###################################
################################################################################

        coreCycles = final[coreName]['cycles']
        coreInstrs = final[coreName]['instrs']

        maxCoreCycles = durationCycles = np.max(coreCycles)
        duration = durationCycles / tc.clockFreq

        #print('-'*40)

        # Below, using instrs -> cycles(1):
        # This may lead to overestimating tCompute/tMem ratio
        # (so, conservative for benefits)

        maxCoreInstrs = np.max(coreInstrs)
        tCompute = maxCoreInstrs / tc.clockFreq
        #print("Compute exec time: %f" % (tCompute))


        #print('-'*40)

        tMem = (maxCoreCycles - maxCoreInstrs) / tc.clockFreq
        #print("Mem execution time: %f" % tMem)

        tTotal = tCompute + tMem
        #print("Total time: %f" % tTotal)


        leakageEnergyPerOp = tc.leakagePower / tc.clockFreq
        EPI = tc.dynamicEnergyPerOp + (tc.leakagePower/tc.clockFreq)

        eActivePerCore = np.array([x * EPI for x in coreInstrs])
        eActive = np.sum(eActivePerCore)
        #print("Total core-active energy: %f" % eActive)

        idleCyclesPerCore = np.array([maxCoreCycles - x for x in coreInstrs])

        # Percentage of peak energy spent in idle mode
        idleRatio = leakageEnergyPerOp / EPI

        eIdlePerCore = np.array([idleRatio * EPI * x for x in idleCyclesPerCore])
        eIdle = np.sum(eIdlePerCore)

        #print("Total core-idle energy: %f" % eIdle)

        #print('-'*40)



################################################################################
#####################################  Cache  ##################################
################################################################################


        # l1dHits ends up an nCores-length vector
        l1dHits =     final['l1d']['hGETS'] + final['l1d']['fhGETS'] +\
                      final['l1d']['hGETX'] + final['l1d']['fhGETX']
        # l1dMisses ends up an nCores-length vector
        l1dMisses =   final['l1d']['mGETS'] + final['l1d']['mGETXSM'] +\
                                              final['l1d']['mGETXIM']
        # l1dReads and l1dWrites both end up nCores-length vectors
        l1dReads =  l1dHits + l1dMisses
        l1dWrites = l1dMisses + final['l1d']['PUTS'] + final['l1d']['PUTX']
        # l1dEnergy ends up an nCores-length vector
        l1dEnergy = ((l1dReads + l1dWrites) * (tc.duCacheAccessEnergies[0])) +\
                        (tc.duCacheLeakagePowers[0] * duration)
        # sumL1dEnergy ends up a scalar
        sumL1dEnergy = np.sum(l1dEnergy)



        # l1iHits ends up an nCores-length vector
        l1iHits =     final['l1i']['hGETS'] + final['l1i']['fhGETS'] +\
                      final['l1i']['hGETX'] + final['l1i']['fhGETX']
        # l1iMisses ends up an nCores-length vector
        l1iMisses =   final['l1i']['mGETS'] + final['l1i']['mGETXSM'] +\
                                              final['l1i']['mGETXIM']
        # l1iReads and l1iWrites both end up nCores-length vectors
        l1iReads =  l1iHits + l1iMisses
        l1iWrites = l1iMisses + final['l1i']['PUTS'] + final['l1i']['PUTX']
        # l1iEnergy ends up an nCores-length vector
        l1iEnergy = ((l1iReads + l1iWrites) * (tc.iCacheAccessEnergies[0])) +\
                        (tc.iCacheLeakagePowers[0] * duration)
        # sumL1iEnergy ends up a scalar
        sumL1iEnergy = np.sum(l1iEnergy)




        # l2Hits ends up an nCores-length vector
        l2Hits =      final['l2']['hGETS'] + final['l2']['hGETX']
        # l2Misses ends up an nCores-length vector
        l2Misses =    final['l2']['mGETS'] + final['l2']['mGETXSM'] +\
                                             final['l2']['mGETXIM']
        # l2Reads and l2Writes both end up nCores-length vectors
        l2Reads =   l2Hits + l2Misses
        l2Writes =  l2Misses + final['l2']['PUTS'] + final['l2']['PUTX']
        # l2Energy ends up an nCores-length vector
        l2PreLeakageEnergy = ((l2Reads + l2Writes) * (tc.duCacheAccessEnergies[1]))
        # sumL2PreLeakageEnergy ends up a scalar
        sumL2PreLeakageEnergy = np.sum(l2PreLeakageEnergy)
        # only add leakage power once (L2 shared by all cores)
        sumL2Energy = sumL2PreLeakageEnergy + (tc.duCacheLeakagePowers[1] * duration)


        totalL1Energy = (sumL1iEnergy + sumL1dEnergy)
        eCache = (totalL1Energy + sumL2Energy)
        #print("Total cache energy: %f" % eCache)




################################################################################
####################################  Memory  ##################################
################################################################################



        memPowers = final['mem']['ap']['total']
        sumMemPowers = np.sum(memPowers)

        eMemory = None
        if sumMemPowers == 0:

            controllerMemRds = final['mem']['rd']
            sumMemRds = nMemRds = np.sum(controllerMemRds)
            memRdEnergy = sumMemRds * tc.memRdEnergyPerBit * tc.lineSize

            controllerMemWrs = final['mem']['wr']
            sumMemWrs = nMemWrs = np.sum(controllerMemWrs)
            memWrEnergy = sumMemWrs * tc.memWrEnergyPerBit * tc.lineSize

            sumMemPreLeakageEnergy = memRdEnergy + memWrEnergy 
            eMemory = sumMemPreLeakageEnergy # plus tc.perChannelMemLeakageEnergy * tc.nControllers
        else:
            eMemory = sumMemPowers * duration


        #print("Mem Energy: %s" % eMemory)


################################################################################
#####################################  Misc  ###################################
################################################################################

        nInstrs = np.sum(coreInstrs)

        kiloInstrs = nInstrs / 1e3
        llcMPKI = np.sum(l2Misses) / kiloInstrs

        #print("LLC MPKI: %f" % llcMPKI)

        #print("nInstrs: %d" % nInstrs)

        #print("nMemRds: %d" % nMemRds)
        #print("nMemWrs: %d" % nMemWrs)



        ## Add computed values to the SimResults object
        self.tCompute = tCompute
        self.tMem = tMem
        self.tTotal = tTotal
        self.eActive = eActive
        self.eIdle = eIdle
        self.eCache = eCache
        self.eMemory = eMemory
        self.llcMPKI = llcMPKI
        self.nInstrs = nInstrs
        self.nMemRds = nMemRds
        self.nMemWrs = nMemWrs
        ## End SimResults constructor



    # Print the results CSV with header
    def printCSV(self):
        print(','.join(csvHeaderFields))

        attrStrs = [str(getattr(self, field)) for field in csvHeaderFields]
        print(','.join(attrStrs))



if __name__ == '__main__':
    res = SimResults(sys.argv[1])
    res.printCSV()
