#!/usr/bin/python

import re
import os
import shutil
import tarfile
import json
import requests


class Dependency(object):
    def __init__(self):
        self._repo_url = 'https://registry.npmjs.org/'

    def _extract_npm_meta(self, file_path):
        package_json_path = 'package/package.json'
        tar = tarfile.open(file_path)
        tar_members = tar.getmembers()
        package_present = False
        for tar_info in tar_members:
            if tar_info.name == package_json_path:
                tar.extract(tar_info)
                package_present = True
        tar.close()
        return package_present

    #needs some work - ideally sort so the latest version is used not the early
    #Also multiple x.x don't necessrily work
    def _parse_version_nums(self, v_from, v_to):

        rep = {"=": "", ">": "", "=": "", "~": "", "<": ""}
        rep = dict((re.escape(k), v) for k, v in rep.iteritems())
        pattern = re.compile("|".join(rep.keys()))
        version = pattern.sub(lambda m: rep[re.escape(m.group(0))], v_from)

        #doesnt always assume the right value - temporary solution
        if "x" in version:
            version = version.replace("x", "1")

        return version

    def parse_dependency(self, name):
        reg_obj = re.compile(
            "^(.*)@([~^\*>]?[=]?)([0-9]{1,2}\.[0-9x]{1,2}\.[0-9x]{1,2})(.*)")
        dep_match = reg_obj.search(name)

        if dep_match:
            dep_name = dep_match.group(1)
            dep_version_from = dep_match.group(3)
            dep_version_to = dep_match.group(4)

            dep_v = self._parse_version_nums(dep_version_from, dep_version_to)
            dep_map = {"dep_name": dep_name, "dep_version": dep_v}

            return dep_map
        else:
            print "Invalid dependency format agains :" + name + "use package@version"
            exit()

    def download_npm(self, dep_obj, output_dir):

        repo_artifact_base = (self._repo_url, dep_obj['dep_name'], '/-/')
        target_tar = (dep_obj['dep_name'], '-', dep_obj['dep_version'], '.tgz')
        url_request = ''.join((repo_artifact_base + target_tar))
        output_file = output_dir + '\\' + ''.join(target_tar)
        if os.path.exists(output_file):
            print "File already exist's. Returning current file path"
            return output_file

        try:
            session = requests.Session()
            response = session.get(url_request, stream=True)
        except requests.exceptions.RequestException as e:
            print "failure Attempt to get " + ''.join(target_tar) + " " + str(e.message)
            exit()

        if not response.status_code == 200:
            print "Failure in geting Tar", str(response.status_code)
            exit()

        response.raw.decode_content = True
        with open(output_file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        return output_file

    def get_dependencies_from_tar(self, tar_file_path):
        if not self._extract_npm_meta(tar_file_path):
            print "Failed to extract meta from NPM for file_path"
            exit()

        end = len(tar_file_path) - tar_file_path.rfind('output')
        package_path = tar_file_path[:-end] + "\\package\\package.json"
        data = json.load(open(package_path))

        data_len = len(data)
        if data_len > 0:
            package_dir = tar_file_path[:-end] + 'package'
            shutil.rmtree(package_dir)

        if "dependencies" not in data:
            return {}

        return data['dependencies']
