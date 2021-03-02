#!/usr/bin/env python
#
# Copyright 2019 Scott Wales
#
# Author: Scott Wales <scott.wales@unimelb.edu.au>
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

from clef.esgf import esgf_query
import functools
import click


def tidy_facet_count(v):
    return v[::2]


@functools.lru_cache()
def get_esgf_facets(project):
    q = esgf_query(limit=0, project=project, type="Dataset", facets="*")

    q = {k: tidy_facet_count(v) for k, v in q["facet_counts"]["facet_fields"].items()}

    return q


cli_facets = {
        "institute": { "short": [],
        "help": "identifier for the institution that is responsible for the scientific aspects of the CORDEX simulation",
        "controlled_vocab": True,
    },
    "experiment": { "short": ["-e"],
        "help": "CMIP5 experiment of driving GCM or 'evaluation' for re-analysis",
        "controlled_vocab": True,
    },
    "ensemble": {"short": ["-en"],
        "help": "Ensemble member of the driving GCM",
        "controlled_vocab": True,
    },
    "domain": {"short": ["-d"], "help": "CORDEX region name", "controlled_vocab": True},
    "variable": {"short": ["-v"], "help": "Variable name in file", "controlled_vocab": True},
    "cf_standard_name": {"short": [], "help": "CF-Conventions name of the variable"},
    "rcm_version": {"short": ["-rcmv"],
        "help": "Identifier for reruns with perturbed parameters or smaller RCM release upgrades",
        "controlled_vocab": True,
    },
    "rcm_name": {"short": ["-m"], "help": "Identifier of the CORDEX RCM", "controlled_vocab": True},
    "driving_model": { "short": ["-dmod"],
        "help": "Model/analysis used to drive the model (eg. ECMWF­ERAINT)",
        "controlled_vocab": True,
    },
    "time_frequency": {"short": ["-f"], "help": "Output frequency indicator", "controlled_vocab": True},
    "version": {"short": [], "help": "Data publication version", "controlled_vocab": True},
    "experiment_family": {"short": [], 'one': True, "controlled_vocab": True,
        "help": "Experiment family: All, Historical, RCP"}
}


class CordexCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        facets = get_esgf_facets(project="CORDEX")
        for k, v in cli_facets.items():
            opt = click.Option(
                [f"--{k}"] + v['short'], help=v["help"], multiple=(False if 'one' in v.keys() else True), metavar="FACET"
            )

            # shouldn't this be True?
            if v.get("controlled_vocab", False):
                opt.type = click.Choice(facets[k], case_sensitive=False)

            self.params.append(opt)

        opt = click.Option(
            ["--and", "and_attr"],
            multiple=True,
            type=click.Choice(cli_facets.keys()),
            help="Attributes for which we want to add AND filter, i.e. -v tasmin -v tasmax --and variable_id will return only model/ensemble that have both",
        )
        self.params.append(opt)
