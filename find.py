import fnmatch
import os
import shutil
import datetime
from pprint import PrettyPrinter
import argparse
import sys
import os
from itertools import starmap


class FindFiles():
    def _find(self, path:str, regex:str):
        #TODO make filter a callback
        matches = []
        for root, dir_names, file_names in os.walk(path):
            matches.extend(self.filter_by_name(root, file_names, regex))
        return matches


    def filter_by_name(self, root:str, file_names:list, regex:str):
        return [os.path.join(root, file_name) for file_name in fnmatch.filter(file_names, regex)]


    def execute(self, file_name:str, search_dirs:list):
        return list(starmap(
            self._find, ((search_dir, file_name) for search_dir in search_dirs))
        )


class PostFind():
    def execute(self, found_files_list:list, copy_dirs:list, move_dirs:list):
        self._execute(copy_dirs,found_files_list,self.copy_files)
        self._execute(move_dirs,found_files_list,self.move_files)

    def _execute(self,dirs:list,found_files_list:list,callback):
        if not dirs:
            return
        args = ((files, dir) for dir in dirs for files in found_files_list)
        list(starmap(callback, args))

    def copy_files(self, file_paths:list, destination_dir:str):
        for file_path in file_paths:
            modified_time, name, type = self.get_file_info(file_path)
            #TODO make rename a callback
            new_path = ''.join([destination_dir, "/", name, "_", str(modified_time)])
            if type:
                new_path.join(type)
            shutil.copy2(file_path, new_path)


    def move_files(self, file_paths:list, destination_dir:str):
        for file_path in file_paths:
            file_name = os.path.split(file_path)[1]
            shutil.move(file_path, destination_dir + file_name)


    def get_file_info(self, file_path:str):
        head, tail = os.path.split(file_path)
        modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        filename = tail.split(".")
        return modified_time, filename[0], filename[1] if len(filename) > 1 else None


class InputHandler():
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--name", help="file name to search (matches regex)", type=str)
        parser.add_argument("-d", "--dir", help="directory to search (default= current dir)", type=str, nargs='*')
        parser.add_argument("-c", "--copy", help="copy files to dir (default= current dir)", type=str, nargs='*')
        parser.add_argument("-m", "--move", help="move files to dir (default= current dir)", type=str, nargs='*')
        self.args = vars(parser.parse_args())

        self.file_name = self.args['name']
        self.init_optional_dirs(self.args, "search_dirs", "dir")
        self.init_optional_dirs(self.args, "move_dirs", "move")
        self.init_optional_dirs(self.args, "copy_dirs", "copy")

        print(self.__dict__)

    def init_optional_dirs(self, args:dict, attr_name:str, arg_name:str):
        value = [str(os.getcwd())] if args[arg_name] == [] else args[arg_name]
        setattr(self, attr_name, value)


if __name__ == '__main__':
    inputHandler = InputHandler()
    findFiles = FindFiles()
    postFind = PostFind()

    found_files_list = findFiles.execute(inputHandler.file_name, inputHandler.search_dirs)
    postFind.execute(found_files_list, inputHandler.copy_dirs, inputHandler.move_dirs)

    pp = PrettyPrinter()
    pp.pprint(found_files_list)

    print("\033[1m 999 \033[0m")
