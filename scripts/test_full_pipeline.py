import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.perception.spl import SPL
from src.filtration.echonet import EchoNet
from src.filtration.scar_logic_core import ScarLogicCore
from src.doctrine.doctrine_spine import DoctrineSpine
from src.utils.models import Doctrine
from datetime import datetime

# Initialize system modules
spl = SPL()
echonet = EchoNet()
scar_core = ScarLogicCore()
doctrine_spine = DoctrineSpine()

# Step 1: Create a doctrine (if none exist)
doctrine = Doctrine(id="Doctrine-0", name="Collapse-Bearing Truth", created_at=datetime.now())
doctrine_spine.add_doctrine(doctrine)

# Step 2: User input
raw_input = "All truth must survive collapse."
echo = spl.process_input(raw_input)
print("Echo object:", echo)

# Step 3: Filtration (EchoNet)
if echonet.filter_claim(echo):
    print("Echo survived filtration (collapse-resistant).")
    scar = echonet.collapse_test(echo)
    print("Scar formed:", scar)
    scar_core.add_scar(scar)

    # Step 4: Link scar to doctrine
    doctrine_spine.link_scar(doctrine.id, scar.id)
    print("Doctrine after linking scar:", doctrine_spine.get_doctrine(doctrine.id))
else:
    print("Echo did NOT survive filtration (no scar/doctrine linkage).")

# Step 5: Show all active scars
print("Active scars in ScarLogicCore:", scar_core.get_active_scars())
