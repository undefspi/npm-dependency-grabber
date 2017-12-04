#!/usr/bin/python

import argparse
import os
from npm import npmdependency

def initialise():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "dependency", help="the target top level dependency to install", type=str)
    args = parser.parse_args()
    return args


def get_dep(name, output_dir):

    dep = npmdependency.Dependency()
    dep_obj = dep.parse_dependency(name)
    output_file_path = dep.download_npm(dep_obj, output_dir)
    if output_file_path:
        print("get dependencies from ", output_file_path)
        artifact_dep = dep.get_dependencies_from_tar(output_file_path)
        for dependency in artifact_dep:
            next_level_dep = dependency + '@' + \
                artifact_dep[dependency].replace("^", "")
            get_dep(next_level_dep, output_dir)

    return False


def main():
    args = initialise()
    outpath = ''.join((os.getcwd(), '\\', 'output'))
    get_dep(args.dependency, outpath)


if __name__ == "__main__":
    main()
