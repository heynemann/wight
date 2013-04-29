#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com


from cement.core import foundation, handler

from wight.cli.base import WightBaseController
from wight.cli.schedule import ScheduleController


def main():
    app = foundation.CementApp('wight', base_controller=WightBaseController)
    handler.register(ScheduleController)

    try:
        app.setup()
        app.run()
    finally:
        app.close()

if __name__ == '__main__':
    main()
