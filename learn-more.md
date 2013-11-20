---
layout: pages
title: Learn More
slug: learn-more
baseurl: "../"
---

# About Our Development

Our combustion began at the grassroots level with free and open source software. Not only do we use it regularly, we also believe in the openness of development and collaboration as a means to producing viable and sustainable products. That’s why we’re thrilled to be contributors toward the development of OpenStack. 

All our work is happening publically on GitHub, and we invite everyone to join in. If you're looking to be a contributor, here's how you can help.

# Guidelines

The OpenStack Compatibility Layer and SoftLayer drivers were created and are maintained by SoftLayer, an IBM Company. We welcome anyone to submit pull requests for fixes or new features, but ask that you follow a few simple steps.

## Pull Requests

All pull requests should be submitted for a reported issue or must include a detailed explanation of what's being changed. For new features, we'd prefer there already be an existing, approved issue in Github, but we're flexible.

## Coding Standards

All changes should follow [PEP8](http://www.python.org/dev/peps/pep-0008) guidelines.

## Test Cases

When contributing to a driver, your changes should not break any currently passing Tempest tests. If you introduce new functionality, please update the Tempest test whitelist to test the new functionality.

## Feature Requests

We are not actively accepting community requests. We are, however, accepting any reproducible issues found within the {{ site.project }} core.

## Issues

Have an issue to report? Here are some guidelines to read through first.

### Check the list of closed issues

Scroll through our list of [closed issues]({{ site.closed_issues }}) to see if yours has already been resolved or reported.

### Provide as much information as possible

Be sure to include any relevant information, such as the OpenStack release (Grizzly, Havana), which version, what components you use, when it was deployed, and so on.

### Use Gist to help explain the issue

Create a [gist](https://gist.github.com) of the code causing the issue, as well as any error messages, and include its URL in the issue report.

### Open a new issue

Create a [new issue on GitHub]({{ site.open_issues }}).

# Contribute to Our Documents

We treat our docs like we treat our code. And like our code, we invite everyone to join in.

* We publish our Getting Started guide on [GitHub Pages](http://pages.github.com) and use GitHub to track and manage changes.
* Our web resources for [Jumpgate](http://softlayer.guthub.io/jimpgate) are managed under the `gh-pages` [branch](https://github.com/softlayer/jumpgate/tree/gh-pages).

{% include community.md %}
{% include copyright.md %}