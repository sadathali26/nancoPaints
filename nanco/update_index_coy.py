import re
import os

file_path = r"d:\Users\user\Desktop\working files\nanco_main\nanco\index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Replace coyTrack with empty div
track_pattern = r'<div class="coy-slider-track" id="coyTrack">.*?</div>\s*<button class="coy-btn coy-next" id="coyNext"'
new_track = '<div class="coy-slider-track" id="coyTrack">\n          <!-- Dynamically populated via JS -->\n        </div>\n        \n        <button class="coy-btn coy-next" id="coyNext"'
html = re.sub(track_pattern, new_track, html, flags=re.DOTALL)

# Add JS logic to fetch and render
script_addition = """
      document.addEventListener('DOMContentLoaded', () => {
        const track = document.getElementById('coyTrack');
        const btnPrev = document.getElementById('coyPrev');
        const btnNext = document.getElementById('coyNext');
        
        if (track && btnPrev && btnNext) {
          btnPrev.addEventListener('click', () => {
            track.scrollBy({ left: -300, behavior: 'smooth' });
          });
          btnNext.addEventListener('click', () => {
            track.scrollBy({ left: 300, behavior: 'smooth' });
          });
        }

        // Fetch dynamic Products of the Year
        async function loadCoyItems() {
          try {
            const res = await fetch('http://127.0.0.1:5000/api/coy-items');
            if (!res.ok) return;
            const items = await res.json();
            
            if (track) {
              track.innerHTML = '';
              items.forEach(item => {
                track.innerHTML += `
                  <a href="../nanco/colors.html?product_id=${item.product_id}" class="coy-item">
                    <div class="coy-content split-layout">
                      <div class="coy-img-wrap">
                        <img class="coy-fg" src="${item.top_image_url}" alt="${item.title}">
                      </div>
                      <div class="coy-img-wrap">
                        <img class="coy-bg" src="${item.bottom_image_url}" alt="${item.title} Room">
                        <div class="coy-text-wrap">
                          <h3 class="coy-title">${item.title}</h3>
                          <p class="coy-desc">${item.description}</p>
                          <span class="coy-explore"><i class="fas fa-chevron-right"></i></span>
                        </div>
                      </div>
                    </div>
                  </a>
                `;
              });
            }
          } catch (err) {
            console.error('Failed to load coy items:', err);
          }
        }
        
        loadCoyItems();
      });
"""
script_pattern = r"document\.addEventListener\('DOMContentLoaded', \(\) => {\s*const track = document\.getElementById\('coyTrack'\);.*?}\);.*?<\/script>"
# Wait, this regex might be tricky. Let's just do a string replace for the old slider init logic.
old_script_logic = """
      document.addEventListener('DOMContentLoaded', () => {
        const track = document.getElementById('coyTrack');
        const btnPrev = document.getElementById('coyPrev');
        const btnNext = document.getElementById('coyNext');
        
        if (track && btnPrev && btnNext) {
          btnPrev.addEventListener('click', () => {
            track.scrollBy({ left: -300, behavior: 'smooth' });
          });
          btnNext.addEventListener('click', () => {
            track.scrollBy({ left: 300, behavior: 'smooth' });
          });
        }
      });
"""

# Try simple replace first
if old_script_logic.strip() in html:
    html = html.replace(old_script_logic.strip(), script_addition.strip())
else:
    # If indentation is different, we can regex it
    # We'll just replace the whole DOMContentLoaded block for coyTrack
    import re
    html = re.sub(r"document\.addEventListener\('DOMContentLoaded', \(\) => {\s*const track = document\.getElementById\('coyTrack'\);.*?\s*}\);", script_addition.strip(), html, flags=re.DOTALL)


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
