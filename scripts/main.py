import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.symbolic_grouping import SymbolicGrouping
from src.output.ore import ORE
from src.perception.spl import SPL
from src.filtration.echonet import EchoNet
from src.filtration.scar_logic_core import ScarLogicCore
from src.doctrine.doctrine_spine import DoctrineSpine
from src.utils.echo_memory import EchoMemory
from src.output.srg import SRG
from src.utils.symbolic_grouping import SymbolicGrouping

ore = ORE()
spl = SPL()
echonet = EchoNet()
scarlogic = ScarLogicCore()
doctrinespine = DoctrineSpine()
echo_memory = EchoMemory()
srg = SRG(scarlogic, doctrinespine, ore)
symbolic = SymbolicGrouping(scarlogic, doctrinespine)
def show_recent_echoes(n=5):
    print("\n[Recent Echoes in Memory]")
    for echo in echo_memory.list_echoes()[-n:]:
        print(ore.format_echo(echo))

def show_help():
    print("\nAvailable commands:")
    print("  [your question]                      Process normally through Aurea pipeline")
    print("  show memory | recap                   Show last 5 echoes from memory")
    print("  recap scars [n] [status]              List [n] recent scars, optionally by status (active, fossil, etc.)")
    print("  recap doctrines [n] [status]          List [n] recent doctrines, optionally by status (active, fossil, etc.)")
    print("  describe scar [id|partial|tag]        Full detail for scar by id, partial name, or tag")
    print("  describe doctrine [id|partial|tag]    Full detail for doctrine by id, partial name, or tag")
    print("  search scars [query]                  Find scars by text/tag/field")
    print("  search doctrines [query]              Find doctrines by text/tag/field")
    print("  group scars by [tag/type/reflex/status]   List scars by any field")
    print("  group doctrines by [tag/status]           List doctrines by tag or status")
    print("  list scar tags                        Show all unique scar tags")
    print("  list doctrine tags                    Show all unique doctrine tags")
    print("  constellation [tag]                   Show all scars and doctrines with a shared tag")
    print("  trace doctrine [id]                   Show the full mutation lineage for a doctrine")
    print("  trace scar [id]                       Trace all doctrinal links from a scar")
    print("  list linked scars [doctrine id]       List all scars linked to a doctrine")
    print("  list linked doctrines [scar id]       List all doctrines linked to a scar")
    print("  exit | quit                           End session\n")
    print()

def smart_describe_scar(query):
    # Try by exact id
    scar = scarlogic.get_scar(query)
    if scar:
        print(srg.describe_scar(scar.id))
        return
    # Try by partial name
    matches = [s for s in scarlogic.scars if query.lower() in getattr(s, "name", "").lower()]
    if not matches:
        # Try by TCA tag
        matches = [s for s in scarlogic.scars if query in getattr(s, "tca_tags", [])]
    if matches:
        print(f"\n[Multiple matches, showing first] ID: {matches[0].id} Name: {matches[0].name}")
        print(srg.describe_scar(matches[0].id))
    else:
        print(f"No scar found for query: {query}")

def smart_describe_doctrine(query):
    doctrine = doctrinespine.get_doctrine(query)
    if doctrine:
        print(srg.describe_doctrine(doctrine.id))
        return
    matches = [d for d in doctrinespine.doctrines if query.lower() in getattr(d, "name", "").lower()]
    if not matches:
        matches = [d for d in doctrinespine.doctrines if query in getattr(d, "tca_tags", [])]
    if matches:
        print(f"\n[Multiple matches, showing first] ID: {matches[0].id} Name: {matches[0].name}")
        print(srg.describe_doctrine(matches[0].id))
    else:
        print(f"No doctrine found for query: {query}")

def search_scars(query):
    found = [s for s in scarlogic.scars if query.lower() in getattr(s, "name", "").lower() or
                                          query.lower() in getattr(s, "description", "").lower() or
                                          query in getattr(s, "tca_tags", [])]
    if found:
        print(f"\n[Matching scars ({len(found)})]")
        for s in found:
            print(f"- {s.id}: {s.name} [tags: {', '.join(getattr(s, 'tca_tags', []))}]")
    else:
        print("No matching scars found.")

def search_doctrines(query):
    found = [d for d in doctrinespine.doctrines if query.lower() in getattr(d, "name", "").lower() or
                                               query.lower() in getattr(d, "description", "").lower() or
                                               query in getattr(d, "tca_tags", [])]
    if found:
        print(f"\n[Matching doctrines ({len(found)})]")
        for d in found:
            print(f"- {d.id}: {d.name} [tags: {', '.join(getattr(d, 'tca_tags', []))}]")
    else:
        print("No matching doctrines found.")

