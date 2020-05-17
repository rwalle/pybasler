import setuptools

setuptools.setup(name='PyBasler',
    version='1.0',
    description='Python module for connecting basler cameras. Uses pypylon',
    url='http://github.com/rwalle/pybasler',
    author='Zhe Li',
    author_email='lizhe05@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=['pypylon', 'numpy'],
    test_suite='tests',
    )