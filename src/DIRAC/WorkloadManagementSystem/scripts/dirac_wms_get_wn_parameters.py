#!/usr/bin/env python
"""
Determine number of processors and memory for the worker node
"""
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script
from DIRAC.WorkloadManagementSystem.Utilities import JobParameters

ceName = ""
ceType = ""
Queue = ""


def setCEName(args):
    global ceName
    ceName = args


def setSite(args):
    global Site
    Site = args


def setQueue(args):
    global Queue
    Queue = args


@Script()
def main():
    global ceName
    global Site
    global Queue
    Script.registerSwitch("N:", "Name=", "Computing Element Name (Mandatory)", setCEName)
    Script.registerSwitch("S:", "Site=", "Site Name (Mandatory)", setSite)
    Script.registerSwitch("Q:", "Queue=", "Queue Name (Mandatory)", setQueue)
    Script.parseCommandLine(ignoreErrors=True)

    gLogger.info("Getting number of processors")
    numberOfProcessor = JobParameters.getNumberOfProcessors(Site, ceName, Queue)

    gLogger.info("Getting memory (RAM)")
    maxRAM = JobParameters.getMemoryFromProc()

    gLogger.info("Getting number of GPUs")
    numberOfGPUs = JobParameters.getNumberOfGPUs(Site, ceName, Queue)

    # just communicating it back
    gLogger.notice(" ".join(str(wnPar) for wnPar in [numberOfProcessor, maxRAM, numberOfGPUs]))


if __name__ == "__main__":
    main()
