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


import clef.cmip6
import pandas
from unittest.mock import patch
import io
import yaml
import intake_esm


def test_catalogue_filter():
    local = pandas.DataFrame({'path': ['a','b']}, index=[1,2])
    remote = pandas.DataFrame({'path': [None, None]}, index=[2,3])

    col = clef.cmip6.Cmip6()

    with patch.object(col, 'local_catalogue', return_value=local), patch.object(col, 'remote_catalogue', return_value=remote):
        r = col.catalogue(filter='local')
        assert set(r.index.values) == {1, 2}

        r = col.catalogue(filter='remote')
        assert set(r.index.values) == {2, 3}

        r = col.catalogue(filter='missing')
        assert set(r.index.values) == {3}

        r = col.catalogue(filter='all')
        assert set(r.index.values) == {1,2,3}


def test_remote_catalogue():
    col = clef.cmip6.Cmip6()

    cat = col.remote_catalogue(
        activity_id = 'CMIP',
        experiment_id = 'historical',
        source_id = 'ACCESS-CM2',
        frequency = 'mon',
        variable_id = 'tas',
        member_id = 'r1i1p1f1',
        )

    assert len(cat) == 1
    assert cat.index.values[0] == 'CMIP6.CMIP.CSIRO-ARCCSS.ACCESS-CM2.historical.r1i1p1f1.Amon.tas.gn.v20191108'


def test_local_catalogue():
    cat_df = pandas.read_csv(io.StringIO('project,activity_id,institution_id,source_id,experiment_id,member_id,table_id,variable_id,grid_label,date_range,path,version,frequency,realm\nCMIP6,CMIP,CSIRO-ARCCSS,ACCESS-CM2,historical,r1i1p1f1,Amon,tas,gn,185001-201412,/g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Amon/tas/gn/v20191108/tas_Amon_ACCESS-CM2_historical_r1i1p1f1_gn_185001-201412.nc,v20191108,mon,atmos\n'))

    cat_meta = yaml.safe_load(io.StringIO("""id: cmip6
assets:
    column_name: path
    format: netcdf
aggregation_control:
    # Name of the variable in the file
    variable_column_name: variable_id
    # Grouping keys are made of these columns, joined by '.'
    groupby_attrs:
        - project
        - activity_id
        - institution_id
        - source_id
        - experiment_id
        - member_id
        - table_id
        - variable_id
        - grid_label
        - version
    aggregations:
        # Join along the existing time dimension
        - type: join_existing
          attribute_name: date_range
          options:
              dim: time"""))

    cat_esm = intake_esm.esm_datastore(cat_df, cat_meta)

    with patch.object(clef.cmip6.intake, 'cat', {'nci': {'esgf': {'cmip6': cat_esm}}}):
        col = clef.cmip6.Cmip6()
        cat = col.local_catalogue(
            activity_id = 'CMIP',
            experiment_id = 'historical',
            source_id = 'ACCESS-CM2',
            frequency = 'mon',
            variable_id = 'tas',
            member_id = 'r1i1p1f1',
            )

    print(cat.columns)

    assert len(cat) == 1
    assert cat.index.values[0] == 'CMIP6.CMIP.CSIRO-ARCCSS.ACCESS-CM2.historical.r1i1p1f1.Amon.tas.gn.v20191108'

    assert False
