import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.perception.spl import SPL

spl = SPL()
echo = spl.process_input("What is symbolic collapse?")
print(echo)
print("Intent:", spl.classify_intent(echo))
