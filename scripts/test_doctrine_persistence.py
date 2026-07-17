import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.doctrine.doctrine_spine import DoctrineSpine
from src.utils.models import Doctrine
from datetime import datetime

filename = "data/doctrines.json"
spine = DoctrineSpine()

# Add a doctrine, save to file
doc = Doctrine(id="Doctrine-0", name="Collapse-Bearing Truth", created_at=datetime.now())
spine.add_doctrine(doc)
spine.save_to_file(filename)

print("Saved doctrines:", spine.doctrines)

# Load from file in a new instance
new_spine = DoctrineSpine()
new_spine.load_from_file(filename)
print("Loaded doctrines:", new_spine.doctrines)
