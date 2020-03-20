from setuptools import setup

setup(name='appinventor-tfjs',
      version='0.1.0',
      description='',
      url='',
      author='Evan Patton',
      author_email='ewpatton@mit.edu',
      license='Apache',
      packages=['appinventor.tfjs'],
      entry_points={'console_scripts': ['appinventor.tfjs = appinventor.tfjs.__main__:main']},
      include_package_data=True,
      install_requires=['certifi'])
