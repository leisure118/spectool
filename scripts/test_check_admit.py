#!/usr/bin/env python3
"""Batch validate check-admit against known cheat cases."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'spectool'))
from spectool.vendored.admit import check_admits

def main():
    admit_file = os.path.join(os.path.dirname(__file__), 'live25_admit.txt')
    with open(admit_file) as f:
        lines = [l.strip() for l in f if l.strip()]

    base_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'ds-v4', 'live25')
    caught, missed, skipped = 0, 0, 0

    for rel in lines:
        name = os.path.basename(os.path.dirname(rel))
        base = os.path.basename(rel)
        real = os.path.join(base_dir, name, base)
        if not os.path.isfile(real):
            skipped += 1
            continue
        with open(real) as sf:
            src = sf.read()
        r = check_admits(src)
        if not r['ok']:
            caught += 1
        else:
            missed += 1
            print('MISSED:', real)

    print(f'Caught: {caught}, Missed: {missed}, Skipped (file not found): {skipped}')

if __name__ == '__main__':
    main()
