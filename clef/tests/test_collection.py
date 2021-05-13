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


from unittest.mock import patch

import clef.collection
import pandas


def test_catalogue_filter():
    local = pandas.DataFrame({"path": ["a", "b"]}, index=[1, 2])
    remote = pandas.DataFrame({"path": [None, None]}, index=[2, 3])

    col = clef.collection.Cmip6()

    with patch.object(col, "local_catalogue", return_value=local), patch.object(
        col, "remote_catalogue", return_value=remote
    ):
        r = col.catalogue(filter="local")
        assert set(r.index.values) == {1, 2}

        r = col.catalogue(filter="remote")
        assert set(r.index.values) == {2, 3}

        r = col.catalogue(filter="missing")
        assert set(r.index.values) == {3}

        r = col.catalogue(filter="all")
        assert set(r.index.values) == {1, 2, 3}


def test_remote_catalogue_cmip6():
    col = clef.collection.Cmip6()

    cat = col.remote_catalogue(
        activity_id="CMIP",
        experiment_id="historical",
        source_id="ACCESS-CM2",
        frequency="mon",
        variable_id="tas",
        member_id="r1i1p1f1",
    )

    assert len(cat) == 1
    assert (
        cat.index.values[0]
        == "CMIP6.CMIP.CSIRO-ARCCSS.ACCESS-CM2.historical.r1i1p1f1.Amon.tas.gn.v20191108"
    )


def test_remote_catalogue_cmip5():
    col = clef.collection.Cmip5()

    cat = col.remote_catalogue(
        experiment="historical",
        model="ACCESS1.0",
        time_frequency="mon",
        variable="tas",
        ensemble="r1i1p1",
    )

    assert len(cat) == 1
    assert (
        cat.index.values[0]
        == "cmip5.output1.CSIRO-BOM.ACCESS1-0.historical.mon.atmos.Amon.r1i1p1.v20120727.tas"
    )


def test_remote_catalogue_cordex():
    col = clef.collection.Cordex()

    cat = col.remote_catalogue(
        institute="UNSW",
        experiment="historical",
        ensemble="r1i1p1",
        domain="AUS-44",
        variable="tas",
        rcm_name="WRF360L",
        driving_model="CSIRO-BOM-ACCESS1-0",
        time_frequency="mon",
    )

    assert len(cat) == 1
    assert (
        cat.index.values[0]
        == "cordex.output.AUS-44.UNSW.CSIRO-BOM-ACCESS1-0.historical.r1i1p1.WRF360L.v1.mon.tas.v20180614"
    )


def test_local_catalogue(mock_cmip6):

    cat = mock_cmip6.local_catalogue(
        activity_id="CMIP",
        experiment_id="historical",
        source_id="ACCESS-CM2",
        frequency="mon",
        variable_id="tas",
        member_id="r1i1p1f1",
    )

    assert len(cat) == 1
    assert (
        cat.index.values[0]
        == "CMIP6.CMIP.CSIRO-ARCCSS.ACCESS-CM2.historical.r1i1p1f1.Amon.tas.gn.v20191108"
    )


def test_local_catalogue_wildcard(mock_cmip6):

    cat = mock_cmip6.local_catalogue(
        activity_id="CMIP",
        experiment_id="historical",
        source_id="ACCESS*",
        frequency="mon",
        variable_id="tas",
        member_id="r1i1p1f1",
    )

    assert len(cat) == 1
    assert (
        cat.index.values[0]
        == "CMIP6.CMIP.CSIRO-ARCCSS.ACCESS-CM2.historical.r1i1p1f1.Amon.tas.gn.v20191108"
    )


def test_catalogue_no_match(mock_cmip6):

    cat = mock_cmip6.catalogue(
        activity_id="CMIP",
        experiment_id="bad_value",
        source_id="ACCESS-CM2",
        frequency="mon",
        variable_id="tas",
        member_id="r1i1p1f1",
    )

    assert len(cat) == 0


def test_check_facets(caplog):
    col = clef.collection.Cmip6()
    with patch.object(
        col, "_get_facet_values", lambda: {"source_id": ["ACCESS-CM2", "ACCESS-ESM"]}
    ):
        col._check_facets({"source_id": ["access_cm"]})

    assert caplog.text.strip().endswith(
        "No CMIP6 source_id named access_cm, close matches ['ACCESS-CM2', 'ACCESS-ESM']"
    )

    col._check_facets({"source_id": ["ACCESS-CM2"]})

    # Nothing added to log
    assert caplog.text.strip().endswith(
        "No CMIP6 source_id named access_cm, close matches ['ACCESS-CM2', 'ACCESS-ESM']"
    )

    col._check_facets({"experiment_id": ["historica"]})

    # Nothing added to log
    assert caplog.text.strip().endswith(
        "No CMIP6 experiment_id named historica, close matches ['historical', 'historical-ext', 'historical-cmip5']"
    )


def test_metadata():
    col = clef.collection.Cmip6()

    meta = col._get_metadata()

    assert "facets" in meta


def test_all_variables_filter():
    col = clef.collection.Cmip6()

    cat = pandas.DataFrame(
        {
            "activity_id": ["a", "a", "a"],
            "institution_id": ["a", "a", "a"],
            "source_id": ["a", "a", "b"],
            "experiment_id": ["a", "a", "a"],
            "member_id": ["a", "a", "a"],
            "variable_id": ["a", "b", "a"],
        }
    )

    cat_f = col.all_variables_filter(cat, variable_id=["a", "b"])

    assert len(cat_f) == 2
    assert cat_f.source_id.unique() == ["a"]
