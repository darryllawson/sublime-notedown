import os
from os.path import abspath, dirname, isdir, join
from shutil import copytree, ignore_patterns, rmtree

dest_path = join(os.environ['HOME'],
                 'Library/Application Support/Sublime Text 3/Packages/',
                 'Notedown')
if isdir(dest_path):
    print('Removing existing Notedown installation')
    rmtree(dest_path)

print('Installing Notedown to {}'.format(dest_path))
copytree(abspath(join(dirname(__file__), os.pardir)), dest_path,
         ignore=ignore_patterns('.git', '__pycache__'))
