import re

files = [
    "index.html",
    "admin_products_of_the_year.html"
]

def replace_item(match):
    indent = match.group(1)
    bg_asset = match.group(2)
    bg_alt = match.group(3)
    fg_asset = match.group(4)
    fg_alt = match.group(5)
    
    # We will use the same foreground image for top and bottom.
    return f"""{indent}<div class="coy-content split-layout">
{indent}  <div class="coy-img-wrap">
{indent}    <img class="coy-fg" data-asset="{fg_asset}" alt="{fg_alt}">
{indent}  </div>
{indent}  <div class="coy-img-wrap">
{indent}    <img class="coy-fg" data-asset="{fg_asset}" alt="{fg_alt} Bottom">
{indent}    <div class="coy-text-wrap">
{indent}      <h3 class="coy-title">{fg_alt}</h3>
{indent}      <p class="coy-desc">Perfect paints for painting the house foundations.</p>
{indent}      <span class="coy-explore"><i class="fas fa-chevron-right"></i></span>
{indent}    </div>
{indent}  </div>
{indent}</div>"""

# For index.html item 3 onwards:
# <div class="coy-content">
#   <img class="coy-bg" data-asset="palettes.bg3" alt="Dessert Love Room">
#   <div class="coy-img-wrap">
#     <img class="coy-fg" data-asset="palettes.fg3" alt="Dessert Love">
#   </div>
#   <div class="coy-text-wrap">
#     <span class="coy-explore"><i class="fas fa-chevron-right"></i></span>
#   </div>
# </div>

pattern_index_basic = r'([ \t]+)<div class="coy-content">\s*<img class="coy-bg" data-asset="([^"]+)" alt="([^"]+)">\s*<div class="coy-img-wrap">\s*<img class="coy-fg" data-asset="([^"]+)" alt="([^"]+)">\s*</div>\s*<div class="coy-text-wrap">\s*<span class="coy-explore"><i class="fas fa-chevron-right"></i></span>\s*</div>\s*</div>'

# For index.html item 1 (with Thara text):
pattern_index_1 = r'([ \t]+)<div class="coy-content">\s*<img class="coy-bg" data-asset="([^"]+)" alt="([^"]+)">\s*<div class="coy-img-wrap">\s*<img class="coy-fg" data-asset="([^"]+)" alt="([^"]+)">\s*</div>\s*<div class="coy-text-wrap">\s*<h3 class="coy-title">Thara</h3>\s*<p class="coy-desc">As this paints that we can use it for painting the house foundations.</p>\s*<span class="coy-explore"><i class="fas fa-chevron-right"></i></span>\s*</div>\s*</div>'

def replace_item_1(match):
    indent = match.group(1)
    fg_asset = match.group(4)
    fg_alt = match.group(5)
    return f"""{indent}<div class="coy-content split-layout">
{indent}  <div class="coy-img-wrap">
{indent}    <img class="coy-fg" data-asset="{fg_asset}" alt="{fg_alt}">
{indent}  </div>
{indent}  <div class="coy-img-wrap">
{indent}    <img class="coy-fg" data-asset="{fg_asset}" alt="{fg_alt} Bottom">
{indent}    <div class="coy-text-wrap">
{indent}      <h3 class="coy-title">Thara</h3>
{indent}      <p class="coy-desc">As this paints that we can use it for painting the house foundations.</p>
{indent}      <span class="coy-explore"><i class="fas fa-chevron-right"></i></span>
{indent}    </div>
{indent}  </div>
{indent}</div>"""


# For admin item 3 onwards (no text wrap):
# <div class="coy-content">
#   <img class="coy-bg" data-asset="palettes.bg3" alt="Dessert Love Room">
#   <div class="coy-img-wrap">
#       <img class="coy-fg" data-asset="palettes.fg3" alt="Dessert Love">
#   </div>
# </div>
pattern_admin_basic = r'([ \t]+)<div class="coy-content">\s*<img class="coy-bg" data-asset="([^"]+)" alt="([^"]+)">\s*<div class="coy-img-wrap">\s*<img class="coy-fg" data-asset="([^"]+)" alt="([^"]+)">\s*</div>\s*</div>'


for filename in files:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(pattern_index_1, replace_item_1, content)
    content = re.sub(pattern_index_basic, replace_item, content)
    content = re.sub(pattern_admin_basic, replace_item, content)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

print("Conversion complete.")
