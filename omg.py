#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OMG
#    Copyright (c) 2014 Francesco OpenCode Apruzzese All Rights Reserved.
#                       www.e-ware.org
#                       opencode@e-ware.org
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from os import mkdir
from os.path import exists
from shutil import copyfile
import argparse
import importlib
from datetime import datetime


def stupid_header():

    return'''----------------------------------------------------------
                          OMG                              
    "OH MY GOD! (formarly OpenERP/Odoo Module Generator)"    
     Francesco OpenCode Apruzzese <opencode@e-ware.org>     
----------------------------------------------------------'''


def render_file(file_path, args):

    with open(file_path, 'r') as file_content:
        content = file_content.read()
        content = content.replace('{# year #}', str(datetime.now().year))
        content = content.replace('{# name #}', args.name.replace('_', ' '))
        content = content.replace('{# author #}', args.author or '')
        depends = ''
        for depend in (args.depends_module and
                       args.depends_module.split(',') or []):
            depends = '%s\'%s\', ' % (depends, depend)
        content = content.replace('{# depends #}', depends)
    new_file = open(file_path, 'w')
    new_file.write(content)
    new_file.close()
    return True


def main(args):

    # ----- Best function in the python (and maybe PHP) world!
    print stupid_header()
    # ----- create the module base path
    module_path = args.destination_path
    if not module_path.endswith('/'):
        module_path = '%s/%s/' % (module_path, args.name)
    # ----- check if path exists
    if exists(module_path):
        print 'Path %s exists in %s, yet!' % (args.name, args.destination_path)
        return False
    mkdir(module_path)
    print 'Created path %s' % (module_path)
    # ----- copy basic file in new module
    for basic_file in ['__init__.py', '__openerp__.py']:
        file_src = 'version/7/%s' % (basic_file)
        file_dest = '%s%s' % (module_path, basic_file)
        print 'Generate %s' % (file_dest)
        copyfile(file_src, file_dest)
        render_file(file_dest, args)
    # ----- copy VCS ignore file
    vcs = args.git and 'git' or args.bazaar and 'bzr' or False
    if vcs:
        file_src = 'version/7/%signore' % (vcs)
        file_dest = '%s%signore' % (module_path, vcs)
        print 'Generate %s ignore file' % (vcs)
        copyfile(file_src, file_dest)
    # ----- create a subdirectory for every inherit module
    for depend in (args.depends_module and
                   args.depends_module.split(',') or []):
        # ----- Create directory and files
        print 'Generate subdirectory for %s' % (depend)
        mkdir('%s%s' % (module_path, depend))
        file_src = 'version/7/__init__.py'
        file_dest = '%s%s/__init__.py' % (module_path, depend)
        copyfile(file_src, file_dest)
        render_file(file_dest, args)
        # ----- update init main file
        with open('%s__init__.py' % (module_path), "a") as init_file:
            init_file.write('import %s\n' % (depend))
        # ----- update subdirectory init file
        with open('%s%s/__init__.py' % (module_path,
                                        depend), "a") as init_file:
            init_file.write('import %s\n\n' % (depend))
        # ----- create file for inherit class
        file_src = 'version/7/inherit.py'
        file_dest = '%s%s/%s.py' % (module_path, depend, depend)
        copyfile(file_src, file_dest)
        render_file(file_dest, args)
    # ----- create file for new class
    if args.empty_class:
        file_src = 'version/7/class.py'
        file_dest = '%s%s.py' % (module_path, args.name)
        copyfile(file_src, file_dest)
        render_file(file_dest, args)
    # ----- Create other basic directories
    for other_path in ['report', 'i18n', 'security']:
        print 'Generate subdirectory %s' % (other_path)
        mkdir('%s%s' % (module_path, other_path))
    # ----- Fly away!
    return True


if __name__ == "__main__":

    # ----- Parse terminal arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='Module name'),
    parser.add_argument('destination_path', help='Module desination'),
    #parser.add_argument('-s', '--generate-config', dest='generate_config',
    #                    action='store_true',
    #                    help='Generate an example config file in user home'),
    #parser.add_argument('-o', '--software-version', dest='software_version',
    #                    help='Set software version to use as base \
    #                    (7 or 8 supported)')
    parser.add_argument('-g', '--git', dest='git', action='store_true',
                        help='Insert git useful files')
    parser.add_argument('-b', '--bazaar', dest='bazaar', action='store_true',
                        help='Insert bazaar useful files')
    #parser.add_argument('-c', '--config', dest='config_file',
    #                    help='Set a config file path')
    parser.add_argument('-m', '--depends-module', dest='depends_module',
                        help='Set depend modules separated by comma')
    parser.add_argument('-e', '--empty-class', dest='empty_class',
                        action='store_true',
                        help='Create an empty structure for new class')
    parser.add_argument('-a', '--author', dest='author',
                        help='Author\'s mail used in copyright section')
    args = parser.parse_args()
    main(args)
