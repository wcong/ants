from setuptools import setup, find_packages


setup(
    name='ants',
    version='0.0.1',
    url='https://github.com/wcong/ants',
    description='open source, distributed, restful crawler engine',
    long_description=open('README.rst').read(),
    author='wcong',
    maintainer='Wcong',
    maintainer_email='wc19920415@gmail.com',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['ants = ants.bootstrap:execute']
    },
    classifiers=[
        'Framework :: Scrapy',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'Twisted>=10.0.0',
        'w3lib>=1.8.0',
        'queuelib',
        'lxml',
        'pyOpenSSL',
        'cssselect>=0.9',
        'six>=1.5.2',
    ],
)
