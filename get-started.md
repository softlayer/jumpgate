---
layout: pages
title: Get Started
slug: get-started
baseurl: "../"
---

# About Jumpgate

Jumpgate is a library, which acts as a translation layer to convert incoming OpenStack calls to different cloud provider's API calls.

# Quick Start

Browse these sections to start downloading, installing, configuring, and creating drivers. To learn more about configuring, deploying, and supporting Jumpgate, check out our [Developer Guide]({{ page.baseurl }}developer-guide).

## Specification

This library has been tested on Python 2.7 and Python 3.3.

## Download

Two download options are available.

*   [Download the latest release]({{ site.repo }}/archive/master.zip)
*   Clone the repo via `git clone https://github.com/softlayer/jumpgate.git`

## Install

Run the following command.

{% highlight bash %}
$ python setup.py install
{% endhighlight %}

## Configure

Jumpgate ships with two default drivers:

1. An OpenStack passthrough driver (primarily as an example)
2. A driver for the SoftLayer API

You can install or develop additional drivers to suit your particular needs. To configure Jumpgate to use a particular driver, open the `jumpgate.conf` file in the root of your installation and change the *driver* properties for each section you wish to use. If you don't want or need a particular set of endpoints, you can comment out that section and Jumpgate will not expose them.

## Start the Server
Jumpgate provides a WSGI-compatible interface. Any web server that supports WSGI can be used, such as nginx, Apache, gunicorn, uwsgi, etc. The server we've been using to test with is [gunicorn](http://gunicorn.org). An example command to get started is located in `test_server.sh`. 

{% highlight bash %}
$ ./test_server.sh
{% endhighlight %}

> Note: This requires [gunicorn to be installed](http://gunicorn.org/#quickstart) in order to run.

# Developer Guide

Our [Developer Guide]({{ page.baseurl }}developer-guide) provides an overview for configuring, deploying, and supporting Jumpgate. It's an extremely valuable resource if you're interested in creating a new driver.

# Known Issues

All known open issues are listed on [our GitHub public repo]({{ site.open_issues }}).

# Additional Documentation

*   [OpenStack API](http://docs.openstack.org/api/api-specs.html)
*   [OpenStack API Quick Reference](http://api.openstack.org/api-ref.html)
*   [Language Bindings for Python/Command-line Clients](http://docs.openstack.org/developer/language-bindings.html)
*   [SoftLayer API](http://sldn.softlayer.com/reference/softlayerapi)

{% include snippet-copyright.md %}