import json
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

try:
    with open("c:/WORKSPACE/FraWo/scratch/odoo_tasks_output.txt", "r", encoding="utf-16") as f:
        raw_content = f.read()

    # Let's clean the string of any surrounding warning messages from SSH
    # and find the JSON structure
    start_idx = raw_content.find('{')
    end_idx = raw_content.rfind('}')
    if start_idx != -1 and end_idx != -1:
        json_str = raw_content[start_idx:end_idx+1]
        data = json.loads(json_str)
        print("JSON keys found:", list(data.keys()))
        
        # In case the warning permanently added is inside the stdout or there are multiple outputs
        for key in ["out-data", "err-data"]:
            if key in data and data[key]:
                val = data[key]
                # Filter out any non-ascii characters before decoding
                ascii_val = "".join([c for c in val if ord(c) < 128 and not c.isspace()])
                try:
                    # Pad the base64 string if necessary
                    missing_padding = len(ascii_val) % 4
                    if missing_padding:
                        ascii_val += '=' * (4 - missing_padding)
                    decoded = base64.b64decode(ascii_val).decode("utf-8", errors="replace")
                    print(f"\n--- {key.upper()} ---")
                    print(decoded)
                except Exception as e:
                    print(f"Error decoding {key}: {e}")
                    # Print a snippet of the value
                    print(f"Snippet of {key}: {val[:100]}...")
                    
        print(f"\nExit Code: {data.get('exitcode')}")
    else:
        print("JSON structure not found in file content.")
        print("Raw content start:")
        print(raw_content[:500])
except Exception as e:
    print(f"Error: {e}")
