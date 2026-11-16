#!/usr/bin/env python3
"""Build the motion assets and the compatible Petdex v2 pack."""
import argparse
from pathlib import Path
from motion_assets import ROOT, build

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'pet/nery')
    build(parser.parse_args().out)
