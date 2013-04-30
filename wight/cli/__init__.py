#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com


from cement.core import foundation, handler

from wight.cli.base import WightDefaultController
from wight.cli.schedule import ScheduleController
from wight.cli.target import TargetSetController, TargetGetController


class WightApp(foundation.CementApp):
    class Meta:
        label = 'wight'
        base_controller = WightDefaultController


def main():
    app = WightApp()
    handler.register(ScheduleController)
    handler.register(TargetSetController)
    handler.register(TargetGetController)

    try:
        app.setup()
        app.run()
    finally:
        app.close()

if __name__ == '__main__':
    main()
