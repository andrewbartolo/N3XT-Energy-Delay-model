#!/usr/bin/env python3


## The technology config (as opposed to architectural config (ArchConfig))
class TechConfig_n3xt:
    def __init__(self):
        self.nCores                 = 64                    # TODO get from .h5
        self.nCacheLevels           = 2                     # TODO get from .h5
        self.nMemControllers        = 64                    # TODO get from .h5
        self.lineSize               = 64 * 8                # line size in bits
        self.leakagePower           = 0.03                  # in W
        self.dynamicEnergyPerOp     = 0.04                  # in nJ
        self.clockFreq              = 4                     # in GHz ; TODO get from out.cfg (?)
        self.iCacheAccessEnergies   = [0.003]               # Cache access energies in nJ for each level
        self.duCacheAccessEnergies  = [0.005, 0.6]          # Cache access energies in nJ for each level
        self.iCacheLeakagePowers    = [1.53]                # for each level
        self.duCacheLeakagePowers   = [2.53, 0.05]          # mW ; for each level
        self.memRdEnergyPerBit      = 0.8                   # in pJ/bit
        self.memWrEnergyPerBit      = 1.5                   # in pJ/bit
        self.memLeakagePower        = 0.8                   # in mW

        self.inSI = False
        self.toSI()                 # convert the above to SI units


    def toSI(self):
        if not self.inSI:   # toSI() needs to be idempotent
            self.dynamicEnergyPerOp *= 1e-9
            self.clockFreq *= 1e9
            self.iCacheAccessEnergies = [x * 1e-9 for x in self.iCacheAccessEnergies]
            self.duCacheAccessEnergies = [x * 1e-9 for x in self.duCacheAccessEnergies]
            self.iCacheLeakagePowers = [x * 1e-3 for x in self.iCacheLeakagePowers]
            self.duCacheLeakagePowers = [x * 1e-3 for x in self.duCacheLeakagePowers]
            self.memRdEnergyPerBit *= 1e-12
            self.memWrEnergyPerBit *= 1e-12
            self.memLeakagePower *= 1e-3

            self.inSI = True