def main():
    show_help()
    while True:
        user_input = input("Aurea > ")
        cmd = user_input.strip().lower()

        # 1. Exit
        if cmd in ["exit", "quit"]:
            break

        # 2. Help
        if cmd == "help":
            show_help()
            continue

        # 3. Echo memory
        if cmd in ["show memory", "recap", "history"]:
            show_recent_echoes()
            continue

        # 4. Recap scars
        prefix = "recap scars"
        if cmd.startswith(prefix):
            tokens = cmd.split()
            n = int(tokens[2]) if len(tokens) > 2 and tokens[2].isdigit() else 5
            status = tokens[3] if len(tokens) > 3 else None
            print("\n[SCAR SUMMARY]")
            print(srg.recap_scars(n=n, status=status))
            continue

        # 5. Recap doctrines
        prefix = "recap doctrines"
        if cmd.startswith(prefix):
            tokens = cmd.split()
            n = int(tokens[2]) if len(tokens) > 2 and tokens[2].isdigit() else 5
            status = tokens[3] if len(tokens) > 3 else None
            print("\n[DOCTRINE SUMMARY]")
            print(srg.recap_doctrines(n=n, status=status))
            continue

        # 6. Describe scar
        prefix = "describe scar "
        if cmd.startswith(prefix):
            query = user_input[len(prefix):].strip()
            print("\n[SCAR DETAIL]")
            smart_describe_scar(query)
            continue

        # 7. Describe doctrine
        prefix = "describe doctrine "
        if cmd.startswith(prefix):
            query = user_input[len(prefix):].strip()
            print("\n[DOCTRINE DETAIL]")
            smart_describe_doctrine(query)
            continue

        # 8. Search scars
        prefix = "search scars "
        if cmd.startswith(prefix):
            query = user_input[len(prefix):].strip()
            search_scars(query)
            continue

        # 9. Search doctrines
        prefix = "search doctrines "
        if cmd.startswith(prefix):
            query = user_input[len(prefix):].strip()
            search_doctrines(query)
            continue

        # 10. Group scars by field (tag, status, reflex, type)
        prefix = "group scars by "
        if cmd.startswith(prefix):
            remainder = cmd[len(prefix):].strip()
            args = remainder.split(" ", 1)
            if len(args) == 2:
                field, value = args
            elif len(args) == 1:
                field, value = "tag", args[0]
            else:
                print("Specify a value, e.g., group scars by tag identity")
                continue
            if field == "tag":
                scars = symbolic.group_scars_by_tag(value)
            elif field == "status":
                scars = symbolic.group_scars_by_status(value)
            elif field == "reflex":
                scars = symbolic.group_scars_by_reflex(value)
            elif field == "type":
                scars = symbolic.group_scars_by_type(value)
            else:
                print(f"Unknown field for scar grouping: {field}")
                continue
            if scars:
                print(f"\n[Scars with {field} '{value}'] ({len(scars)})")
                for s in scars:
                    print(f"- {s.id}: {getattr(s, 'name', '')}")
            else:
                print(f"No scars found with {field}: {value}")
            continue

        # 11. Group doctrines by field (tag, status)
        prefix = "group doctrines by "
        if cmd.startswith(prefix):
            remainder = cmd[len(prefix):].strip()
            args = remainder.split(" ", 1)
            if len(args) == 2:
                field, value = args
            elif len(args) == 1:
                field, value = "tag", args[0]
            else:
                print("Specify a value, e.g., group doctrines by tag collapse")
                continue
            if field == "tag":
                doctrines = symbolic.group_doctrines_by_tag(value)
            elif field == "status":
                doctrines = symbolic.group_doctrines_by_status(value)
            else:
                print(f"Unknown field for doctrine grouping: {field}")
                continue
            if doctrines:
                print(f"\n[Doctrines with {field} '{value}'] ({len(doctrines)})")
                for d in doctrines:
                    print(f"- {d.id}: {getattr(d, 'name', '')}")
            else:
                print(f"No doctrines found with {field}: {value}")
            continue

        # 12. Constellation by tag
        prefix = "constellation "
        if cmd.startswith(prefix):
            tag = user_input[len(prefix):].strip()
            print()
            print(symbolic.summarize_constellation(tag))
            continue

        # 13. List all scar or doctrine tags
        if cmd == "list scar tags":
            print("\nScar tags:")
            print(", ".join(symbolic.all_scar_tags()))
            continue
        if cmd == "list doctrine tags":
            print("\nDoctrine tags:")
            print(", ".join(symbolic.all_doctrine_tags()))
            continue

        # 14. Chain/lineage CLI
        prefix = "trace doctrine "
        if cmd.startswith(prefix):
            doctrine_id = user_input[len(prefix):].strip()
            print(symbolic.summarize_lineage(doctrine_id, depth=5))
            continue

        prefix = "trace scar "
        if cmd.startswith(prefix):
            scar_id = user_input[len(prefix):].strip()
            print(symbolic.summarize_chain(scar_id, depth=5))
            continue

        prefix = "list linked scars "
        if cmd.startswith(prefix):
            doctrine_id = user_input[len(prefix):].strip()
            scars = symbolic.list_linked_scars_for_doctrine(doctrine_id)
            if scars:
                print(f"Scars linked to {doctrine_id}:")
                for s in scars:
                    print(f"- {s.id}: {getattr(s, 'name', '')}")
            else:
                print("No scars found.")
            continue

        prefix = "list linked doctrines "
        if cmd.startswith(prefix):
            scar_id = user_input[len(prefix):].strip()
            doctrines = symbolic.list_linked_doctrines_for_scar(scar_id)
            if doctrines:
                print(f"Doctrines linked to {scar_id}:")
                for d in doctrines:
                    print(f"- {d.id}: {getattr(d, 'name', '')}")
            else:
                print("No doctrines found.")
            continue

        # --- PIPELINE: Process as symbolic input ---
        echo = spl.process_input(user_input)
        echo_memory.add_echo(echo)

        collapse_result = echonet.filter_claim(echo)
        if not collapse_result.passed:
            print(f"Input did not survive collapse filtration. Reason: {collapse_result.reason}")
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
