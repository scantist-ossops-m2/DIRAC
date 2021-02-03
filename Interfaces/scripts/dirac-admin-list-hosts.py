#!/usr/bin/env python
########################################################################
# File :    dirac-admin-list-hosts
# Author :  Adrian Casajus
########################################################################
"""
Usage:

  dirac-admin-list-hosts (<options>|<cfgFile>)*

Example:

  $ dirac-admin-list-hosts
  dirac.in2p3.fr
  host-dirac.in2p3.fr
"""
from __future__ import print_function
__RCSID__ = "$Id$"

from DIRAC.Core.Base import Script

Script.setUsageMessage(__doc__)
Script.registerSwitch("e", "extended", "Show extended info")

Script.parseCommandLine(ignoreErrors=True)
args = Script.getPositionalArgs()

from DIRAC import exit as DIRACExit
from DIRAC.Interfaces.API.DiracAdmin import DiracAdmin
diracAdmin = DiracAdmin()
exitCode = 0
errorList = []
extendedInfo = False

for unprocSw in Script.getUnprocessedSwitches():
  if unprocSw[0] in ('e', 'extended'):
    extendedInfo = True

if not extendedInfo:
  result = diracAdmin.csListHosts()
  for host in result['Value']:
    print(" %s" % host)
else:
  result = diracAdmin.csDescribeHosts()
  print(diracAdmin.pPrint.pformat(result['Value']))

for error in errorList:
  print("ERROR %s: %s" % error)

DIRACExit(exitCode)
