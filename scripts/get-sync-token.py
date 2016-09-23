#!/usr/bin/env python

import sys
import os


def main():
    if len(sys.argv) < 2:
        print('usage: get-sync-token.py token')
        return

    token = sys.argv[1]

    cache = os.path.expanduser('~') + '/.todoist-sync/'

    if not os.path.isdir(cache):
        return

    try:
        with open(cache + token + '.sync') as f:
            sync_token = f.read()
    except:
        return

    print(sync_token)


if __name__ == '__main__':
    main()
