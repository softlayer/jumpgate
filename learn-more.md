---
layout: pages
title: Learn More
slug: learn-more
baseurl: "../"
---

# Our Work

Our combustion begins at the grassroots level with free and open source software. Not only do we use it, we’re also firm believers in the openness of development and collaboration in order to make viable and sustainable products. That’s why we’re thrilled to be contributors toward the development of OpenStack.

All our work is happening publicly on GitHub, and we invite everyone to join in.

{% include snippet-community.md %}

# Contributor Guidelines

The OpenStack Compatibility Layer and SoftLayer drivers were created and are maintained by SoftLayer, an IBM Company. We welcome anyone to submit pull requests for fixes or new features, but ask that you follow a few simple steps.

## Coding Standards

All changes should follow [PEP8](http://www.python.org/dev/peps/pep-0008) guidelines.

## Pull Requests

Submit all pull requests for a reported issue or include a detailed explanation of what’s changing. 

## Feature Requests

For new features, we’d prefer there already be an existing, approved issue in GitHub, but we’re flexible.

## Issues

Have an issue to report? Here are some guidelines to read first.

* Scroll through our list of [closed issues]({{ site.closed_issues }}) to see if yours has already been resolved or reported.
* Be sure to include any relevant information, such as the OpenStack release (Grizzly, Havana), what components you use, when it was deployed, and so on.
* Create a [gist](https://gist.github.com) of the code causing the issue, as well as any error messages, and include its URL in the issue report.
* When you're ready, create a [new issue on GitHub]({{ site.open_issues }}).

## Test Cases

When contributing to a driver, your changes should not break any currently passing Tempest tests. If you introduce new functionality, please update the Tempest test whitelist to test the new functionality.

{% include snippet-versioning.md %}

{% include snippet-docs.md %}

{% include snippet-copyright.md %}
