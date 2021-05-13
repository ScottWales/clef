import lzma
import typing as T

import yaml

from .collection import all_collections

if __name__ == "__main__":
    meta: T.Dict = {}

    for col in all_collections:
        meta[col.name] = {"facets": col._get_facet_values_esgf()}

    with lzma.open("metadata.yaml.xz", "wt") as f:
        yaml.dump(meta, f)
