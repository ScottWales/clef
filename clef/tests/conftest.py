import pytest
import intake
import intake_esm
import clef.collection
from unittest.mock import patch
import pandas
import io
import yaml

requires_nci_intake = pytest.mark.skipif(
    "nci" not in intake.cat, reason="Requires NCI intake"
)


@pytest.fixture
def mock_cmip6():
    cat_df = pandas.read_csv(
        io.StringIO(
            "project,activity_id,institution_id,source_id,experiment_id,member_id,table_id,variable_id,grid_label,date_range,path,version,frequency,realm\nCMIP6,CMIP,CSIRO-ARCCSS,ACCESS-CM2,historical,r1i1p1f1,Amon,tas,gn,185001-201412,/g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Amon/tas/gn/v20191108/tas_Amon_ACCESS-CM2_historical_r1i1p1f1_gn_185001-201412.nc,v20191108,mon,atmos\n"
        )
    )

    cat_meta = yaml.safe_load(
        io.StringIO(
            """id: cmip6
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
              dim: time"""
        )
    )

    cat_esm = intake_esm.esm_datastore(cat_df, cat_meta)

    with patch.object(
        clef.collection.intake, "cat", {"nci": {"esgf": {"cmip6": cat_esm}}}
    ):
        yield clef.collection.Cmip6()
