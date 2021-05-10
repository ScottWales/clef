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


def test_catalogue_filter():
    local = pandas.DataFrame({'path': ['a','b']}, index=[1,2])
    remote = pandas.DataFrame({'path': [None, None]}, index=[2,3])

    col = clef.cmip6.Cmip6()

    with patch.object(col, 'local_catalogue', return_value=local), patch.object(col, 'remote_catalogue', return_value=remote):
        r = col.catalogue({}, filter='local')
        assert set(r.index.values) == {1, 2}

        r = col.catalogue({}, filter='remote')
        assert set(r.index.values) == {2, 3}

        r = col.catalogue({}, filter='missing')
        assert set(r.index.values) == {3}

        r = col.catalogue({}, filter='all')
        assert set(r.index.values) == {1,2,3}
