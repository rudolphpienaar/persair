#!/usr/bin/env python3
#
# (c) 2023+ Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

__version__ = "2.2.14"

import sys, os

from    persair             import persair
from    persair.persair     import parser_setup, parser_interpret, parser_JSONinterpret

try:
    from    .               import __pkg, __version__
except:
    from persair           import __pkg, __version__

import  asyncio
from    asyncio             import AbstractEventLoop

from    argparse            import RawTextHelpFormatter
from    argparse            import ArgumentParser, Namespace
import  pudb
from    pfmisc              import Colors as C
from    print_color         import print as cprint
from    typing              import Any, Literal
import  json
import  re
NC =  C.NO_COLOUR

str_title:str = f"""

                                                   _
                                                  (_)
                         _ __   ___ _ __ ___  __ _ _ _ __
                        | '_ \ / _ \ '__/ __|/ _` | | '__|
                        | |_) |  __/ |  \__ \ (_| | | |
                        | .__/ \___|_|  |___/\__,_|_|_|
                        | |
                        |_|
"""

str_heading:str = f"""
                            python purpleair client

"""

def synopsis(ab_shortOnly = False) -> None:
    scriptName:str          = os.path.basename(sys.argv[0])
    print(C.CYAN + '''
    NAME
        ''', end = '' + NC)
    print(scriptName)
    print(C.CYAN + '''
    SYNPOSIS
        ''' + NC, end = '')
    print(scriptName + persair.package_CLIfull)
    print(C.CYAN + '''
    BRIEF EXAMPLE
    ''' + NC)

    if ab_shortOnly: return
    print(C.CYAN + '''
    ARGS''' + NC, end="")
    print(persair.package_argsSynopsisFull)

def earlyExit_check(args:Namespace) -> int:
    """
    Check if version/man page are required, and if so service
    and return

    Args:
        args (Namespace): The CLI namespace

    Returns:
        int: 0 -- continue
             1 -- exit
    """
    if args.man:
        cprint(str_title, color='green')
        str_help:str    = ""
        if args.man:    synopsis(False)
        else:           synopsis(True)
        return 1
    if args.b_version:
        print("Name:    ", end="")
        print(C.LIGHT_CYAN + f'{__pkg.name}' + NC)
        print("Version: ", end="")
        print(C.LIGHT_GREEN + f'{__version__}\n')
        return 1
    return 0

def main(argv=None) -> Literal[1, 0]:

    # pudb.set_trace()
    # Preliminary setup
    parser:ArgumentParser       = parser_setup('A client for interacting with PurpleAir')
    options:Namespace           = parser_interpret(parser, argv)
    if earlyExit_check(options): return 1

    # Setup the persair sensor object
    sensors:persair.Persair = persair.Persair(options)

    # and run it!
    loop:AbstractEventLoop  = asyncio.get_event_loop()
    loop.run_until_complete(sensors.service())

    print(sensors.responseData.json())

    return 0

if __name__ == "__main__":
    sys.exit(main())
