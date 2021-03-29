#!/usr/bin/pytthon3
""" Diswalk Class """
import os
# import shutil as shu

class diskwalk():
    """API for getting directory walking collections"""

    def __init__(self, path):
        if isinstance(path, (str, dict)):
            if isinstance(path, str):
                self.options = {'path': path, 'dbg': False}
            elif isinstance(path, dict):
                if 'path' in path.keys() and isinstance(path['path'], str):
                    self.options = path.copy()
                else:
                    raise ValueError("path must exist and be str")

            if 'ignore' not in self.options.keys():
                self.options['ignore'] = []
            if 'delete' not in self.options.keys():
                self.options['delete'] = {'filetype': [], 'regex': []}
            if 'dbg' not in self.options.keys():
                self.options['dbg'] = False

            self.path_collection = []
        else:
            raise ValueError("diskwalk requires str or dict")


    def enumeratePaths(self):
        """Returns the path to all the files in a directory as a list"""
        for dirpath, _, filenames in os.walk(self.options['path']):
            for filename in filenames:
                fullpath = os.path.join(dirpath, filename)
                base_dir_ind = self._test_string_start(fullpath)
                if not base_dir_ind:
                    self.path_collection.append(fullpath)

        return self.path_collection

    def enumerateFiles(self):
        """Returns all the files in a directory as a list"""
        file_collection = []
        for dirpath, dirnames, filenames in os.walk(self.options['path']):
            for file in filenames:
                file_collection.append(file)

        return file_collection

    def enumerateDir(self):
        """Returns all the directories in a directory as a list"""
        dir_collection = []
        for dirpath, dirnames, _ in os.walk(self.options['path']):
            base_dir_ind = self._test_string_start(dirpath)

            if dirpath not in self.options['ignore'] and not base_dir_ind:
                for dir1 in dirnames:
                    dir_fnl = os.sep.join([dirpath, dir1])
                    if dir_fnl not in self.options['ignore']:
                        dir_collection.append(dir_fnl)
                    else:
                        if 'dbg' in self.options and self.options['dbg']:
                            print("excluding %s" % (dir_fnl))
            else:
                if 'dbg' in self.options and self.options['dbg']:
                    print("excluding subdir %s" % (dirpath))
        return dir_collection

    def cleanseDir(self, dryrun=True):
        ''' Removes files eeting criteria specficed in options['delete'] '''
        deletes = []

        if 'delete' in self.options.keys() and isinstance(self.options['delete'], dict):
            if not self.path_collection:
                self.enumeratePaths()

            if 'filetype' in self.options['delete'].keys() and\
                    isinstance(self.options['delete']['filetype'], list):

                for itm in self.path_collection:
                    itm_list = itm.split('.')
                    if itm_list[-1] in self.options['delete']['filetype']:

                        deletes.append(itm)
                        if dryrun:
                            print("D: dryrun deletion of %s" % (itm))
                        else:
                            os.remove(itm)


            if deletes:
                if self.options['dbg']:
                    print("%s Files are queued for deletion" % (len(deletes)))

                for itm in deletes:
                    self.path_collection.remove(itm)


                # here -- need remove file + calculate statistics
        else:
            if self.options['dbg']:
                print("No files queued for deletion as NO criteria were specified ")


    def _test_string_start(self, init_str):
        ''' relies on string method startswith to determine whether directory or file path is
            amongst ignored directories. Returns true if directory or file path s amongst
            ignored directories.
        '''
        base_dir_ind = False
        if isinstance(self.options['ignore'], list) and self.options['ignore']:
            for itm in self.options['ignore']:
                if init_str.startswith(itm):
                    base_dir_ind = True
                    break
        return base_dir_ind
