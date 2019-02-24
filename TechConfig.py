#!/usr/bin/env python3


## The technology config (as opposed to architectural config (ArchConfig))
class TechConfig:
    def __init__(self):
        self.nCores                 = 64                    # TODO get from .h5
        self.nCacheLevels           = 2                     # TODO get from .h5
        self.nMemControllers        = 1                     # TODO get from .h5
        self.lineSize               = 64 * 8                # line size in bits
        self.leakagePower           = 0.3                   # 0.3 W
        self.dynamicEnergyPerOp     = 0.5                   # 0.5 nJ
        self.clockFreq              = 2                     # 2 GHz ; TODO get from out.cfg (?)
        self.iCacheAccessEnergies   = [0.01]                # Cache access energies in nJ for each level
        self.duCacheAccessEnergies   = [0.05, 0.52]          # Cache access energies in nJ for each level
        self.iCacheLeakagePowers    = [0]                   # for each level
        self.duCacheLeakagePowers    = [0, 100]              # mW ; for each level
        self.memRdEnergyPerBit      = 52                    # in pJ/bit
        self.memWrEnergyPerBit      = 52                    # in pJ/bit

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

            self.inSI = True
