Graphite Output for Splunk App - Enables Graphite Output for Splunk Searches, Events
and Alerts.

.. image:: http://dl.dropbox.com/u/4036736/Screenshots/zkpmksp8r9jm.png

Download via Splunk Base: <http://apps.splunk.com/app/1760/>

Usage
=====

The Graphite Output for Splunk App has several operating modes:

#. As a Splunk Search Command "**graphite**", with optional paramaters::

    graphite [--host=HOST] [--port=PORT] [--namespace=NAMESPACE] [--prefix=PREFIX] [--namefield=FIELD] [--noop] [field1 field2 ...]
        --host HOST: Send metrics to HOST. Default: `localhost
        --port PORT: Send metrics to TCP PORT on Graphite host. Default: `2003`
        --namespace NAMESPACE: Prepend metrics with NAMESPACE. Default: `splunk.search`
        --prefix PREFIX: Prepend metrics namespace with PREFIX. Default: None.
        --namefield FIELD: Prepend the metric name with the value of this field. Default: None
        --noop: Test run - Show what would be done, but don't do it.

        field1 field2 ...: Output specified fields to Graphite. Default: All int & float fields.

#. As a Splunk Saved Search Alert: "**graphite.py**".
#. As a Splunk Event Action: "**Graphite Output**".


Use Cases
=========

**The following use cases do not require any App configuration:**


**Use Case 1:** A Search Command sending all metrics to a specified host:

#. Search for events containing metrics you'd like to export to graphite::

    > search meter
    1396998727 meter=275
    1396998722 meter=67
    1396998717 meter=165

#. Append 'graphite' to the search command, using '--host=' to specify the destination host::

    > search meter | graphite --host=graphite.example.com


**Use Case 2:** A Search Command sending a specific metric to a specified host:

#. Search for events containing metrics you'd like to export to graphite, as well as metrics you don't want to send to graphite::

    > search meter
    1396999098 temperature=267 meter=86
    1396999093 temperature=118 meter=258
    1396999088 temperature=189 meter=290
    ...

#. Append the **graphite** search command with **--host=** to specify the destination host and **meter** to specify that you only want to send the **meter** metric::

    > search meter | graphite --host=graphite.example.com meter

#. Append the **graphite** search command with **--namefield=** to specify a field that contains the metric name prefixes::

    > search meter
    | bucket _time span=10s
    | stats
      avg(meter) as meter.mean
      max(meter) as meter.max
      by _time,name
    | graphite --namefield=name meter.mean meter.max


**Use Case 3:** A Search Command sending a specific metric to a specified host with a specified event as metrics prefix:

#. Search for events containing metrics you'd like to export to graphite, as well as metrics you don't want to send to graphite::

    > search meter
    1396999098 temperature=267 meter=86
    1396999093 temperature=118 meter=258
    1396999088 temperature=189 meter=290
    ...

#. Append the **graphite** search command with **--host=** to specify the destination host and **meter** to specify that you only want to send the **meter** metric::

    > search meter | graphite --host=graphite.example.com meter

#. Append the **graphite** search command with **--namefield=** to specify a field that contains the metric name prefixes::

    > search meter
    | bucket _time span=10s
    | stats
      avg(meter) as meter.mean
      max(meter) as meter.max
      by _time,name
    | graphite --namefield=name meter.mean meter.max


**The following use cases require App configuration:**

**Apps** > **Manage Apps** > **Graphite Output** > **Set up**:

.. image:: http://dl.dropbox.com/u/4036736/Screenshots/cc91~hdsqky7.png


**Use Case 3:** As a Event Action:

#. Search for events containing metrics you'd like to export to graphite::

    > search meter
    1396999098 temperature=267 meter=86
    1396999093 temperature=118 meter=258
    1396999088 temperature=189 meter=290
    ...

#. Click  **>** > **Event Actions** > **Graphite Output** pull-down to export events to your App configured graphite destination:
    .. image:: https://dl.dropboxusercontent.com/u/4036736/Screenshots/gwxw3hdx0p%7El.png


**Use Case 4:** As a Saved Search Alert Script:

#. Search for events containing metrics you'd like to export to graphite::

    > search meter
    1396999098 temperature=267 meter=86
    1396999093 temperature=118 meter=258
    1396999088 temperature=189 meter=290
    ...

#. Create a Alert: **Save As** > **Alert**.
    .. image:: http://dl.dropbox.com/u/4036736/Screenshots/67_nutfz8j3w.png
#. Enter Alert paramaters and click **Next**:
    .. image:: http://dl.dropbox.com/u/4036736/Screenshots/~s5koj0l~fha.png
#. Select **Run a Script** and enter **graphite.py**, then click **Save**.
    .. image:: http://dl.dropbox.com/u/4036736/Screenshots/wh3q2-pyz_cg.png


Testing & Development
=====================

This app requires Vagrant and a Python environment to test and develop.

To test this App::

    $ make vagrant_up
    $ make test


Source
======
https://github.com/OnBeep/splunk_graphite


Author
======
* Greg Albrecht <gba@onbeep.com>


Contributors
============
* Greg Albrecht - https://github.com/ampledata
* Christian Ruschke - https://github.com/cruschke
* Nathaniel Waisbrot - https://github.com/waisbrot
* David Narayan - https://github.com/davidnarayan


Copyright
=========
* Copyright 2014 OnBeep, Inc.


License
=======
Apache License, Version 2.0

See LICENSE
