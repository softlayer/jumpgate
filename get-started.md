---
layout: pages
title: Get Started
slug: get-started
baseurl: "../"
---

# About

Jumpgate is a library, which acts as a translation layer to convert incoming OpenStack calls to different cloud provider's API calls.

# Specification

This library has been tested on **Python 2.7** and **Python 3.3**.

# Get Started

Browse the following sections to learn how to download, install, configure, and create drivers.

## Download

Two download options are available.

*   [Download the latest release]({{ site.repo }}/archive/master.zip)
*   Clone the repo via `git clone https://github.com/softlayer/jumpgate.git`

## Install

After downloading the source, run the following command.

{% highlight bash %}
$ python setup.py install
{% endhighlight %}

## Configure

After you download Jumpgate, configure it to use the appropriate drivers for your chosen target API. 

Jumpgate ships with two default drivers:

1. An OpenStack passthrough driver (primarily as an example)
2. A driver for the SoftLayer API

You can install or develop additional drivers to suit your particular needs. To configure Jumpgate to use a particular driver, open the `jumpgate.conf` file in the root of your installation and change the *driver* properties for each section you wish to use. If you don't want or need a particular set of endpoints, you can comment out that section and Jumpgate will not expose them.

## Start the server
Jumpgate provides a WSGI-compatible interface so any web server which supports WSGI can be used including nginx, Apache, gunicorn, uwsgi, etc. The server we've been using to test with is gunicorn. An example command to get started is located in `test_server.sh`. This requires gunicorn to be installed to run.

{% highlight bash %}
$ ./test_server.sh
{% endhighlight %}


# Developer Guide

Our [Developer Guide]({{ page.baseurl }}developer-guide) provides an overview for configuring, deploying, and supporting Jumpgate. It's an extremely valuable resource if you're interested in creating a new driver.

# Known Issues

All known open issues are listed on [our GitHub public repo]({{ site.open_issues }}).

{% include additional-docs.md %}
{% include copyright.md %}