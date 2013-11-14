Jumpgate
========

Jumpgate is a library which acts as translation layer to convert incoming OpenStack calls to different cloud provider's API calls.

Installation
------------

Download source and run:

.. code-block:: bash
	
	$ python setup.py install


System Requirements
-------------------
* This library has been tested on Python 3.3.


Configuring
-----------
Once you have jumpgate, you need to configure it to use the appropriate drivers for your chosen target API. Jumpgate ships with two default drivers: An OpenStack passthrough driver (primarily as an example) and a driver for the SoftLayer API. You may install or develop additional drivers to suit your particular needs.

To configure jumpgate to use a particular driver, open the jumpgate.conf file in the root of your installation and change the 'driver' properties for each section you wish to use. If you don't want or need a particular set of endpoints, you can comment out that section and jumpgate will not expose them.

Some drivers may require additional configuration via a driver.conf file. Consult your driver's documentation to determine if this is necessary.


Developing Drivers
------------------
If you're interested in developing a new driver, please consult the DRIVERS.rst file 


Copyright
---------
This software is Copyright (c) 2013 SoftLayer Technologies, Inc.
See the bundled LICENSE file for more information.
