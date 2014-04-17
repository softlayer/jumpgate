from setuptools import setup, find_packages

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
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'falcon>=0.1.8',
        'requests',
        'six>=1.4.1',
        'oslo.config>=1.2.0',
        'softlayer',
        'pycrypto',
        'iso8601',
    ],
    setup_requires=[],
    test_suite='nose.collector',
    entry_points={'console_scripts': ['jumpgate = jumpgate.cmd:main']}
)
