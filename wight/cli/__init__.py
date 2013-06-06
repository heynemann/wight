#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import backend
from colorama.ansi import Fore, Style

from wight.cli.app import WightApp
from wight.errors import UnauthenticatedError, TargetNotSetError

def main():
    defaults = backend.defaults('wight', 'log')
    defaults['log']['level'] = 'WARN'

    app = WightApp(config_defaults=defaults)
    app.register_controllers()

    bright_yellow = "%s%s" % (Fore.YELLOW, Style.BRIGHT)
    bright_magenta = "%s%s" % (Fore.MAGENTA, Style.BRIGHT)
    dim_red = "%s%s" % (Fore.RED, Style.DIM)
    dim_white = "%s%s" % (Fore.WHITE, Style.DIM)
    reset = "%s%s" % (Style.RESET_ALL, dim_white)
    try:
        app.setup()
        app.run()
    except UnauthenticatedError:
        print "\n%sYou need to be logged to use this command. Use '%swight login%s %s<user e-mail>%s%s' to login.%s\n" % (
            dim_red, bright_yellow, reset, bright_magenta, reset, dim_red, reset
        )
    except TargetNotSetError:
        print "\n%sYou need to set the target to use wight. Use '%swight target-set%s %s<url of target>%s%s' to login.%s\n" % (
            dim_red, bright_yellow, reset, bright_magenta, reset, dim_red, reset
        )
    finally:
        app.close()

if __name__ == '__main__':
    main()
