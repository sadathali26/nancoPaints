import re
import sys
import os

target_files = [
    "products.html",
    "services.html",
    "colors.html",
    "calculators.html",
    "paint_visualizer.html",
    "about_us.html"
]

# Read index.html
with open("index.html", "r", encoding="utf-8") as f:
    index_content = f.read()

# 1. Extract the HTML/CSS/JS block between </ul> and </nav>
nav_tail_match = re.search(r'(</ul>\s*)(<div class="nav-search-bar">.*?</nav>)', index_content, re.DOTALL)
if not nav_tail_match:
    print("Could not find nav tail in index.html")
    sys.exit(1)

nav_tail_replacement = nav_tail_match.group(2)

# 2. Extract mobile nav toggle and lang toggle JS
mobile_nav_js = re.search(r'(// Mobile nav toggle.*?// Close on outside click.*?\}\);)', index_content, re.DOTALL)
lang_toggle_js = re.search(r'(// Language switcher toggle.*?\}\n    \})', index_content, re.DOTALL)

js_to_append = ""
if mobile_nav_js:
    js_to_append += "\n" + mobile_nav_js.group(1) + "\n"
if lang_toggle_js:
    js_to_append += "\n" + lang_toggle_js.group(1) + "\n"

# 3. Inject JS into the <script> block of nav_tail_replacement
if js_to_append:
    script_match = re.search(r'(<script>)(.*?)(</script>)', nav_tail_replacement, re.DOTALL)
    if script_match:
        new_script = script_match.group(1) + script_match.group(2) + "\n" + js_to_append + "\n" + script_match.group(3)
        nav_tail_replacement = nav_tail_replacement[:script_match.start()] + new_script + nav_tail_replacement[script_match.end():]

# 4. Patch target files
for file in target_files:
    try:
        if not os.path.exists(file):
            print(f"{file} does not exist. Skipping.")
            continue
            
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # We need to replace everything from </ul> to </nav> in the target file
        patched_content = re.sub(r'</ul>.*?</nav>', '</ul>\n      ' + nav_tail_replacement.strip(), content, flags=re.DOTALL)
        
        with open(file, "w", encoding="utf-8") as f:
            f.write(patched_content)
        print(f"Patched {file}")
    except Exception as e:
        print(f"Error patching {file}: {e}")
