#!/usr/bin/env python
# Copyright 2021 ARC Centre of Excellence for Climate Extremes
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

import logging
import typing as T

import requests

log = logging.getLogger(__name__)


def esgf_api(
    limit: int = 100,
    offset: int = 0,
    facets: T.List[str] = None,
    fields: T.List[str] = None,
    replica=False,
    **kwargs
) -> T.Dict:
    """
    Perform a single ESGF API query
    """
    params = {
        **kwargs,
        **{
            "format": "application/solr+json",
            "limit": limit,
            "offset": offset,
            "replica": replica,
            "latest": True,
        },
    }

    if facets is not None:
        params["facets"] = ",".join(facets)
    if fields is not None:
        params["fields"] = ",".join(fields)

    r = requests.get("https://esgf.nci.org.au/esg-search/search", params)
    log.debug("GET %s", r.url)

    r.raise_for_status()
    return r.json()


def esgf_api_results_iter(**kwargs) -> T.Generator[T.Dict, None, None]:
    """
    Return a stream of results from a ESGF API query, automatically handling pagination
    """
    limit = 1000
    offset = 0

    while True:
        log.debug("Results %d - %d", offset, offset + limit)
        r = esgf_api(limit=limit, offset=offset, **kwargs)

        for d in r["response"]["docs"]:
            yield {
                k: v[0] if isinstance(v, list) and len(v) == 1 else v
                for k, v in d.items()
                if k != "score"
            }

        offset += limit
        if offset > r["response"]["numFound"]:
            break
