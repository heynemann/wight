#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com

from cement.core import backend

from wight.cli.app import WightApp


def main():
    defaults = backend.defaults('wight', 'log')
    defaults['log']['level'] = 'WARN'

    app = WightApp(config_defaults=defaults)
    app.register_controllers()

    try:
        app.setup()
        app.run()
    finally:
        app.close()

if __name__ == '__main__':
    main()
