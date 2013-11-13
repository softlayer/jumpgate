---
layout: pages
slug: getting-started
baseurl: "../"
---

# Introduction

The primary purpose of the this project is to provide an easy way to add
OpenStack API compatibility to existing cloud products. This is
accomplished through a series of drivers that are specific to each cloud
provider. If you're reading this document, it is assumed that you are
interested in using this project to add OpenStack API compatibility via
drivers.

# Getting Started

When creating a new driver, there are only a few things you need to
understand:

1.  The compatibility layer has been written primarily for Python 3.3 and assumes your drivers will use this version as well.
2.  Drivers are built as a series of objects for the 
3.  . You should be familiar with both Falcon and REST APIs in general.
3.  You need to be familiar with the expected [OpenStack API](http://api.openstack.org/api-ref.html) JSON. The compatibility layer will provide the endpoint mappings for you, but does not handle building valid responses.

Once you have these things, you are ready to begin building your driver.

## Your First Driver

There are many places where you could begin building your first driver,
but we've generally found starting with the index and the Identity
driver (Keystone) to be the easiest. We're going to cover how to build
out a couple endpoints to give you an idea. From there, you can use the
SoftLayer driver that ships with this project as a further example of
other endpoints, should you need it.

Note that there are no restrictions on how you build your driver as long
as you make it work with the [Falcon framework](http://falconframework.org). You are free to use
whatever libraries, tools, and folder layout you are most comfortable
with. This document will use the same style as the SoftLayer driver for
consistency, but you are not required to do this for your driver.

### Create Your Driver

The first step is to create your driver. You can do this anywhere, as
long as its within your Python path and the compatibility layer can load
it. We're going to do it within the 'drivers' directory for identity.
We'll start with the index driver.

	$ mkdir babelfish/index/drivers/my_driver

Next we're going to create an \_\_init\_\_.py within that directory.
This is the file that the compatibility layer is going to load. We could
jam all of our code into it, but that's going to get extremely large for
some projects, such as Nova Compute. So instead, we're going to use this
as a module to load other modules based upon functional area. To start,
make this the contents of your \_\_init\_\_.py file:

	from babelfish.openstack import openstack_dispatcher
	from .endpoints.index import IndexV2

	openstack_dispatcher.set_handler('v2_index', IndexV2())

	openstack_dispatcher.import_routes()

Let's look at each section. The first thing we import is the
openstack\_dispatcher. Each area of the API has a dispatcher that knows
about the routes/endpoints that OpenStack has. The compatibility layer creates these dispatcher objects for you and
uses them to determine which endpoints your driver supports and doesn't
expose any functionality you haven't created.

The next import pulls in the IndexV2 class. This is the actual driver
class we'll be developing for the /v2 endpoint. We'll cover it in a
moment.

Next, we see a call to the set\_handler() method. This is how we tell
the dispatcher object that we're going to expose a particular endpoint.
The set\_handler() method takes two arguments: The endpoint variable and
the responder object for to handle that endpoint. Each endpoint that
OpenStack supports has a unique variable name so that you can refer to
it without having to know exactly what the URL is. You can either open
up the dispatcher to get a list of all of the endpoint variables or
check out our docs on GitHub to get a list there. The handler is the
IndexV2() object we imported earlier.

The last thing in the file is a call to import\_routes(). This call
tells the dispatcher that you've finished assigning handlers and that it
should import the routes into Falcon's routes table. If you don't make
this call, your endpoints won't be exposed and your driver won't do
anything!

# The Index Endpoint

Now that the driver has been created, we need to build a response
handler. As noted above, we're starting with the v2\_index endpoint,
which corresponds to the /v2 path. If you refer to the [OpenStack API](http://api.openstack.org/api-ref.html)
docs, you'll find a /v2 endpoint for multiple APIs. The one we're going
to concern ourselves with right now is within the [Compute API](http://api.openstack.org/api-ref-compute.html). If you
read the details for the section, you'll find out that it doesn't need a
request body and the response JSON is straightforward. We could copy the
document from the docs exactly and have a valid response, but there are
a couple problems with this:

1.  It has URLs in it
2.  It doesn't represent the functionality our driver actually supports.

When implementing things like the index endpoint (and the tokens
endpoint later), it's extremely important to remember that the output is
dependent upon what your driver *actually* supports. In this case, we're
not going to worry about v3 support and we're going to add in v1 support
(to make using Horizon easier).

To start, let's create the endpoints directory we imported from earlier:

	$ mkdir babelfish/index/drivers/my_driver/endpoints

Now within that, create the index.py where our IndexV2 class will
reside. (Note - Since this is Python 3.3, we don't need an
\_\_init\_\_.py file within the directory.) Start by putting the
following within the index.py file:

	from babelfish.compute import compute_dispatcher

	class IndexV2(object):
    	def on_get(self, req, resp):
        	versions = [{
            	'id': 'v2.0',
            	'links': [{
                	'href': compute_dispatcher.get_endpoint_url(req, 'v2_index'),
                	'rel': 'self'
            	}],
            	'status': 'CURRENT',
            	'media-types': [
                	{
                    	'base': 'application/json',
                    	'type': 'application/vnd.openstack.compute.v1.0+json',
                	}
            	],
         	}, {
             	'id': 'v1.0',
             	'links': [{
                 	'href': compute_dispatcher.get_endpoint_url(req, 'v1_index'),
                 	'rel': 'self'
             	}],
             	'status': 'ACTIVE',
             	'media-types': [
                 	{
                     	'base': 'application/json',
                     	'type': 'application/vnd.openstack.compute.v1.0+json',
                 	}
             	],
         	}]

         	resp.body = {'versions': versions}

As with the driver above, we import a dispatcher, but notice that we're
importing the compute\_dispatcher (for Nova) and not the generic
OpenStack one. We'll see why in a moment.

Next, we start the class itself. Response handlers are plain objects and
don't need to inherit from any particular class or interface. Per the
[Compute API](http://api.openstack.org/api-ref-compute.html) documentation, we know that this endpoint handles the GET
verb, so we create an on\_get() function. This is how the
[Falcon framework](http://falconframework.org) handles responses. The contents of the function are
what we're going to do to serve this endpoint. This should look very
similar to the sample within the API docs, though you'll see we've added
the v1 support as we discussed and we're not hardcoding URLs.

Because dispatchers handle endpoints, they also know how to build URLs.
This is handy because it provides a level of abstraction between your
driver and the OpenStack API itself so that if something changed in the
future or the compatibility layer switched hosts, you shouldn't need to
change any of your driver code. To get the URL for a particular
endpoint, call the get\_endpoint\_url() method on the appropriate
dispatcher and pass in the Falcon request object and the identifier for
the endpoint. If the endpoint's URL has variables within it (as a lot of
the Nova compute endpoints do), you pass them in as keyword arguments.
The only exception to this is the tenant ID, which we'll discuss later. Each dispatcher only knows about its own endpoints (they're contained as properties of the object), so you need to use the appropriate one when building your endpoint URL.

The very last thing the function does is assign a body to the response
object. This should conform to the expected format within the OpenStack
API documentation. Assuming you provide a valid Python dictionary, the
compatibility layer will automatically JSON encode it for you. Note that
the default status code is 200. If you need to assign a different status
code, you should refer to the Falcon docs or look at the examples within
the SoftLayer driver.

# The Tokens Endpoint

The other endpoint example we're going to provide is the v2\_tokens
endpoint within the Keystone Identity API. This endpoint is important
because every OpenStack tool will first try to authenticate to Keystone
before doing anything else, so if you don't have this, you may have
problems. It also has several other interesting examples for a driver
that make it worth discussing even if you're not planning on using
Keystone.

As with the index driver, we first need to create a few things. We'll do
it in a larger batch this time:

	$ mkdir babelfish/identity/drivers/my_driver
	$ mkdir babelfish/identity/drivers/my_driver/endpoints

Create the \_\_init\_\_.py file

	from babelfish.identity import identity_dispatcher
	from .endpoints.tokens import TokensV2

	identity_dispatcher.set_handler('v2_tokens', TokensV2())

	identity_dispatcher.import_routes()

This should look familiar to you from the index example earlier. Next,
create the tokens.py file where the TokensV2 class will live.

	from datetime import datetime
	from babelfish.identity import identity_dispatcher
	from babelfish.openstack import openstack_dispatcher

	class TokensV2(object):
    	def on_post(self, req, resp):
    	    body = req.stream.read().decode()

This is the starting point for the driver. If you refer to the Identity
API documentation, you'll see that the /v2.0/tokens endpoint responds to
POST, so we've created an on\_post() method. Next, we pull the body out
of the request stream. After that, we should authenticate the user. The
implementation of this is going to be specific to your API, but
hopefully you know how to authenticate someone. We're going to assume
that you've successfully authenticated the person and put information
about him into a dictionary called *user* and information about his
tenant account into a dictionary called *account*. From there, we just
need to build the response body based upon what the driver supports and
what the API expects.

# The Tokens Endpoint (Part 2)

The other endpoint example we're going to provide is the v2\_tokens
endpoint within the Keystone Identity API. This endpoint is important
because every OpenStack tool will first try to authenticate to Keystone
before doing anything else, so if you don't have this, you may have
problems. It also has several other interesting examples for a driver
that make it worth discussing even if you're not planning on using
Keystone.

As with the index driver, we first need to create a few things. We'll do
it in a larger batch this time:


	$ mkdir babelfish/identity/drivers/my_driver
	$ mkdir babelfish/identity/drivers/my_driver/endpoints

Create the \_\_init\_\_.py file

            index_url = identity_dispatcher.get_endpoint_url(req, 'v2_auth_index')
            v2_url = openstack_dispatcher.get_endpoint_url(req, 'v2_index')

            service_catalog = [{
               'endpoint_links': [],
               'endpoints': [{
                    'region': 'RegionOne',
                    'publicURL': v2_url + '/%s' % account['id'],
                    'privateURL': v2_url + '/v2/%s' % account['id'],
                    'adminURL': v2_url + '/v2/%s' % account['id'],
                    'internalURL': v2_url + '/v2/%s' % account['id'],
                    'id': 1,
               }],
               'type': 'compute',
               'name': 'nova',
            }, {
               'endpoint_links': [],
               'endpoints': [
                   {
                       'region': 'RegionOne',
                       'publicURL': index_url,
                       'privateURL': index_url,
                       'adminURL': index_url,
                       'internalURL': index_url,
                       'id': 1,
                   },
               ],
               'type': 'identity',
               'name': 'keystone',
            }, 
            ]

            expiration = datetime.datetime.now() + datetime.timedelta(days=1)
            access = {
                'token': {
                    'expires': expiration.isoformat(),
                    'id': token,
                    'tenant': {
                        'id': account['id'],
                        'enabled': True,
                        'description': account['companyName'],
                        'name': account['id'],
                    },
                },
                'serviceCatalog': service_catalog,
                'user': {
                    'username': user['username'],
                    'id': user['id'],
                    'roles': [
                        {'name': 'user'},
                    ],
                    'role_links': [],
                    'name': user['username'],
                },
            }

            resp.body = {'access': access}

You'll notice that this is a lot smaller than what you get back from a native OpenStack Keystone call and that's because we're not going to support many modules right now. As you add more drivers, you'll want to update this dictionary. Lastly, as before, we assign it to the response body and we're done.

# Configuring

Now that we've built a couple drivers, we need to tell the compatibility layer to use them. This is done by modifying the babelfish.conf file in the root of the installation directory. By default, the compatibility layer uses the OpenStack pass-through drivers. What we want to do instead is use our drivers for the index and identity. Open up the babelfish.conf file and it should look something like this:

    [identity]
    driver=babelfish.identity.drivers.openstack.identity

    [compute]
    driver=babelfish.compute.drivers.openstack.compute

    [image]
    driver=babelfish.image.drivers.openstack.image

    [block_storage]
    driver=babelfish.block_storage.drivers.openstack.block_storage

    [openstack]
    driver=babelfish.openstack.drivers.openstack.core

    [network]
    driver=babelfish.network.drivers.openstack.network

    [shared]
    driver=babelfish.shared.drivers.openstack.network


The file is in standard [ConfigParser](http://docs.python.org/3.3/library/configparser.html) format and should be easy to follow. All we need to do is replace the driver line for both OpenStack and Identity so that it uses the module path for our drivers instead.

    [identity]
    driver=babelfish.identity.drivers.my_driver

    [compute]
    driver=babelfish.compute.drivers.openstack.compute

    [image]
    driver=babelfish.image.drivers.openstack.image

    [block_storage]
    driver=babelfish.block_storage.drivers.openstack.block_storage

    [openstack]
    driver=babelfish.openstack.drivers.my_driver

    [network]
    driver=babelfish.network.drivers.openstack.network

    [shared]
    driver=babelfish.shared.drivers.openstack.network


## Next Steps

At this point, you have the basics of building a driver and it's a matter of expanding the functionality. Where you go next is up to you and what your goals are. But regardless of what you build next, there are a few things that can help you to be more successful.

* Use [Horizon](https://github.com/openstack/horizon) in debug mode to test your functionality. Horizon provides a good, standard GUI for interacting with OpenStack and will give you a list of target endpoints to prioritize when implementing your drivers.
* If Horizon is too broad for you, you can also use the various CLI tools provided by Nova and other modules for the same purpose. Just add the --debug flag.
* Check out the included SoftLayer drivers. We don't have full OpenStack compatibility yet, but we do have a very usable subset of commands implemented.

# Useful Tools

Building any compatibility driver is going to be a large amount of work for any provider, so we've included a few things to hopefully make the process easier.

* Within the babelfish.common directory, there are several libraries for providing common, reusable functionality for things like error handling, formatting, and nested dictionary management. If you find yourself using something else repeatedly, please let us know so that we can include it in the common toolset.
* The dispatcher includes a full set of before and after request hooks that allow you to perform common actions immediately prior to or after acting upon a request. This can allow you to centralize some common functionality. For example, the SoftLayer driver uses it to automatically set the tenant_id variable on routes that need it. All you have to do is set the tenant_id property within the request's environment dictionary and the dispatcher will automatically include it.
* The dispatcher objects include a method called get_unused_endpoints() that will provide a list of all endpoints the dispatcher knows about that you haven't attached handlers to. If you want to get an idea of your coverage, you can run that command after calling import_routes().
