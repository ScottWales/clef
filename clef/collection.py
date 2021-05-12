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

import intake
import pandas
import typing as T
import os
import difflib
import logging
from . import esgf

log = logging.getLogger(__name__)


class Collection:
    def __init__(self):
        pass

    def setup_subparser(self, subp):
        """
        Setup CLI
        """
        parser = subp.add_parser(self.name)
        parser.set_defaults(main=self.cli)

        parser.add_argument(
            "--filter",
            choices=["local", "remote", "missing", "all"],
            default="all",
            help="filter the output to show only files at nci (local), all files on esgf (remote), files on esgf but not nci (missing), or both files at nci and missing files (all)",
        )
        parser.add_argument(
            "--request",
            action="store_true",
            help="request missing datasets be downloaded",
        )
        parser.add_argument(
            "--csv",
            nargs="?",
            default=f"{self.name}_query.csv",
            metavar="FILE",
            help="store output in a csv file",
        )
        parser.add_argument(
            "--stats", action="store_true", help="print a summary of results"
        )

        facets = parser.add_argument_group("esgf search facets")

        for name, attrs in self.facets.items():
            facets.add_argument(f"--{name}", nargs="+")

        return parser

    def cli(self, args):
        """
        Run the CLI command
        """
        facets = {
            k: v
            for k, v in vars(args).items()
            if k in self.facets.keys() and v is not None
        }

        cat = self.catalogue(filter=args.filter, **facets)

        if args.csv is not None:
            cat.to_csv(args.csv)

        if args.stats:
            self.print_stats(cat)
        else:
            self.print_results(cat)

        if args.request:
            self.request_download(cat)

    def catalogue(
        self, *, filter: str = "all", **facets: T.Dict[str, T.List[str]]
    ) -> pandas.DataFrame:
        """
        Create a dataframe with filtered search results

        Args:
            facets: ESGF search facets
            filter: filter the output to show only files at nci (local), all
                files on esgf (remote), files on esgf but not nci (missing), or
                both files at nci and missing files (all)

        Returns:
            DataFrame with columns ['instance_id', **self.facets.keys(), 'path']
        """
        if filter not in ["local", "remote", "missing", "all"]:
            raise NotImplementedError(f"Bad filter name '{filter}'")

        local_results = None
        remote_results = None

        if filter != "remote":
            local_results = self.local_catalogue(**facets)

        if filter != "local":
            remote_results = self.remote_catalogue(**facets)

        if filter == "local":
            return local_results
        elif filter == "remote":
            return remote_results

        missing_idx = remote_results.index.difference(local_results.index)
        missing_results = remote_results.loc[missing_idx]

        if filter == "missing":
            return missing_results
        elif filter == "all":
            return pandas.concat([local_results, missing_results])
        else:
            raise Exception  # Shouldn't reach here

    def local_catalogue(self, **facets: T.Dict[str, T.List[str]]) -> pandas.DataFrame:
        """
        Create a dataframe with local search results

        Args:
            facets: ESGF search facets

        Returns:
            DataFrame with columns ['instance_id', **self.facets.keys(), 'path']
        """
        self._check_facets(facets)

        cat = intake.cat["nci"]["esgf"][self.intake_cat].search(**facets)

        df = cat.df.groupby(cat.groupby_attrs).first().reset_index()
        df["path"] = df["path"].apply(os.path.dirname)

        index = df.apply(lambda r: ".".join(r[cat.groupby_attrs].values), axis=1)

        return df.set_index(index)

    def remote_catalogue(self, **facets: T.Dict[str, T.List[str]]) -> pandas.DataFrame:
        """
        Create a dataframe with remote search results

        Args:
            facets: ESGF search facets

        Returns:
            DataFrame with columns ['instance_id', **self.facets.keys(), 'path']
        """
        self._check_facets(facets)

        results = list(
            esgf.esgf_api_results_iter(
                project=self.esgf_project,
                fields=["instance_id", *self.facets.keys()],
                **facets,
            )
        )

        df = pandas.DataFrame.from_records(results)
        df["path"] = None

        return df.set_index("instance_id")

    def print_stats(self, cat: pandas.DataFrame):
        """
        Print a summary of results
        """
        pass

    def print_results(self, cat: pandas.DataFrame):
        """
        Print search results
        """
        for key, row in cat.iterrows():
            if row["path"] is not None:
                print(row["path"])
            else:
                print(key)

    def _get_facet_values(self):
        return {k: [] for k in self.facets.keys()}

    def _check_facets(self, facets: T.Dict[str, T.List[str]]):
        """
        Check the given facet values match possible values on ESGF

        If a value is not possible, print some suggestions
        """
        diff_names = set(facets.keys()) - set(self.facets.keys())
        if len(diff_names) > 0:
            raise Exception(f"Invalid facet names {diff_names}")

        possible_values = self._get_facet_values()
        for k, values in facets.items():
            # Ensure values is a list
            if isinstance(values, str):
                values = [values]

            for v in values:
                if v not in possible_values[k]:
                    nearest = difflib.get_close_matches(
                        v.upper(), possible_values[k], cutoff=0.6
                    )
                    log.warning(
                        "No %s %s named %s, close matches %s",
                        self.esgf_project,
                        k,
                        v,
                        nearest,
                    )


class Cmip6(Collection):
    name = "cmip6"
    esgf_project = "CMIP6"
    intake_cat = name
    facets = {
        "activity_id": {},
        "source_id": {},
        "institution_id": {},
        "experiment_id": {},
        "member_id": {},
        "table_id": {},
        "frequency": {},
        "realm": {},
        "variable_id": {},
    }

    def __init__(self):
        super().__init__()


class Cmip5(Collection):
    name = "cmip5"
    esgf_project = "CMIP5"
    intake_cat = name
    facets = {
        "institute": {},
        "model": {},
        "experiment": {},
        "ensemble": {},
        "cmor_table": {},
        "time_frequency": {},
        "realm": {},
        "variable": {},
    }

    def __init__(self):
        super().__init__()

    def remote_catalogue(self, **facets: T.Dict[str, T.List[str]]):
        """
        Create a dataframe with remote search results

        Args:
            facets: ESGF search facets

        Returns:
            DataFrame with columns ['instance_id', **self.facets.keys(), 'path']
        """
        df = super().remote_catalogue(**facets)

        # CMIP5 doesn't include variable in instance_id, and returns all possible variables
        # Convert the list of variables to rows
        df = df.explode("variable")

        # Add the variable name to instance_id
        df.index = df.index + "." + df.variable

        # Filter out variables to only the required values
        if "variable" in facets:
            v = facets["variable"]
            if isinstance(v, str):
                v = [v]
            df = df[df.variable.isin(v)]

        return df
