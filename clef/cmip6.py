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
import intake
import pandas
import typing as T
from . import esgf


class Cmip6():
    name = 'cmip6'
    esgf_project = 'CMIP6'
    intake_cat = name
    facets = {
        'activity_id': {},
        'source_id': {},
        'institution_id': {},
        'experiment_id': {},
        'member_id': {},
        'table_id': {},
        'frequency': {},
        'realm': {},
        'variable_id': {},
        }


    def __init__(self):
        pass


    def setup_subparser(self, subp):
        parser = subp.add_parser(self.name)

        parser.add_argument('--filter', choices=['local','remote','missing','all'], default='all', help='filter the output to show only files at nci (local), all files on esgf (remote), files on esgf but not nci (missing), or both files at nci and missing files (all)')
        parser.add_argument('--request', action='store_true', help='request missing datasets be downloaded')
        parser.add_argument('--csv', nargs='?', type=argparse.FileType('w'), default=f'{self.name}_query.csv', metavar='FILE', help='store output in a csv file')
        parser.add_argument('--stats', action='store_true', help='print a summary of results')

        # Old filter names
        parser.add_argument('--local', dest='filter', action='store_const', const='local', help='see --filter local')
        parser.add_argument('--remote', dest='filter', action='store_const', const='remote', help='see --filter remote')
        parser.add_argument('--missing', dest='filter', action='store_const', const='missing', help='see --filter missing')

        facets = parser.add_argument_group('esgf search facets')

        for name, attrs in self.facets.items():
            facets.add_argument(f'--{name}', nargs='+')

        return parser


    def catalogue(self, *, filter: str='all', **facets: T.Dict[str, T.List[str]]):
        """
        Create a dataframe with the search results

        Args:
            facets: ESGF search facets
            filter: filter the output to show only files at nci (local), all
                files on esgf (remote), files on esgf but not nci (missing), or
                both files at nci and missing files (all)

        Returns:
            DataFrame with columns ['instance_id', **self.facets.keys(), 'path']
        """
        if filter not in ['local', 'remote', 'missing', 'all']:
            raise NotImplementedError(f"Bad filter name '{filter}'")

        if filter != 'remote':
            local_results = self.local_catalogue(facets)

        if filter != 'local':
            remote_results = self.remote_catalogue(facets)

        if filter == 'local':
            return local_results
        elif filter == 'remote':
            return remote_results

        missing_idx = remote_results.index.difference(local_results.index)
        missing_results = remote_results.loc[missing_idx]

        if filter == 'missing':
            return missing_results
        elif filter == 'all':
            return pandas.concat([local_results, missing_results])
        else:
            raise Exception # Shouldn't reach here


    def local_catalogue(self, **facets: T.Dict[str, T.List[str]]):
        self._check_facets(facets)

        cat = intake.cat['nci']['esgf'][self.intake_cat].search(**facets)

        df = cat.df[[*self.facets.keys(), 'path']]

        index = df.apply(lambda r: '.'.join(r[cat.groupby_attrs]), axis=1)

        return df.set_index(index)


    def remote_catalogue(self, **facets: T.Dict[str, T.List[str]]):
        self._check_facets(facets)

        results = esgf.esgf_api_results_iter(project=self.esgf_project, fields=['instance_id', *self.facets.keys()], **facets)

        df = pandas.DataFrame.from_records(results)

        return df.set_index('instance_id')
    

    def get_facet_values(self):
        pass


    def _check_facets(self, facets):
        diff_names = set(facets.keys()) - set(self.facets.keys())
        if len(diff_names) > 0:
            raise Exception(f"Invalid facet names {diff_names}")
