### Contributing ###

The OpenStack Compatibility Layer and SoftLayer drivers were created and are maintained by SoftLayer, an IBM Company. We welcome anyone to submit pull requests for fixes or new features, but ask that you follow a few simple steps.

1.) All pull requests should be submitted for a reported issue or must include a detailed explanation of what's being changed. For new features, we'd prefer there already be an existing, approved issue in Github, but we're flexible.

2.) All changes should follow [PEP8](http://www.python.org/dev/peps/pep-0008/) guidelines.

3.) When contributing to a driver, your changes should not break any currently passing Tempest tests. If you introduce new functionality, please update the Tempest test whitelist to test the new functionality.