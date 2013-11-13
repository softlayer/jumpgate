---
layout: pages
title: Release Notes
slug: release-notes
baseurl: "../"
---

# Overview

The release for Chef-OpenStack is now available on [GitHub]({{ site.repo }}). Browse the sections below to read more about what’s available.

## Summary

The details regarding the project are below.

<div class="table-responsive" id="component-table">
  <table class="table table-hover" id="no-borders">
    <thead>
      <tr>
        <th>Reference</th>
        <th>Details</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Release Phase</td>
        <td>Phase 1</td>
      </tr>
      <tr>
        <td>Release Version (Havana)</td>
        <td>v0.3.3</td>
      </tr>
      <tr>
        <td>Release Version (Grizzly)</td>
        <td>v0.2.0</td>
      </tr>
      <tr>
        <td>Product Line</td>
        <td>OpenStack Compatibility API</td>
      </tr>
    </tbody>
  </table>
</div>

## Milestones

The key milestones for this project are outlined below.

<div class="table-responsive" id="component-table">
  <table class="table table-hover" id="no-borders">
    <thead>
      <tr>
        <th>Event</th>
        <th>Date</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Kickoff</td>
        <td>September 18, 2013</td>
      </tr>
      <tr>
        <td>Dev Complete</td>
        <td>October 31, 2013</td>
      </tr>
      <tr>
        <td>Public Unveiling</td>
        <td>November 4, 2013</td>
      </tr>
    </tbody>
  </table>
</div>

# Features

The first public version is generally available as an open source project. It includes four OpenStack components:

* Keystone (authentication)
* Nova (compute)
* Glance (images)
* Horizon (dashboard)

# Known Issues

All known open issues are listed on [our GitHub public repo]({{ site.open_issues }}).

# Download

Two download options are available.

*   [Download the latest release](https://github.com/softlayer/chef-openstack/archive/master.zip)
*   Clone the repo: `git clone https://github.com/softlayer/chef-openstack.git`

# Install

Our [Getting Started Guide]({{ page.baseurl }}getting-havana) provides an overview for installing, configuring, deploying, and supporting OpenStack and Chef.

{% include community.md %}