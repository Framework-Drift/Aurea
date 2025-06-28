"""
symbolic_grouping.py — Symbolic Grouping and Constellation Engine for Aurea

Provides grouping, cluster analysis, and constellation mapping of scars and doctrines for
reflection, TCA, analytics, and self-recursive operations.
"""

from typing import Set
from typing import List, Dict, Any
from src.filtration.scar_logic_core import ScarLogicCore
from src.doctrine.doctrine_spine import DoctrineSpine

class SymbolicGrouping:
    """
    Provides static/grouping views over all symbolic memory:
      - Group scars by tag, type, reflex, etc.
      - Group doctrines by status, tag, or mutation lineage.
      - Constellation mapping (symbolic networks).
    """
    def __init__(self, scarlogic: ScarLogicCore, doctrinespine: DoctrineSpine):
        self.scarlogic = scarlogic
        self.doctrinespine = doctrinespine

    # --- Scar Grouping ---
    def group_scars_by_tag(self, tag: str) -> List[Any]:
        """Return all scars with the specified TCA tag."""
        return [s for s in self.scarlogic.scars if tag in getattr(s, "tca_tags", [])]

    def group_scars_by_type(self, type_str: str) -> List[Any]:
        """Return all scars with the specified type."""
        return [s for s in self.scarlogic.scars if getattr(s, "type", None) == type_str]

    def group_scars_by_reflex(self, reflex: str) -> List[Any]:
        """Return all scars linked to a specific reflex."""
        return [s for s in self.scarlogic.scars if reflex in getattr(s, "reflexes", [])]

    def all_scar_tags(self) -> List[str]:
        """Return a sorted list of all unique TCA tags in use across all scars."""
        tags = set()
        for s in self.scarlogic.scars:
            tags.update(getattr(s, "tca_tags", []))
        return sorted(tags)

    # --- Doctrine Grouping ---
    def group_doctrines_by_tag(self, tag: str) -> List[Any]:
        """Return all doctrines with the specified TCA tag."""
        return [d for d in self.doctrinespine.doctrines if tag in getattr(d, "tca_tags", [])]

    def group_doctrines_by_status(self, status: str) -> List[Any]:
        """Return all doctrines with the specified status."""
        return [d for d in self.doctrinespine.doctrines if getattr(d, "status", None) == status]

    def all_doctrine_tags(self) -> List[str]:
        """Return a sorted list of all unique TCA tags in use across all doctrines."""
        tags = set()
        for d in self.doctrinespine.doctrines:
            tags.update(getattr(d, "tca_tags", []))
        return sorted(tags)

    # --- Constellation Mapping (Symbolic Network) ---
    def constellation_by_tag(self, tag: str) -> Dict[str, List[Any]]:
        """
        Return a symbolic constellation: all scars and doctrines linked by the given tag.
        Useful for TCA, cluster analytics, and symbolic heatmaps.
        """
        return {
            "scars": self.group_scars_by_tag(tag),
            "doctrines": self.group_doctrines_by_tag(tag)
        }

    def constellation_by_reflex(self, reflex: str) -> Dict[str, List[Any]]:
        """
        Return a symbolic constellation: all scars and doctrines linked by a shared reflex (where applicable).
        """
        scars = self.group_scars_by_reflex(reflex)
        doctrines = [d for d in self.doctrinespine.doctrines if reflex in getattr(d, "mutation_lineage", [])] # Example: if doctrine lineage is reflex-linked
        return {
            "scars": scars,
            "doctrines": doctrines
        }

    # --- General Utilities ---
    def find_scar_tags_for_id(self, scar_id: str) -> List[str]:
        scar = self.scarlogic.get_scar(scar_id)
        return getattr(scar, "tca_tags", []) if scar else []

    def find_doctrine_tags_for_id(self, doctrine_id: str) -> List[str]:
        doctrine = self.doctrinespine.get_doctrine(doctrine_id)
        return getattr(doctrine, "tca_tags", []) if doctrine else []

    def summarize_constellation(self, tag: str) -> str:
        """
        Human-readable symbolic summary of a constellation (all scars/doctrines for a tag).
        """
        net = self.constellation_by_tag(tag)
        scars = net["scars"]
        doctrines = net["doctrines"]
        lines = [f"Constellation: {tag}"]
        lines.append(f"  Scars: {len(scars)}")
        for s in scars:
            lines.append(f"    - {getattr(s, 'id', '?')}: {getattr(s, 'name', '')}")
        lines.append(f"  Doctrines: {len(doctrines)}")
        for d in doctrines:
            lines.append(f"    - {getattr(d, 'id', '?')}: {getattr(d, 'name', '')}")
        return "\n".join(lines)

    # --- Additional Grouping Utilities ---
    def group_scars_by_status(self, status: str) -> List[Any]:
        """Return all scars with the specified decay_state/status."""
        return [s for s in self.scarlogic.scars if getattr(s, "decay_state", None) == status]

    def all_scar_types(self) -> List[str]:
        """Return all unique scar types in use."""
        return sorted(set(getattr(s, "type", None) for s in self.scarlogic.scars if getattr(s, "type", None)))

    def all_scar_reflexes(self) -> List[str]:
        """Return all unique reflexes across all scars."""
        reflexes = set()
        for s in self.scarlogic.scars:
            reflexes.update(getattr(s, "reflexes", []))
        return sorted(reflexes)

    # --- Adjacency/Linkage Utilities ---
    def list_linked_scars_for_doctrine(self, doctrine_id: str) -> List[Any]:
        """Return all scars linked to a doctrine by scar_links."""
        doctrine = self.doctrinespine.get_doctrine(doctrine_id)
        if doctrine:
            return [self.scarlogic.get_scar(sid) for sid in getattr(doctrine, "scar_links", []) if self.scarlogic.get_scar(sid)]
        return []

    def list_linked_doctrines_for_scar(self, scar_id: str) -> List[Any]:
        """Return all doctrines linked to a scar by linked_doctrines."""
        scar = self.scarlogic.get_scar(scar_id)
        if scar:
            return [self.doctrinespine.get_doctrine(did) for did in getattr(scar, "linked_doctrines", []) if self.doctrinespine.get_doctrine(did)]
        return []

    # --- Traversal/Lineage (Recursive) ---
    def traverse_doctrine_lineage(self, doctrine_id: str, depth: int = 3) -> List[Any]:
        """Trace doctrine's mutation lineage recursively up to depth."""
        visited = set()
        result = []
        def _recurse(did, d):
            if did in visited or len(result) >= depth:
                return
            visited.add(did)
            doctrine = self.doctrinespine.get_doctrine(did)
            if doctrine:
                result.append(doctrine)
                for prev in getattr(doctrine, "mutation_lineage", []):
                    _recurse(prev, d+1)
        _recurse(doctrine_id, 0)
        return result

    def traverse_scar_links(self, scar_id: str, depth: int = 3) -> List[Any]:
        """Trace all doctrine links recursively from a scar (scar->doctrines->scars...)."""
        visited = set()
        chain = []
        def _recurse(sid, d):
            if sid in visited or len(chain) >= depth:
                return
            visited.add(sid)
            scar = self.scarlogic.get_scar(sid)
            if scar:
                chain.append(scar)
                for did in getattr(scar, "linked_doctrines", []):
                    doctrine = self.doctrinespine.get_doctrine(did)
                    if doctrine:
                        for next_sid in getattr(doctrine, "scar_links", []):
                            _recurse(next_sid, d+1)
        _recurse(scar_id, 0)
        return chain

    # --- Advanced Human-Readable Summaries ---
    def summarize_lineage(self, doctrine_id: str, depth: int = 3) -> str:
        """Human-readable summary of doctrine's mutation lineage."""
        lineage = self.traverse_doctrine_lineage(doctrine_id, depth)
        lines = [f"Lineage for doctrine {doctrine_id}:"]
        for d in lineage:
            lines.append(f"- {getattr(d, 'id', '?')}: {getattr(d, 'name', '')}")
        return "\n".join(lines)

    def summarize_chain(self, scar_id: str, depth: int = 3) -> str:
        """Human-readable summary of scar's doctrinal linkage chain."""
        chain = self.traverse_scar_links(scar_id, depth)
        lines = [f"Scar chain for {scar_id}:"]
        for s in chain:
            lines.append(f"- {getattr(s, 'id', '?')}: {getattr(s, 'name', '')}")
        return "\n".join(lines)
