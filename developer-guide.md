---
layout: pages
title: Developer Guide
slug: developer-guide
baseurl: "../"
---

# Introduction

Our intent is to provide an easy way to make the OpenStack API compatible with any existing cloud products. This is accomplished through a series of drivers that are specific to each cloud provider.

If you're reading this, we assume you’re interested in adding OpenStack API compatible driver to an existing public or private cloud provider.

## Before You Start

Here are a few things to take into account before creating a new driver:

1. Jumpgate was written primarily for Python 2.7/Python 3.3. Your drivers will need to work with these versions as well.
2. Drivers are created as a series of objects for the [Falcon framework](http://falconframework.org). You should be familiar with both Falcon and REST APIs in general.
3. You need to be familiar with the expected [OpenStack API](http://api.openstack.org/api-ref.html) JSON. Jumpgate provides the endpoint mappings for you, but doesn’t handle the building of valid responses.

Once you have these things, you’re ready to begin creating your driver.

# Creating Your Driver

You have many places where you could begin creating your first driver, but we've found starting with the compute index and the Identity driver (Keystone) to be the easiest. To give you the general idea, we're going to cover how to create a couple endpoints. From there, you can use the SoftLayer driver as a further example of other endpoints, should you need it.

Note that there are no restrictions on how you create your driver as long as you make it work with the Falcon framework. You are free to use whatever libraries, tools, and folder layout you are most comfortable with. For consistency, we’ll use the same style as the SoftLayer driver, but you are not required to do this for your driver.

## The Starting Point

The first step in creating your driver is deciding where to create it. You can create it almost anywhere as long as: 

1. It will be in your Python path
2. It can be imported by Jumpgate

We'll start by creating a small compute driver that implements the index endpoint (`/v2/`).

{% highlight bash %}
$ mkdir jumpgate/compute/drivers/my_driver
{% endhighlight %}

Next, we're going to create a \_\_init\_\_.py within that directory. Here, you could jam all of your code into it, but that's going to get extremely clunky for some projects (such as Nova Compute). And since Jumpgate loads this file, we're going to be importing classes from other modules instead.

To start, make this the contents of your \_\_init\_\_.py file:

{% highlight python %}
from .index import IndexV2

def setup_routes(app, disp):
    disp.set_handler('v2_index', IndexV2(disp))
{% endhighlight %}

Let's look at each section. First we import the IndexV2 class. This is the actual driver class we'll be developing for the /v2 endpoint. We'll cover it in a moment.

Next, we implement a `setup_routes()` method which takes two arguments: `app` and `disp`. `app` is an instance of jumpgate.api.Jumpgate which is likely the only instance. This enables us to attach global hooks (before and after) and gives us a clean way to access jumpgate configuration. `disp` is an instance of `jumpgate.common.dispatcher.Dispatcher`. The `Dispatcher.set_handler()` method takes two arguments: The endpoint name and the responder object for to handle that endpoint. Each endpoint that OpenStack supports has a unique name so that you can refer to it without having to know exactly what the URL is. You can either open up the dispatcher to get a list of all of the endpoint names or check out our docs on GitHub to get a list there. The handler is an instance of IndexV2 that we imported earlier.

## The Index Endpoint

Now that the driver created, we need to build a response handler. As noted above, we're starting with the v2_index endpoint, which corresponds to the /v2 path. If you refer to the [OpenStack API](http://api.openstack.org/api-ref.html) docs, you'll find a /v2 endpoint for multiple APIs. The one we're going to concern ourselves with right now is within the [Compute API](http://api.openstack.org/api-ref-compute.html). If you read the details for the section, you'll find out that it doesn't need a request body and the response JSON is straightforward. We could copy the document from the docs exactly and have a valid response, but there are a couple problems with this:

1. It has URLs in it
2. It doesn't represent the functionality our driver actually supports.

When implementing things like the index endpoint (and the tokens endpoint later), it's extremely important to remember that the output is dependent upon what your driver *actually* supports. In this case, we're not going to worry about v3 support and we're going to add in v1 support (to make using Horizon easier).

To start, create the index.py where our IndexV2 class will reside. Start by putting the following within the index.py file:

{% highlight python %}
class IndexV2(object):
    def __init__(self, disp):
        self.disp = disp

    def on_get(self, req, resp):
        versions = [{
            'id': 'v2.0',
            'links': [{
                'href': self.disp.get_endpoint_url(req, 'v2_index'),
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
                 'href': self.disp.get_endpoint_url(req, 'v1_index'),
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
{% endhighlight %}

Response handlers are plain objects and don't need to inherit from any particular class or interface. Per the [Compute API](http://api.openstack.org/api-ref-compute.html) documentation, we know that this endpoint handles the GET verb, so we create an `on_get()` function. This is how the [Falcon framework](http://falconframework.org) handles responses. The contents of the function are what we're going to do to serve this endpoint. This should look very similar to the sample within the API docs, though you'll see we've added the v1 support as we discussed and we're not hardcoding URLs.

Because dispatchers handle endpoints, they also know how to build URLs. This is handy because it provides a level of abstraction between your driver and the OpenStack API itself so that if something changed in the future or Jumpgate switched hosts, you shouldn't need to change any of your driver code. To get the URL for a particular endpoint, call the `get_endpoint_url()` method on the dispatcher and pass in the Falcon request object and the identifier for the endpoint. If the endpoint's URL has variables within it (as a lot of the Nova compute endpoints do), you pass them in as keyword arguments. The only exception to this is the tenant ID, which we'll discuss later. Each dispatcher only knows about its own endpoints (they're contained as properties of the object), so you need to use the appropriate one when building your endpoint URL.

The very last thing the function does is assign a body to the response object. This should conform to the expected format within the OpenStack API documentation. Assuming you provide a valid Python dictionary, Jumpgate will automatically JSON encode it for you. Note that the default status code is 200. If you need to assign a different status code, you should refer to the Falcon docs or look at the examples within the SoftLayer driver.

## The Tokens Endpoint

The other endpoint example we're going to provide is the v2_tokens endpoint within the Keystone Identity API. This endpoint is important because every OpenStack tool will first try to authenticate to Keystone before doing anything else, so if you don't have this, you may have problems. It also has several other interesting examples for a driver that make it worth discussing even if you're not planning on using Keystone.

As with the index driver, we first need to create a few things. We'll do it in a larger batch this time:

{% highlight bash %}
$ mkdir jumpgate/identity/drivers/my_driver
{% endhighlight %}

Create the \_\_init\_\_.py file

{% highlight python %}
from .tokens import TokensV2

def setup_routes(app, disp):
    disp.set_handler('v2_tokens', TokensV2())
{% endhighlight %}

This should look familiar to you from the index example earlier. Next,
create the tokens.py file where the TokensV2 class will live.

{% highlight python %}
from datetime import datetime

class TokensV2(object):
    def __init__(self, app):
        self.app = app

    def on_post(self, req, resp):
        body = req.stream.read().decode()
{% endhighlight %}

This is the starting point for the driver. If you refer to the Identity API documentation, you'll see that the /v2.0/tokens endpoint responds to POST, so we've created an `on_post()` method. Next, we pull the body out of the request stream. After that, we should authenticate the user. The implementation of this is going to be specific to your API, but hopefully you know how to authenticate someone. We're going to assume that you've successfully authenticated the person and put information about him into a dictionary called *user*, information about his tenant account into a dictionary called *account* and a string which represents enough information to represent an authenticated session called *token*. From there, we just need to build the response body based upon what the driver supports and what the API expects.

<div class="alert alert-info">
Note: This is a continuation of the previous snippet.
</div>

{% highlight python %}
    index_url = self.app.get_dispatcher('identity').get_endpoint_url(req, 'v2_auth_index')
    v2_url = self.app.get_dispatcher('compute').get_endpoint_url(req, 'v2_index')

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
{% endhighlight %}

You'll notice that this is a lot smaller than what you get back from a native OpenStack Keystone call and that's because we're not going to support many modules right now. As you add more drivers, you'll want to update this dictionary. Lastly, as before, we assign it to the response body and we're done.

## Configuring

Now that we've built a couple drivers, we need to tell Jumpgate to use them. This is done by modifying the jumpgate.conf file in the root of the installation directory. By default, Jumpgate uses the OpenStack passthrough drivers. What we want to do instead is use our drivers for the index and identity. Open up the jumpgate.conf file. It should look something like this:

{% highlight bash %}
[identity]
driver=jumpgate.identity.drivers.openstack

[compute]
driver=jumpgate.compute.drivers.openstack

[image]
driver=jumpgate.image.drivers.openstack

[block_storage]
driver=jumpgate.block_storage.drivers.openstack

[network]
driver=jumpgate.network.drivers.openstack
{% endhighlight %}


The file is in standard [ConfigParser](http://docs.python.org/3.3/library/configparser.html) format and should be easy to follow. All we need to do is replace the driver line for both Compute and Identity so that it uses the module path for our drivers instead.

{% highlight bash %}
[identity]
driver=jumpgate.identity.drivers.my_driver

[compute]
driver=jumpgate.compute.drivers.my_driver

[image]
driver=jumpgate.image.drivers.openstack

[block_storage]
driver=jumpgate.block_storage.drivers.openstack.block_storage

[network]
driver=jumpgate.network.drivers.openstack

{% endhighlight %}

## Next Steps

At this point, you have the basics of creating a driver. Now, it’s just a matter of expanding the functionality. Where you go next is up to you and what your goals are. Regardless of what you create next, here are a few things to help you to be more successful.

* Use [Horizon](https://github.com/openstack/horizon) in debug mode to test your functionality. Horizon provides a good, standard GUI for interacting with OpenStack and will give you a list of target endpoints to prioritize when implementing your drivers.
* If Horizon is too broad for you, you can also use the various CLI tools provided by Nova and other modules for the same purpose. Just add the `-debug` flag.
* Check out the included SoftLayer drivers. We don't have full OpenStack compatibility yet, but we do have a very usable subset of commands implemented.

# Useful Tools

Building any compatibility driver is going to be a large amount of work for any provider, so we've included a few things to hopefully make the process easier.

* Within the jumpgate.common directory, there are several libraries for providing common, reusable functionality for things like error handling, formatting, and nested dictionary management. If you find yourself using something else repeatedly, please let us know so that we can include it in the common toolset.
* The dispatcher includes a full set of before and after request hooks that allow you to perform common actions immediately prior to or after acting upon a request. This can allow you to centralize some common functionality. For example, the SoftLayer driver uses it to automatically set the `tenant_id variable` on routes that need it. All you have to do is set the `tenant_id property` within the request's environment dictionary and the dispatcher will automatically include it.
* The dispatcher objects include a method called `get_unused_endpoints()` that will provide a list of all endpoints the dispatcher knows about that you haven't attached handlers to. If you want to get an idea of your coverage.

# Compatibility

Each section below includes the following compatibility references for the SoftLayer driver:

* Identity (Keystone)
* Compute (Nova)
* Images (Glance)
* Block Storage (Cinder)

## Identity

This table includes compatibility references for Identity (Keystone).

<div class="table-responsive">
  <table class="table table-bordered table-hover">
    <thead>
      <tr>
        <th>Verb</th>

        <th>Endpoint</th>

        <th>Available</th>

        <th>Notes</th>
      </tr>
    </thead>

    <tbody>
      <tr>
        <td>GET</td>

        <td>v2.0</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2.0/extensions</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2.0/extensions/{alias}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>POST</td>

        <td>v2.0/tokens</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>HEAD</td>

        <td>v2.0/tokens/{tokenId}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2.0/tokens/tenants</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2.0/users/</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2.0/users/{user_id}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2.0/users/{user_id}/roles</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2.0/tenants</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2.0/tenants/{tenantId}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2.0/tenants/{tenantId}/users/{userId}/roles</td>

        <td>No</td>

        <td></td>
      </tr>
    </tbody>
  </table>
</div>

## Compute

This table includes compatibility references for Compute (Nova).

<div class="table-responsive">
  <table class="table table-bordered table-hover">
    <thead>
      <tr>
        <th>Verb</th>

        <th>Endpoint</th>

        <th>Available</th>

        <th>Notes</th>
      </tr>
    </thead>

    <tbody>
      <tr>
        <td>GET</td>

        <td>v2</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/extensions</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/extensions/{alias}</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/limits</td>

        <td>Mocked</td>

        <td>Hardcoded to garbage data. This would effect Horizon's neat graphical displays.</td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/servers</td>

        <td>Yes</td>

        <td>Missing: public network only, direct IP allocation</td>
      </tr>

      <tr>
        <td>POST</td>

        <td>v2/{tenant_id}/servers</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/servers/detail</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/servers/{server_id}</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>PUT</td>

        <td>v2/{tenant_id}/servers/{server_id}</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>DELETE</td>

        <td>v2/{tenant_id}/servers/{server_id}</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>PUT</td>

        <td>v2/{tenant_id}/servers/{server_id}/metadata</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>POST</td>

        <td>v2/{tenant_id}/servers/{server_id}/metadata</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/servers/{server_id}/metadata</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/servers/{server_id}/metadata/{key}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>PUT</td>

        <td>v2/{tenant_id}/servers/{server_id}/metadata/{key}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>DELETE</td>

        <td>v2/{tenant_id}/servers/{server_id}/metadata/{key}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>POST</td>

        <td>v2/{tenant_id}/servers/{server_id}/action</td>

        <td>Yes</td>

        <td>Missing: suspend/unsuspend/console log/change password/resize/confirmResize/revertResize</td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/servers/ips</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/servers/ips/{network_id}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/images</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/images/detail</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/images/{image_id}</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>POST</td>

        <td>v2/{tenant_id}/images/{image_id}</td>

        <td>No</td>

        <td>Missing: Importing images, creating 'empty' image records to be populated later</td>
      </tr>

      <tr>
        <td>PUT</td>

        <td>v2/{tenant_id}/images/{image_id}/metadata</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>POST</td>

        <td>v2/{tenant_id}/images/{image_id}/metadata</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/images/{image_id}/metadata</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/images/{image_id}/metadata/{key}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/images/{image_id}/metadata/{key}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>DELETE</td>

        <td>v2/{tenant_id}/images/{image_id}/metadata/{key}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/flavors</td>

        <td>Mocked</td>

        <td>This is currently hardcoded until we determine how we're going to support flavors.</td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/flavors/detail</td>

        <td>Mocked</td>

        <td>This is currently hardcoded until we determine how we're going to support flavors.</td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/flavors/{flavor_id}</td>

        <td>Mocked</td>

        <td>This is currently hardcoded until we determine how we're going to support flavors.</td>
      </tr>
    </tbody>
  </table>
</div>

## Images

This table includes compatibility references for Images (Glance).

<div class="table-responsive">
  <table class="table table-bordered table-hover">
    <thead>
      <tr>
        <th>Verb</th>

        <th>Endpoint</th>

        <th>Available</th>

        <th>Notes</th>
      </tr>
    </thead>

    <tbody>
      <tr>
        <td>GET</td>

        <td>v2/schemas/images</td>

        <td>Mocked</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/schemas/image</td>

        <td>Mocked</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/images</td>

        <td>Yes</td>

        <td>Need to understand how this differs from /v2/{tenant_id}/images</td>
      </tr>

      <tr>
        <td>POST</td>

        <td>v2/images</td>

        <td>No</td>

        <td>Mocked, but not even remotely functional</td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/images/{image_id}</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>PATCH</td>

        <td>v2/images/{image_id}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>DELETE</td>

        <td>v2/images/{image_id}</td>

        <td>No</td>

        <td>Mocked, but does nothing</td>
      </tr>

      <tr>
        <td>PUT</td>

        <td>v2/images/{image_id}/file</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/images/{image_id}/file</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>POST</td>

        <td>v2/images/{image_id}/tags/{tag}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>DELETE</td>

        <td>v2/images/{image_id}/tags/{tag}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v1/images</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>POST</td>

        <td>v1/images</td>

        <td>No</td>

        <td>Mocked, but not functional</td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v1/images/detail</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v1/images/{image_id}</td>

        <td>Yes</td>

        <td></td>
      </tr>

      <tr>
        <td>PUT</td>

        <td>v1/images/{image_id}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>DELETE</td>

        <td>v1/images/{image_id}</td>

        <td>No</td>

        <td>Mocked, but does nothing</td>
      </tr>

      <tr>
        <td>PUT</td>

        <td>v1/images/{image_id}/members</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>PUT</td>

        <td>v1/images/{image_id}/members/{owner}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>DELETE</td>

        <td>v1/images/{image_id}/members/{owner}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v1/shared-images/{owner}</td>

        <td>No</td>

        <td></td>
      </tr>
    </tbody>
  </table>
</div>

## Block Storage

This table includes compatibility references for Block Storage (Cinder).

<div class="table-responsive">
  <table class="table table-bordered table-hover">
    <thead>
      <tr>
        <th>Verb</th>

        <th>Endpoint</th>

        <th>Available</th>

        <th>Notes</th>
      </tr>
    </thead>

    <tbody>
      <tr>
        <td>POST</td>

        <td>v2/{tenant_id}/volumes</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/volumes</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/volumes/detail</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/volumes/{volume_id</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>PUT</td>

        <td>v2/{tenant_id}/volumes/{volume_id}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>DELETE</td>

        <td>v2/{tenant_id}/volumes/{volume_id}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/types</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/types/{volume_type_id}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>POST</td>

        <td>v2/{tenant_id}/snapshots</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/snapshots</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/snapshots/detail</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>GET</td>

        <td>v2/{tenant_id}/snapshots/{snapshot_id}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>PUT</td>

        <td>v2/{tenant_id}/snapshots/{snapshot_id}</td>

        <td>No</td>

        <td></td>
      </tr>

      <tr>
        <td>DELETE</td>

        <td>v2/{tenant_id}/snapshots/{snapshot_id}</td>

        <td>No</td>

        <td></td>
      </tr>
    </tbody>
  </table>
</div>

# Additional Documentation

*   [OpenStack API](http://docs.openstack.org/api/api-specs.html)
*   [OpenStack API Quick Reference](http://api.openstack.org/api-ref.html)
*   [Language Bindings for Python/Command-line Clients](http://docs.openstack.org/developer/language-bindings.html)
*   [SoftLayer API](http://sldn.softlayer.com/reference/softlayerapi.html)
