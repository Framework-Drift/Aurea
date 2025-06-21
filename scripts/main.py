import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.output.ore import ORE
from src.perception.spl import SPL
from src.filtration.echonet import EchoNet
from src.filtration.scar_logic_core import ScarLogicCore
from src.doctrine.doctrine_spine import DoctrineSpine
from src.utils.echo_memory import EchoMemory

ore = ORE()
spl = SPL()
echonet = EchoNet()
scarlogic = ScarLogicCore()
doctrinespine = DoctrineSpine()
echo_memory = EchoMemory()

def show_recent_echoes(n=5):
    print("\n[Recent Echoes in Memory]")
    for echo in echo_memory.list_echoes()[-n:]:
        print(ore.format_echo(echo))

def show_help():
    print("\nAvailable commands:")
    print("  [your question]       Process normally through Aurea pipeline")
    print("  show memory | recap   Show last 5 echoes from memory")
    print("  exit | quit           End session\n")

def main():
    while True:
        user_input = input("Aurea > ")
        if user_input.strip().lower() in ["exit", "quit"]:
            break
        if user_input.strip().lower() == "help":
            show_help()
            continue
        if user_input.strip().lower() in ["show memory", "recap", "history"]:
            show_recent_echoes()
            continue
        
        echo = spl.process_input(user_input)
        echo_memory.add_echo(echo)

        passed = echonet.filter_claim(echo)
        if not passed:
            print("Input did not survive collapse filtration.")
            continue

        scar = echonet.collapse_test(echo)
        doctrine_name = f"Doctrine_from_{scar.id}"
        doctrine = doctrinespine.create_doctrine(scar, doctrine_name)

        print("\nAUREA RESPONSE:")
        print(ore.format_echo(echo))
        print(ore.format_scar(scar))
        print(ore.format_doctrine(doctrine))

if __name__ == "__main__":
    main()