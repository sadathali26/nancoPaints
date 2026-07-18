import re

files = [
    "index.html",
    "admin_products_of_the_year.html"
]

def repl(m):
    prefix = m.group(1)
    fg_asset = m.group(2)
    fg_alt = m.group(3)
    mid = m.group(4)
    
    num_match = re.search(r'\d+', fg_asset)
    if num_match:
        bg_asset = f"palettes.bg{num_match.group(0)}"
    else:
        bg_asset = fg_asset.replace('fg', 'bg')
        
    return f'{prefix}data-asset="{fg_asset}" alt="{fg_alt}">{mid}<img class="coy-bg" data-asset="{bg_asset}" alt="{fg_alt} Room">'

pattern = r'(<div class="coy-content split-layout">\s*<div class="coy-img-wrap">\s*<img class="coy-fg"\s+)data-asset="([^"]+)" alt="([^"]+)">(\s*</div>\s*<div class="coy-img-wrap">\s*)<img class="coy-fg" data-asset="[^"]+" alt="[^"]+">'

for filename in files:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = re.sub(pattern, repl, content)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("Conversion complete.")
