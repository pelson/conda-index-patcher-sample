#!/usr/bin/env python

# conda execute
# env:
#  - python >=3.6

import bz2
import json
from pathlib import Path
from pprint import pprint
import urllib.request


def patch_index(index):
    return index


def write_index(index, outdir):
    repofname = outdir / 'repodata.json'
    if not outdir.exists():
        outdir.mkdir(parents=True)
    with repofname.open('w') as fh:
        fh.write(json.dumps(index, indent=4))
    with (repofname.with_suffix('.json.bz2')).open('wb') as fh:
        fh.write(bz2.compress(json.dumps(index).encode('utf8')))


def order_dict(dictionary):
    return {k: order_dict(v) if isinstance(v, dict) else v
            for k, v in sorted(dictionary.items())}


def update_index(fname, outdir):
    with fname.open() as fh:
        index = json.load(fh)
    index = patch_index(index)
    index = order_dict(index)
    write_index(index, outdir)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("destination")
    parser.add_argument("--no-cache", action='store_true')
    args = parser.parse_args()
    use_cache = not args.no_cache
    for platform in ['linux-64', 'osx-64', 'noarch']:
        print(f'Preparing {platform}')
        fname = Path('cache') / platform / 'repodata.json.bz2'
        fname_uncompressed = fname.with_suffix('.json')
        if not fname_uncompressed.exists():
            if not fname.parent.exists():
                fname.parent.mkdir(parents=True)
            if not fname.exists():
                url = f'https://conda.anaconda.org/conda-forge/{platform}/repodata.json.bz2'
                urllib.request.urlretrieve(url, fname)
            with fname.open('rb') as fh:
                with fname_uncompressed.open('w') as fh_write:
                    json.dump(json.loads(bz2.decompress(fh.read())), fh_write, indent=4)
        update_index(fname_uncompressed, Path(args.destination) / platform)

