persair
=======

.. image:: https://badge.fury.io/py/persair.svg
    :target: https://badge.fury.io/py/persair

.. image:: https://travis-ci.org/FNNDSC/persair.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/persair

.. image:: https://img.shields.io/badge/python-3.5%2B-blue.svg
    :target: https://badge.fury.io/py/persair

.. contents:: Table of Contents


Quick Overview
--------------

-  ``persair`` is a python client (CLI and API) for retrieving data from sensors registered to the PurpleAir API.

Overview
--------

``persair`` (the _pers_ is a play on the word _purple_) is a both a standalone script and a python module that provides the means to interact with the PurpleAir API and retrieve sensor information. Together with the app itself, this repo also provides a supporting ecosystem of a monogdb container that is used to persist data pulled from PurpleAir.

While the PurpleAir mission is to enable community driven science, accessing the API does carry a small monetary cost. Without commenting on that reality, ``persair`` provides the means to pull sensor data and archive them in a separate data base with easy/free access.

One of the use cases of ``persair`` is to scan a set of sensors and check if any are off-line (as indicated by the `last_seen` field for the sensor when queried in PurpleAir).

Installation
------------

Using ``PyPI``
~~~~~~~~~~~~~~

The best method of installing this script and all of its dependencies is
by fetching it from PyPI

.. code:: bash

        pip3 install persair

Using CLI
~~~~~~~~~

Alternatively, from a cloned version of the repository:

.. code:: bash

        pip3 install -r requirements.txt -U ./


Running
-------

Ecosystem
~~~~~~~~~

Assuming you have `docker` and `docker-compose` on your system, do

.. code:: bash

    docker-compose up -d

Environment
~~~~~~~~~~~

Several environment variables need to be set prior to running ``persair``:

.. code:: bash

    export DB=tanguro && export DBauthPath=/home/dicom/services/pfair.json &&\
    export URI=mongodb://localhost:27017 && export ReadWriteKey=tanguro


Command line arguments
----------------------

.. code:: html

        [--mongodbinit <init.json>]
        The mongodb initialization file.

        [--version]
        If specified, print app name/version.

        [--man]
        If specified, print this help/man page.

        [--sensorDataGet <sensorRef>]
        Get data for sensor <sensorRef>. This can either be a sensor index
        or a sensor ID. Set the ref type with --sensorRefType.

        [--fieldsList]
        If specified, print information about the fields can be passed to the
        "fields" parameter.

        [fields <comma,separated,list>]
        A comma separated list of field data to retrieve.

        [--asHistory | --asHistoryCSV]
        If specified, do a "history" retrieve (optionally as CSV data)

        [--start_timestamp <%Y-%m-%d>]
        For a "history" retrieve, the start timestamp.

        [--end_timestamp <%Y-%m-%d>]
        For a "history" retrieve, the end timestamp.

        [--sensorRefType sensor_index|sensor_id]
        Set the specific reference "type" for sensors. This must be one of
        either 'sensor_id' or 'sensor_index'. Default is 'sensor_index'.

        [--sensorAddToGroup <sensorRef>]
        Add the sensor referenced by <sensorRef> to a group. The group is
        additionally specified with the --usingGroupID CLI.

        [--sensorsAddFromFile <filename>]
        Add all sensors referenced in <filename> to the group defined by
        --usingGroupID. References in the <filename> should only contain
        a single sensor per line.

        [--sensorsInGroupList <groupid>]
        List all sensors in <groupid>.

        [--usingGroupID <groupid>]
        CLI for additionally specifying a <groupid> to use in conjunction
        with several sensor operations.

Examples
--------

    List all the sensor indices in a group:

        persair --sensorsInGroupList --usingGroupID 1700

    Get (all) the data for a given sensor (note this carries an actual _cost_ in tokens which if exhausted need to be topped off/purchased):

        persair --sensorDataGet 103270

    Get only some fields for a given sensor:

        persair --sensorDataGet 103270 --fields temperature,last_seen,latitude,longitude

    Get some historical data for a give sensor:

        persair --sensorDataGet 103270 --fields temperature \
                --asHistoryCSV --start_timestamp 2023-06-01 --end_timestamp 2023-06-02

