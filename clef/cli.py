#!/g/data/hh5/public/apps/nci_scripts/python-analysis3
# Copyright 2021 Scott Wales
# author: Scott Wales <scott.wales@unimelb.edu.au>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging
#from . import cmip6
import cmip6


def main():
    logging.basicConfig()
    log = logging.getLogger('clef')

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', help='show debugging logs', action='store_true')

    subp = parser.add_subparsers()

    cmip6.Cmip6().setup_subparser(subp)


    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)


if __name__ == '__main__':
    main()
