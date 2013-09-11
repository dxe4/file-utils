import fnmatch
import os
import shutil
import datetime
from pprint import PrettyPrinter
import argparse
import sys
import os
from itertools import starmap

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="file name to search (matches regex)", type=str)
parser.add_argument("-d", "--dir", help="directory to search (default= current dir)", type=str, nargs='*')
parser.add_argument("-c", "--copy", help="copy files to dir (default= current dir)", type=str, nargs='*')
parser.add_argument("-m", "--move", help="move files to dir (default= current dir)", type=str, nargs='*')

args = parser.parse_args()
file_name = args.name
print(args.dir)
print(len(args.dir))
search_dirs = [str(os.getcwd())] if args.dir == [] else args.dir
move_dirs = [str(os.getcwd())] if args.move == [] else args.move
copy_dirs = [str(os.getcwd())] if args.copy == [] else args.copy

print(args)
print("dir %s" % search_dirs)
print("move_dir %s" % move_dirs)
print("copy dir %s" % copy_dirs)


def find(path, regex):
    matches = []
    for root, dir_names, file_names in os.walk(path):
        matches.extend(filter_by_name(root, file_names, regex))
    return matches


def filter_by_name(root, file_names, regex):
    return [os.path.join(root, file_name) for file_name in fnmatch.filter(file_names, regex)]


def copy_files(file_paths, destination_dir):
    for file_path in file_paths:
        modified_time, name, type = get_file_info(file_path)
        new_path = ''.join([i for i in [destination_dir, "/", name, "_", str(modified_time)]])
        if type:
            new_path.join(type)
        shutil.copy2(file_path, new_path)


def move_files(file_paths, destination_dir):
    for file_path in file_paths:
        file_name = os.path.split(file_path)[1]
        shutil.move(file_path, destination_dir + file_name)


def get_file_info(file_path):
    head, tail = os.path.split(file_path)
    modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    filename = tail.split(".")
    return modified_time, filename[0], filename[1] if len(filename) > 1 else None


found_files_list = list(starmap(find, ((search_dir, file_name) for search_dir in search_dirs)))
pp = PrettyPrinter()
pp.pprint(found_files_list)

if (copy_dirs):
    res=starmap(copy_files,((files, copy_dir) for copy_dir in copy_dirs for files in found_files_list))
if (move_dirs):
    res=starmap(move_files,((files, move_dir) for move_dir in move_dirs for files in found_files_list))




