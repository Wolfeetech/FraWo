import glob
import re

for file in glob.glob('Codex/website/*.html'):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # regex sub: replace "required" followed by space or > or \n with "required='required'"
    # only if it doesn't already have an equals sign
    content = re.sub(r'\brequired(?!\s*=)', 'required="required"', content)
    content = re.sub(r'\bchecked(?!\s*=)', 'checked="checked"', content)
    content = re.sub(r'\bdisabled(?!\s*=)', 'disabled="disabled"', content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
print("Fix applied successfully!")
