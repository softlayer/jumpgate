---
layout: pages
title: Contributing
slug: contributing
baseurl: "../"
---

# Contributing

Looking to be a contributor? Here's how you can help.

# Guidelines

The OpenStack Compatibility Layer and SoftLayer drivers were created and are maintained by SoftLayer, an IBM Company. We welcome anyone to submit pull requests for fixes or new features, but ask that you follow a few simple steps.

### Pull Requests

All pull requests should be submitted for a reported issue or must include a detailed explanation of what's being changed. For new features, we'd prefer there already be an existing, approved issue in Github, but we're flexible.

### Coding Standards

All changes should follow [PEP8](http://www.python.org/dev/peps/pep-0008) guidelines.

### Test Cases

When contributing to a driver, your changes should not break any currently passing Tempest tests. If you introduce new functionality, please update the Tempest test whitelist to test the new functionality.

# Contribute to Our Documents

Our docs are treated like our code. 

* We publish our public-facing content on [GitHub Pages](http://pages.github.com) and use GitHub to track and manage changes.
* Our web resources for [OpenStack Compatibility API](http://softlayer.guthub.io/slapi-stack) are managed under the `gh-pages` [branch](https://github.com/softlayer/slapi-stack/tree/gh-pages).

{% include community.md %}

{% include copyright.md %}
