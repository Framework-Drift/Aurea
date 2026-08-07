"""
spl.py - Symbolic Perception Layer for Aurea
Normalizes and classifies all input for downstream filtration.

    ~~Normalizes and classifies all input, PRODUCING ECHO OBJECTS for
    downstream filtration.~~

SUPERSEDED 2026-08-05 BY RULING 75, old text kept verbatim. **This layer no
longer produces Echo objects**: it normalizes content, and `EchoMemory` - the
writer - mints identity and constructs the record (Ruling 69's law). The struck
sentence is the record of what this file used to be responsible for, and of the
seam that let a wall-clock id onto every perception AUREA has ever had.

`datetime` is no longer imported, and that absence is the deletion's proof: this
module cannot mint from a clock because it can no longer read one.
"""

from src.utils.models import Echo

class SPL:
    """
    Symbolic Perception Layer for Aurea input.
    """

    def normalize(self, raw_input: str) -> str:
        """
        Normalize raw input into the CONTENT of a perception.
        Args:
            raw_input (str): The unprocessed input.
        Returns:
            str: The normalized content. **Not an Echo, and not an identity.**

        RULING 75 (2026-08-05): **SPL STOPS MINTING, AND THE ENFORCEMENT IS
        THAT IT NO LONGER CONSTRUCTS AN ECHO AT ALL.**

            ~~`process_input(self, raw_input, doctrine_link=None, *,
            claim_id=None) -> Echo`~~, whose body built:

                ~~echo = Echo(
                      id=f"Echo-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                      content=cleaned, resonance_score=1.0,
                      created_at=datetime.now(),
                      doctrine_link=doctrine_link, claim_id=claim_id)~~

            DELETED, history kept, because the deleted body IS the record of
            the defect: **this layer minted the identity of every perception
            AUREA has ever had, from a wall clock, while owning no store.**

        THE SEAM IS SPLIT WHERE THE AUTHORITY ALREADY LAY. Ruling 69's law is
        that the WRITER owns the mint, and SPL is not the writer - `EchoMemory`
        is. A wall-clock id is unique only by luck of microsecond spacing and
        orders by WHEN rather than by WHAT; the ledger derives its ordinal from
        the file at the moment of minting, which is the property this project
        has now ruled on three times.

        So: **SPL produces CONTENT, the ledger mints IDENTITY.** The remaining
        fields (`doctrine_link`, `claim_id`, `resonance_score`) were never SPL's
        to decide either - they are carried by the caller and handed to
        `EchoMemory.record`, which is where `claim_id` is now set at
        construction, exactly as Ruling 60 requires. The law did not change; the
        construction site moved, and the law moved with it.

        DELETION RATHER THAN DEPRECATION (Rulings 61 / 65 / 68's form): a method
        that still constructs an Echo, however unused, is a loaded gun for the
        next caller who reaches for it. `Echo` survives below only as the type
        `classify_intent` reads.
        """
        # (Placeholder normalization - can add more logic later)
        return raw_input.strip()

    def classify_intent(self, echo: Echo) -> str:
        """
        Classify input intent (stub for future expansion).
        Args:
            echo (Echo): Input echo object.
        Returns:
            str: Classified intent (e.g., 'question', 'claim', 'command').
        """
        # Placeholder: add NLP or rule-based logic later
        content = echo.content.lower()
        if content.endswith('?'):
            return 'question'
        elif content.startswith('do ') or content.startswith('please '):
            return 'command'
        else:
            return 'claim'
