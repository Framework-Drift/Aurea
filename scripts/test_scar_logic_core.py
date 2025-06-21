import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.filtration.scar_logic_core import ScarLogicCore
from src.utils.models import Scar
from datetime import datetime

scar_core = ScarLogicCore()

# Create two scars
scar1 = Scar(id="Δ001", origin="Echo-01", weight=80.0, created_at=datetime.now())
scar2 = Scar(id="Δ002", origin="Echo-02", weight=90.0, created_at=datetime.now())

# Add scars
scar_core.add_scar(scar1)
scar_core.add_scar(scar2)

# Show active scars
print("Active scars:", scar_core.get_active_scars())

# Decay one scar
scar_core.decay_scar("Δ001")
print("Active scars after decay:", scar_core.get_active_scars())
print("Scar Δ001:", scar_core.get_scar("Δ001"))
