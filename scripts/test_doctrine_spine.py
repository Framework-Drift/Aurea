import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.doctrine.doctrine_spine import DoctrineSpine
from src.utils.models import Doctrine
from datetime import datetime

spine = DoctrineSpine()

# Create a doctrine
doctrine = Doctrine(id="Doctrine-0", name="Collapse-Bearing Truth", created_at=datetime.now())
spine.add_doctrine(doctrine)

# Link a scar
spine.link_scar("Doctrine-0", "Δ001")
print("Doctrine after linking scar:", spine.get_doctrine("Doctrine-0"))

# Mutate doctrine
spine.mutate_doctrine("Doctrine-0", "Collapse-Bearing Wisdom")
print("Doctrine after mutation:", spine.get_doctrine("Doctrine-0"))
