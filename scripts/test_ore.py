import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.output.ore import ORE
from src.utils.models import Echo, Scar, Doctrine
from datetime import datetime

ore = ORE()

echo = Echo(id="Echo-01", content="All truth must survive collapse.", source="user", resonance_score=0.9, created_at=datetime.now())
scar = Scar(id="Δ001", origin="Echo-01", weight=88.5, created_at=datetime.now())
doctrine = Doctrine(id="Doctrine-0", name="Collapse-Bearing Truth", scar_links=["Δ001"], created_at=datetime.now())

print(ore.format_echo(echo))
print(ore.format_scar(scar))
print(ore.format_doctrine(doctrine))
