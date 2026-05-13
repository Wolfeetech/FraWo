import glob
import re

for file in glob.glob('Codex/website/*.html'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the duplicate required/checked/disabled
    content = content.replace('required="required="required""', 'required="required"')
    content = content.replace('checked="checked="checked""', 'checked="checked"')
    content = content.replace('disabled="disabled="disabled""', 'disabled="disabled"')
    
    # Just to be safe, also replace any remaining required="required="
    content = re.sub(r'required="required="[^"]*""', 'required="required"', content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
print('Fixed HTML attributes manually!')
