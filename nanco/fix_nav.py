import glob, re

for f in glob.glob('nanco/*.html'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # We replace the toggling logic to include e.stopImmediatePropagation()
    # It looks like: btn.addEventListener('click', () => {
    
    # We can use regex to find btn.addEventListener('click', () => { and replace it
    new_content = re.sub(
        r"btn\.addEventListener\('click',\s*\(\)\s*=>\s*\{(\s*)const\s+isOpen\s*=\s*nav\.classList\.toggle\('open'\);",
        r"btn.addEventListener('click', (e) => {\1e.stopImmediatePropagation();\1const isOpen = nav.classList.toggle('open');",
        content
    )
    
    if new_content != content:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f'Fixed {f}')
