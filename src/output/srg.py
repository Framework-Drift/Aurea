"""
srg.py - Self-Reflection Generator for Aurea
Aggregates and summarizes scars, doctrines, and mutation lineage for symbolic recap and reflection.
"""

from src.output.ore import ORE
from src.filtration.scar_logic_core import ScarLogicCore
from src.doctrine.doctrine_spine import DoctrineSpine

class SRG:
    """
    Self-Reflection Generator: Symbolic summary/recap engine for Aurea.
    """
    def __init__(self, scarlogic: ScarLogicCore, doctrinespine: DoctrineSpine, ore: ORE):
        self.scarlogic = scarlogic
        self.doctrinespine = doctrinespine
        self.ore = ore

    def recap_scars(self, n=5, status=None):
        """
        Recap the n most recent scars (optionally by status: active, fossil, etc).
        """
        scars = self.scarlogic.scars
        if status:
            scars = [s for s in scars if s.decay_state == status]
        scars = sorted(scars, key=lambda s: s.created_at, reverse=True)[:n]
        return "\n".join([self.ore.format_scar(s) for s in scars])

    def recap_doctrines(self, n=5, status=None):
        """
        Recap the n most recent doctrines (optionally by status: active, fossil, etc).
        """
        doctrines = self.doctrinespine.doctrines
        if status:
            doctrines = [d for d in doctrines if d.status == status]
        doctrines = sorted(doctrines, key=lambda d: d.created_at, reverse=True)[:n]
        return "\n".join([self.ore.format_doctrine(d) for d in doctrines])

    def describe_scar(self, scar_id):
        """
        Give a full symbolic description of a scar.
        """
        scar = self.scarlogic.get_scar(scar_id)
        if scar:
            lines = [
                f"ID: {scar.id}",
                f"Name: {scar.name}",
                f"Origin: {scar.origin}",
                f"Type: {scar.type}",
                f"Weight: {scar.weight}",
                f"Status: {scar.decay_state}",
                f"Linked Doctrines: {scar.linked_doctrines}",
                f"Reflexes: {scar.reflexes}",
                f"TCA Tags: {scar.tca_tags}",
                f"Echo Proximity: {scar.echo_proximity}",
                f"Description: {scar.description}",
                f"Seed: {scar.is_seed}",
                f"Created: {scar.created_at}",
            ]
            return "\n".join(lines)
        else:
            return f"No scar found with id: {scar_id}"

    def describe_doctrine(self, doctrine_id):
        """
        Give a full symbolic description of a doctrine.
        """
        doctrine = self.doctrinespine.get_doctrine(doctrine_id)
        if doctrine:
            lines = [
                f"ID: {doctrine.id}",
                f"Name: {doctrine.name}",
                f"Status: {doctrine.status}",
                f"Linked Scars: {doctrine.scar_links}",
                f"Mutation Lineage: {doctrine.mutation_lineage}",
                f"Description: {doctrine.description}",
                f"TCA Tags: {doctrine.tca_tags}",
                f"Seed: {doctrine.is_seed}",
                f"Created: {doctrine.created_at}",
                f"Last Mutated: {doctrine.last_mutated}",
            ]
            return "\n".join(lines)
        else:
            return f"No doctrine found with id: {doctrine_id}"
