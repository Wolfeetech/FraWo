import json
import re
import sys
import argparse

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path")
    args = parser.parse_args()
    
    try:
        with open(args.file_path, "r", encoding="utf-16") as f:
            content = f.read()

        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)
            
            if "out-data" in data and data["out-data"]:
                print("--- STDOUT ---")
                print(data["out-data"])
                
            if "err-data" in data and data["err-data"]:
                print("--- STDERR ---")
                print(data["err-data"])
                
            print(f"\nExit Code: {data.get('exitcode')}")
        else:
            print("No JSON found in file.")
            print(content[:500])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
