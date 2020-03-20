# MIT App Inventor TFJS Extension Generator

The aim of this tool is to make it easier to generate the scaffolding needed to use a Tensorflow.js model in App Inventor.

## Quickstart

Install the App Inventor TFJS extension generator using pip:

```
pip install appinventor-tfjs
```

Create an extension prototype for Posenet:

```
python -m appinventor.tfjs posenet edu.mit.appinventor.ai.posenet.PosenetExtension
```

The output of this command will be a new directory called PosenetExtension. Within this directory, you will find a fresh git clone of the App Inventor extension template repository. The directory will have the following structure:

```
build.xml
lib
 ├─ android
 │   ├─ android.jar
 │   ├─ appcompat-v7-28.0.0.jar
 │   └─ dx.jar
 ├─ ant-contrib
 │   └─ ant-contrib-1.0b3.jar
 ├─ appinventor
 │   └─ AndroidRuntime.jar
 │   └─ AnnotationProcessors.jar
 └─ deps
README.md
src
 └─ edu
     └─ mit
         └─ appinventor
             └─ ai
                 └─ posenet
                     ├─ assets
                     │   ├─ app.js
                     │   ├─ group1-shard1of2.bin
                     │   ├─ group1-shard2of2.bin
                     │   ├─ index.html
                     │   ├─ model-stride16.json
                     │   ├─ posenet.min.js
                     │   ├─ tf-converter.min.js
                     │   ├─ tf-core.min.js
                     │   └─ VERSIONS
                     └─ PosenetExtension.java
```

Of those files, the ones under `src` are most interesting. Briefly:

* `PosenetExtension.java` - Boilerplate extension code for a TFJS extneion in App Inventor. You will want to customize it to provide model-specific behavior, such as interpreting the results before passing information back to the blocks layer.
* `app.js` - Boilerplate Javascript code to load the model and interact with the Java code in the App Inventor extension. You will need to modify this to interact correctly with the TFJS model, such as calling the correct method to start the model and interpret its output for App Inventor.
* `group-*.bin` - These are the weights at each level of the model, pulled from the TFJS model repository. The number of files will vary based on the size of the model.
* `index.html` - The index.html file loads all of the prerequisite Javascript files. It generally does not need to be modified.
* `*.min.js` - Minified Javascript code for the model and any dependencies, such as tfjs-core and tfjs-converter.
* `VERSIONS` - The VERSIONS file contains a key-value mapping the different npm modules to the versions that were retrieved. There should be one entry per min.js file.

## Usage

```
usage: python -m appinventor.tfjs [-h] [--scope SCOPE] model_name class_name

Create a TensorFlow.js-based extension for MIT App Inventor.

positional arguments:
  model_name
  class_name

optional arguments:
  -h, --help     show this help message and exit
  --scope SCOPE
```

The `model_name` argument names the Tensorflow.js model of interest. A list of pretrained models is available on [GitHub](https://github.com/tensorflow/tfjs-models). For example, if you are interested in trying the MobileNet model, you would specify `mobilenet` as the `model_name`.

The `class_name` argument specifies a fully qualified Java class name that will be used for the extension. For example, a MobileNet extension for App Inventor might have the fully qualified class name `com.example.tfjs.mobile.MobileNetExtension`. The extension generator will create this class and any intermediate packages for you.

The optional `--scope SCOPE` argument allows you to import models from npm packages that are not under the `@tensorflow-models` namespace (effectively, if `--scope` is not specified it is the same as `--scope @tensorflow-models`).

## Development

### Dependencies

You will need to create a virtual environment and install the dependencies by running. We provide instructions for macOS below.

### Create a virtualenv

#### macOS

1. Install Homebrew
2. Install pyenv

   ```shell
   brew install pyenv
   echo "eval \"\$(pyenv init -)\"" >> ~/.bash_profile
   echo "eval \"\$(pyenv virtualenv-init -)\"" >> ~/.bash_profile
   source ~/.bash_profile
   ```

3. Create a python environment using pyenv and activate it

   ```shell
   pyenv install 3.6
   pyenv virtualenv 3.6 appinventor3
   pyenv activate appinventor3
   ```

### Install dependencies

```shell
pip install -r requirements.txt
pip install .
```

## Contributing

This software is made available under the Apache Software License 2.0. You are welcome to contribute pull requests to this project via GitHub.

## License

Copyright 2020 Massachusetts Institute of Technology

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
