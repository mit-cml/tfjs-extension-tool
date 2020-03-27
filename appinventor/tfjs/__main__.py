#!/usr/bin/env python
# -*- mode: python; -*-

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request


TEMPLATE = os.path.join(os.path.dirname(__file__), 'template')
peer_re = re.compile(r' requires a peer of (?P<peer>[^ ]*) but none is installed')
fetch_template = """
const tf = require('@tensorflow/tfjs-core');
const model = require('%s');

async function go() {
    const oldFetch = tf.ENV.platform.fetch;
    tf.ENV.platform.fetch = path => {
        console.log(path);
        return oldFetch(path);
    }

    await model.load();
}

go();
"""


def create_project(project_name):
    subprocess.check_output(['git', 'clone', 'https://github.com/mit-cml/extension-template.git', project_name])


def install(package):
    peers = []
    process = subprocess.run(['npm', 'i', package], encoding='utf-8', universal_newlines=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    for line in io.StringIO(process.stdout):
        match = peer_re.search(line)
        if match:
            peers.append(match.group('peer'))
    return peers


def retrieve_model(model_package):
    try:
        os.mkdir('out')
    except FileExistsError:
        pass  # already exists!
    with open('retrieve.js', 'w') as f:
        f.write(fetch_template % model_package)
    print('Fetching model assets...')
    subprocess.check_output(['npm', 'i', '@tensorflow/tfjs-core'], encoding='utf-8', universal_newlines=True, stderr=None)
    output = subprocess.check_output(['node', 'retrieve.js'], encoding='utf-8', universal_newlines=True, stderr=None)
    for line in io.StringIO(output):
        if line.startswith('https://'):
            filename = line.strip().split('/')
            filename = filename[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
            print('Retrieving ' + line.strip())
            with urllib.request.urlopen(line.strip()) as response:
                with open(os.path.join('out', filename), 'wb') as out:
                    out.write(response.read())


def get_package_and_class(class_name):
    parts = class_name.split('.')
    return '.'.join(parts[:-1]), parts[-1]


def copy_assets(class_name, model_name, dependencies, package_dir):
    src_asset_dir = os.path.join(TEMPLATE, 'assets')
    dst_asset_dir = os.path.join(package_dir, 'assets')
    os.makedirs(dst_asset_dir, exist_ok=True)
    assets = []
    for dependency in dependencies:
        path = ['node_modules'] + dependency.split('/')
        if '@' in path[-1]:  # Strip version number
            path[-1] = path[-1].split('@')[0]
        for (dirname, subdirs, files) in os.walk(os.path.join(*path)):
            for file in files:
                if file.endswith('.min.js'):
                    shutil.copy(src=os.path.join(dirname, file), dst=os.path.join(dst_asset_dir, file))
                    assets.append(file)
    for (dirname, subdirs, files) in os.walk(src_asset_dir):
        for file in files:
            if file == 'app.js':
                with open(os.path.join(dirname, file)) as src:
                    with open(os.path.join(dst_asset_dir, file), 'w') as dst:
                        for line in src:
                            dst.write(line.replace('TensorflowTemplate', class_name).replace('$MODEL', model_name))
            elif file == 'index.html':
                with open(os.path.join(dirname, file)) as src:
                    with open(os.path.join(dst_asset_dir, file), 'w') as dst:
                        for line in src:
                            if 'SCRIPTS' not in line:
                                dst.write(line)
                            else:
                                for asset in assets:
                                    if asset.endswith('.min.js'):
                                        dst.write(f'    <script src="{asset}"></script>\n')
            else:
                shutil.copy(os.path.join(dirname, file), os.path.join(dst_asset_dir, file))
    return assets


def copy_model_assets(package_dir):
    result = []
    asset_dir = os.path.join(package_dir, 'assets')
    for file in os.listdir('out'):
        shutil.copy(os.path.join('out', file), os.path.join(asset_dir, file))
        result.append(file)
    return result


def copy_extension(package_dir, package_name, class_name, model, files):
    with open(os.path.join(TEMPLATE, 'TensorflowTemplate.java')) as template:
        with open(os.path.join(package_dir, f'{class_name}.java'), 'w') as out:
            for line in template:
                if line.startswith('package '):
                    out.write(f'package {package_name};\n')
                elif line.startswith("    description ="):
                    out.write(f'    description = "An extension that embeds a {model} model.",\n')
                elif line.startswith('@UsesAssets('):
                    filelist = ', '.join(files + ['index.html', 'app.js'])
                    out.write(f'@UsesAssets(fileNames = "{filelist}")\n')
                else:
                    out.write(line.replace('TensorflowTemplate', class_name))


def create_versions_file(package_dir, dependencies):
    with open(os.path.join(package_dir, 'assets', 'VERSIONS'), 'w') as f:
        with open('package-lock.json') as npmpkg:
            packageinfo = json.load(npmpkg)
        for dependency in dependencies:
            starts_with_at = dependency[0] == '@'
            if '@' in dependency[1:]:
                dependency = dependency.split('@')[1 if starts_with_at else 0]
                if starts_with_at:
                    dependency = '@' + dependency
            info = packageinfo['dependencies'][dependency]
            f.write(f'{dependency}={info["version"]}\n')


def populate_extension(fqcn, model, dependencies):
    package, class_name = get_package_and_class(fqcn)
    package_dir = os.path.join(*(['..', 'src'] + package.split('.')))
    os.makedirs(os.path.join(package_dir, 'assets'), exist_ok=True)
    files = copy_assets(class_name, model, dependencies, package_dir)
    files += copy_model_assets(package_dir)
    copy_extension(package_dir, package, class_name, model, files)
    create_versions_file(package_dir, dependencies)


def main():
    # appinventor_dir = os.environ['APPINVENTOR_DIR'] if 'APPINVENTOR_DIR' in os.environ else os.getcwd()
    # if not appinventor_dir.endswith('appinventor'):
    #     print('This module should be run from within the appinventor directory in appinventor-sources.',
    #           file=sys.stderr)
    #     sys.exit(1)
    parser = argparse.ArgumentParser(prog='appinventor.tfjs',
                                     description='Create a TensorFlow.js-based extension for MIT App Inventor.')
    parser.add_argument('--scope', default='@tensorflow-models')
    parser.add_argument('model_name')
    parser.add_argument('class_name')
    args = parser.parse_args()
    scope, model_name, fqcn = args.scope, args.model_name, args.class_name
    package_name, class_name = get_package_and_class(fqcn)
    create_project(class_name)
    os.chdir(class_name)
    with tempfile.TemporaryDirectory(dir=os.getcwd()) as work_dir:
        os.chdir(work_dir)
        model_package = f'{scope}/{model_name}'
        dependencies = []
        for peer in install(model_package):
            print(f'Installing peer package {peer}')
            install(peer)
            dependencies.append(peer)
        dependencies.append(model_package)
        retrieve_model(model_package)
        populate_extension(args.class_name, model_name, dependencies)
        os.chdir('..')
    subprocess.check_output(['ant'])
    print('Finished.')


if __name__ == '__main__':
    main()
