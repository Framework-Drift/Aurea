import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.perception.spl import SPL
from src.filtration.echonet import EchoNet

spl = SPL()
echonet = EchoNet()

echo = spl.process_input("All truth must survive collapse.")
print("Echo:", echo)
passed = echonet.filter_claim(echo)
print("Passed filtration:", passed)

if passed:
    scar = echonet.collapse_test(echo)
    print("Scar formed:", scar)
else:
    print("No scar formed (input did not survive collapse filtration).")
