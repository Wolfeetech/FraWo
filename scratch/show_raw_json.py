import json
import re

try:
    with open("c:/WORKSPACE/FraWo/scratch/odoo_tasks_output.txt", "r", encoding="utf-16") as f:
        content = f.read()

    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        json_str = match.group(0)
        data = json.loads(json_str)
        print("JSON keys:", list(data.keys()))
        if "out-data" in data and data["out-data"]:
            val = data["out-data"]
            print(f"out-data length: {len(val)}")
            codes = [ord(c) for c in val[:100]]
            print("First 100 char codes:")
            print(codes)
            # Print as ascii string if printable, otherwise hex code
            printable = []
            for c in val[:50]:
                o = ord(c)
                if 32 <= o < 127:
                    printable.append(c)
                else:
                    printable.append(f"\\u{o:04x}")
            print("Visual representation:")
            print("".join(printable))
    else:
        print("No JSON found.")
except Exception as e:
    print(f"Error: {e}")
