#!/usr/bin/python3

import os
import subprocess
import argparse
import xml.etree.ElementTree as ET
from typing import List


class SVNItem:
    def __init__(self, path, status="unversioned"):
        self.path = path
        self.status = status

    def __repr__(self):
        return 'SVNItem("{path}", {status})'.format(path=self.path, status=self.status)

def svn_status(path: str) -> List[SVNItem]:
    items = []
    output = subprocess.check_output('svn status --no-ignore --xml', cwd=path, shell=True)
    #print(output.decode('utf8'))
    root = ET.fromstring(output.decode('utf8'))
    target = root[0]
    assert(target.tag == 'target')
    for entry in target:
        wcstatus = entry[0]
        assert(wcstatus.tag == "wc-status")
        items.append(SVNItem(entry.attrib['path'], wcstatus.attrib['item']))

    return items

def clean_items(items: List[SVNItem], dirs:bool=False, dry_run:bool=False, ignored:bool=False):
    msg = 'Would remove {path}' if dry_run else 'Removing {path}'
    item_filter = ["unversioned"]
    if ignored:
        item_filter.append("ignored")
    for item in [x for x in items if x.status in item_filter]:
        print(msg.format(path=item.path))
        if os.path.isdir(item.path):
            if dirs:
                if not dry_run:
                    os.removedirs(item.path)
        else:
            if not dry_run:
                os.remove(item.path)


def main():
    parser = argparse.ArgumentParser(description="Remove untracked files from the working directory")
    parser.add_argument("-n", "--dry-run", default=False, action="store_true", help="Don’t actually remove anything, just show what would be done.")
    parser.add_argument("-d", "--directories", default=False, action="store_true", help="Remove untracked directories in addition to untracked files.")
    parser.add_argument("-x", "--ignored", default=False, action="store_true", help="Remove also ignored files/directories by subversion.")
    args = parser.parse_args()

    items = svn_status(os.getcwd())
    clean_items(items, args.directories, args.dry_run, args.ignored)

if __name__ == '__main__':
    main()
