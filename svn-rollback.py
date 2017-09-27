#!/usr/bin/python3

import os
import subprocess
import argparse
import xml.etree.ElementTree as ET
from typing import List


class SVNItem:
    def __init__(self, path, action, kind):
        self.path = path
        self.action = action
        self.kind = kind

    def __repr__(self):
        return 'SVNItem("{path}", {action}, {kind})'.format(path=self.path, action=self.action, kind=self.kind)

def svn_root_url():
    return subprocess.check_output('svn info --show-item repos-root-url', shell=True).decode('utf8').rstrip()

def svn_changedfiles(path: str, rev: int) -> List[SVNItem]:
    items = []
    output = subprocess.check_output('svn log --verbose -r{rev} --xml'.format(rev=rev), cwd=path, shell=True)
    #print(output.decode('utf8'))
    root = ET.fromstring(output.decode('utf8'))
    log_elem = root[0]
    paths_elem = log_elem.find("paths")
    for path in paths_elem:
        assert(path.tag == "path")
        items.append(SVNItem(path.text, path.attrib['action'], path.attrib['kind']))
    return items

def main():
    parser = argparse.ArgumentParser(description="Rollback a given revision")
    parser.add_argument("revision", type=int, help="Revision to rollback")
    args = parser.parse_args()

    output = subprocess.check_output('svn merge -c -{rev} .'.format(rev=args.revision), shell=True)
    subprocess.check_output('svn commit -m "revert commit {rev}"'.format(rev=args.revision), shell=True)

    items = svn_changedfiles(os.getcwd(), args.revision)
    root_url = svn_root_url()
    for item in [x for x in items if x.action in ['A', 'M']]:
        path = root_url + item.path
        subprocess.check_call('svn export --force "{url}"@{rev}'.format(url=path, rev=args.revision), shell=True)


if __name__ == '__main__':
    main()
