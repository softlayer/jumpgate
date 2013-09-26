#!/usr/bin/env python
import nose
import argparse
import os
import os.path

TEMPEST_DEFAULT_LOCATION = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'tempest')
TEMPEST_CONFIG_DEFAULT_LOCATION = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'etc', 'tempest.conf')
WHITELIST_DEFAULT_LOCATION = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'etc', 'tempest-whitelist.txt')


def get_whitelist_from_file(path):
    whitelist = []
    with open(path) as f:
        whitelist = [test.strip() for test in f.readlines()]

    # filter commented-out tests
    whitelist = filter(lambda t: not t.startswith('#') and len(t) > 0,
                       whitelist)
    return whitelist


def main():
    " Run tempests tests "
    parser = argparse.ArgumentParser(
        description='Tempest test runner for SLAPI-Stack')
    parser.add_argument('--tempest-location',
                        default=TEMPEST_DEFAULT_LOCATION,
                        help='Location of tempest tests')
    parser.add_argument('--tempest-config',
                        default=TEMPEST_CONFIG_DEFAULT_LOCATION,
                        help='Location of tempest config')
    parser.add_argument('--whitelist-location',
                        default=WHITELIST_DEFAULT_LOCATION,
                        help='Location of whitelist file')
    parser.add_argument('--disable-whitelist',
                        action='store_true',
                        help='Option to use whitelist')
    parser.add_argument('args', nargs='*', help='arguments for nosetests')
    options, unknown_args = parser.parse_known_args()

    args = [os.path.basename(__file__)] + unknown_args

    if options.disable_whitelist:
        # Pass through positional args to nosetests
        args += options.args
    else:
        # Limit tests to those in the whitelist
        whitelist = get_whitelist_from_file(options.whitelist_location)
        test_list = []
        if options.args:
            # For each user input, gather tests in our whitelist that match
            test_list = set([test
                             for test_section in options.args
                             for test in whitelist
                             if test_section in test])

            if not test_list:
                exit('No tests found with names: %s'
                     % (','.join(options.args)))
        else:
            test_list = whitelist
        args += test_list

    tempest_config = options.tempest_config
    if not os.path.isfile(tempest_config):
        exit('Tempest config file "%s" does not exist. Make sure there is a '
             'tempest config at that location.' % tempest_config)
    os.environ['TEMPEST_CONFIG'] = tempest_config

    if not os.path.exists(options.tempest_location):
        exit('Tempest path "%s" does not exist. Make sure there is a tempest '
             'checkout at that location.' % options.tempest_location)
    os.chdir(options.tempest_location)

    # Run nose
    nose.main(argv=args)


if __name__ == '__main__':
    main()
