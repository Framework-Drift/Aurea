import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.models import Scar, Doctrine, Echo
from datetime import datetime

# Test Scar creation
scar = Scar(
    id="Δ001",
    origin="Doctrine-0",
    weight=87.5,
    created_at=datetime.now(),
    linked_doctrines=["Doctrine-0"],
)

# Test Doctrine creation
doctrine = Doctrine(id="Doctrine-0", name="Collapse-Bearing Truth", scar_links=["Δ001"])

# Test Echo creation
echo = Echo(
    id="Echo-01",
    content="All truth must survive collapse.",
    source="user",
    resonance_score=0.92,
    created_at=datetime.now(),
    doctrine_link="Doctrine-0",
)

print(scar)
print(doctrine)
print(echo)
