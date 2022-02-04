from .links import links_coll
from .references import references_coll
from .structures import structures_coll
from .trajectories import trajectories_coll

ENTRY_COLLECTIONS = {
    "links": links_coll,
    "references": references_coll,
    "structures": structures_coll,
    "trajectories": trajectories_coll,
}  # TODO: make a check to determine which entry points are actually present.
