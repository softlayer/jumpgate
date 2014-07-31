from setuptools import setup, find_packages
import sys

install_requires_list = [
    'falcon>=0.1.8',
    'requests',
    'six>=1.7',
    'oslo.config>=1.2.0',
    'softlayer',
    'pycrypto',
    'iso8601',
]

if sys.version_info[0] < 3:
    install_requires_list.append('py2-ipaddress')

setup(
    name='jumpgate',
    version='0.1',
    description='OpenStack Transation Layer for cloud providers',
    long_description=open('README.rst', 'r').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.3',
    ],
    author_email='innovation@softlayer.com',
    url='http://sldn.softlayer.com',
    license='MIT',
    packages=find_packages(exclude=['*.tests']),
    data_files=[('etc', ['etc/identity.templates',
                         'etc/identity_v3.templates',
                         'etc/jumpgate.conf',
                         'etc/tempest.conf.sample',
                         'etc/volume_types.json',
                         'etc/flavor_list.json'])],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires_list,
    setup_requires=[],
    test_suite='nose.collector',
    entry_points={'console_scripts': ['jumpgate = jumpgate.cmd_main:main']}
)
