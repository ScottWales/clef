from unittest.mock import patch

import clef.cli

from .conftest import *


def test_cmip6_remote_search(capsys):
    clef.cli.main(
        "cmip6 --filter remote --activity CMIP --experiment historical "
        "--source ACCESS-CM2 --frequency mon "
        "--variable tas --member r1i1p1f1".split()
    )

    out, err = capsys.readouterr()

    assert (
        out.strip()
        == "CMIP6.CMIP.CSIRO-ARCCSS.ACCESS-CM2.historical.r1i1p1f1.Amon.tas.gn.v20191108"
    )


def test_cmip6_remote_search_alias(capsys):
    clef.cli.main(
        "cmip6 --filter remote --activity CMIP --experiment historical "
        "--model ACCESS-CM2 --frequency mon "
        "--variable tas --member r1i1p1f1".split()
    )

    out, err = capsys.readouterr()

    assert (
        out.strip()
        == "CMIP6.CMIP.CSIRO-ARCCSS.ACCESS-CM2.historical.r1i1p1f1.Amon.tas.gn.v20191108"
    )


def test_cmip6_local_search_mock(mock_cmip6, capsys):
    with patch("clef.cli.collection.Cmip6", lambda: mock_cmip6):
        clef.cli.main(
            "cmip6 --filter local --activity CMIP --experiment historical "
            "--source ACCESS-CM2 --frequency mon "
            "--variable tas --member r1i1p1f1".split()
        )

    out, err = capsys.readouterr()

    assert (
        out.strip()
        == "/g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Amon/tas/gn/v20191108"
    )


@requires_nci_intake
def test_cmip6_local_search(capsys):
    clef.cli.main(
        "cmip6 --filter local --activity CMIP --experiment historical "
        "--source ACCESS-CM2 --frequency mon "
        "--variable tas --member r1i1p1f1".split()
    )

    out, err = capsys.readouterr()

    assert (
        out.strip()
        == "/g/data/fs38/publications/CMIP6/CMIP/CSIRO-ARCCSS/ACCESS-CM2/historical/r1i1p1f1/Amon/tas/gn/v20191108"
    )
