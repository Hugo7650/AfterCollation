#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import vgmdb.fetch
import json

def parse_albumlist(album):
	album_info = vgmdb.fetch.albumlist(album, use_cache=False)
	return json.dumps(album_info, sort_keys=True, indent=4, separators=(',',': '), ensure_ascii=False)
if __name__ == '__main__' and len(sys.argv) > 1:
	print(parse_albumlist(sys.argv[1]).encode('utf-8'))
