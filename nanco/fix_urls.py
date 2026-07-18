import os
import glob
import re

html_files = glob.glob('*.html')
pattern_strict = re.compile(r"const\s+API_BASE_URL\s*=\s*['\"`]http://127\.0\.0\.1:5000['\"`];")
pattern_ternary = re.compile(r"const\s+API_BASE_URL\s*=\s*window\.location\.hostname\s*===\s*['\"`]127\.0\.0\.1['\"`]\s*\|\|\s*window\.location\.hostname\s*===\s*['\"`]localhost['\"`]\s*\?\s*['\"`]http://127\.0\.0\.1:5000['\"`]\s*:\s*['\"`]https://nanco-backend\.onrender\.com['\"`];")

replacement = """const API_BASE_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost' 
          ? 'http://127.0.0.1:5000' 
          : '';"""

for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = pattern_strict.sub(replacement, content)
    new_content = pattern_ternary.sub(replacement, new_content)
    
    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {file}')
