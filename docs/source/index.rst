.. wight documentation master file, created by
   sphinx-quickstart on Wed Aug  7 14:06:48 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Wight Continuous Load Testing
=============================

Wight is a tool that enables users to do continuous load testing of their apps using Funkload tests.

It provides reports that showcase performance tests, diff between two tests and trend of tests.

.. TODO: Add pictures of reports.

Architecture
------------

Wight is divided in server and client components.

The server components include the api and web reports.

The client portion is just a commmand line interface (CLI) that allows usage and scheduling of tests.

Installing
----------

Installing wight's server portion is as easy as::

    $ pip install wight

The CLI app can be installed easily with::

    $ pip install wight-cli

.. toctree::
   :maxdepth: 2
