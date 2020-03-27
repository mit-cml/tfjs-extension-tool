from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(name='appinventor-tfjs',
      version='0.1.1',
      description='Tool for generating App Inventor extension skeletons from Tensorflow.js models',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/mit-cml/tfjs-extension-tool',
      author='Evan W. Patton',
      author_email='ewpatton@mit.edu',
      license='Apache',
      packages=find_packages(),
      entry_points={'console_scripts': ['appinventor.tfjs = appinventor.tfjs.__main__:main']},
      python_requires='>=3.0',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'License :: OSI Approved :: Apache Software License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: JavaScript',
            'Programming Language :: Python :: 3',
            'Topic :: Education',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Software Development',
            'Topic :: Software Development :: Code Generators'
      ],
      include_package_data=True,
      install_requires=['certifi'])
