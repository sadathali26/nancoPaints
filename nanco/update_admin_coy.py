import re
import os

file_path = r"d:\Users\user\Desktop\working files\nanco_main\nanco\admin_products_of_the_year.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add CSS for modal
modal_css = """
        /* ── MODAL STYLES ── */
        .modal-overlay {
            position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000;
            display: flex; align-items: center; justify-content: center; backdrop-filter: blur(4px);
        }
        .modal-content {
            background: #fff; border-radius: 24px; width: 100%; max-width: 800px;
            padding: 32px; box-shadow: 0 24px 60px rgba(0,0,0,0.2); max-height: 90vh; overflow-y: auto;
        }
        .modal-header {
            display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;
        }
        .modal-header h3 { margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px; }
        .close-btn { background: none; border: none; font-size: 20px; cursor: pointer; color: var(--color-sage-mute); }
        .close-btn:hover { color: #000; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; margin-bottom: 8px; font-size: 14px; font-weight: 700; }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%; padding: 12px; border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; font-size: 14px; box-sizing: border-box;
        }
        .form-group textarea { resize: vertical; min-height: 80px; }
        
        /* Loading Overlay */
        .loading-overlay {
            position: absolute; inset: 0; background: rgba(255,255,255,0.8); z-index: 50;
            display: none; align-items: center; justify-content: center; font-weight: 700;
        }
"""
html = html.replace('</style>', modal_css + '\n    </style>')

# 2. Add Modal HTML and JS at the end of body
modal_html_js = """
    <!-- ── MODAL ── -->
    <div id="coyModal" class="modal-overlay" style="display: none;">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Add Product of the Year</h3>
                <button type="button" class="close-btn" onclick="closeModal()"><i class="fas fa-times"></i></button>
            </div>
            <div style="display: flex; gap: 32px; flex-wrap: wrap;">
                <form id="coyForm" onsubmit="submitCoy(event)" style="flex: 1; min-width: 300px; position: relative;">
                    <div id="formLoading" class="loading-overlay">Saving...</div>
                    <div class="form-group">
                        <label>Select Product</label>
                        <select id="coyProductSelect" required onchange="onProductSelect()">
                            <option value="">Loading products...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Title</label>
                        <input type="text" id="coyTitle" required oninput="updatePreview()">
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea id="coyDescription" required oninput="updatePreview()"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Top Image</label>
                        <input type="file" id="coyTopImage" accept="image/*" required onchange="updatePreview()">
                    </div>
                    <div class="form-group">
                        <label>Bottom Image</label>
                        <input type="file" id="coyBottomImage" accept="image/*" required onchange="updatePreview()">
                    </div>
                    <div style="margin-top: 24px;">
                        <button type="submit" class="btn-primary" style="width: 100%; justify-content: center;">Save Item</button>
                    </div>
                </form>

                <div class="preview-section" style="width: 280px; flex-shrink: 0;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 700;">Live Preview</label>
                    <div class="coy-item" style="pointer-events: none; margin: 0; position: relative; height: 420px; border-radius: 24px; overflow: hidden; background: #eee;">
                        <div class="coy-content split-layout" style="width:100%; height:100%; display:flex; flex-direction:column; justify-content:space-between;">
                            <div class="coy-img-wrap" style="position:relative; height:50%; width:100%;">
                                <img id="previewTopImg" style="width:100%; height:100%; object-fit:cover; display:none;">
                            </div>
                            <div class="coy-img-wrap" style="position:relative; height:50%; width:100%;">
                                <img id="previewBottomImg" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:none;">
                                <div class="coy-text-wrap" style="position:absolute; inset:0; display:flex; flex-direction:column; justify-content:space-between; align-items:flex-start; padding:24px; background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0) 25%, rgba(0,0,0,0) 65%, rgba(0,0,0,0.85) 100%);">
                                    <h3 id="previewTitle" class="coy-title" style="margin:0; color:#fff; font-size:24px; font-weight:800; text-shadow:0 2px 10px rgba(0,0,0,0.4);">Title</h3>
                                    <p id="previewDesc" class="coy-desc" style="margin:0 0 20px 0; color:rgba(255,255,255,0.95); font-size:14px; text-align:left; max-width:90%; text-shadow:0 2px 6px rgba(0,0,0,0.6);">Description</p>
                                    <span class="coy-explore" style="position:absolute; bottom:20px; right:24px; color:#fff; font-size:16px;"><i class="fas fa-chevron-right"></i></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE_URL = 'http://127.0.0.1:5000';
        let productsData = [];

        async function fetchProducts() {
            try {
                const res = await fetch(`${API_BASE_URL}/api/items`);
                const data = await res.json();
                productsData = data;
                const select = document.getElementById('coyProductSelect');
                select.innerHTML = '<option value="">Select a product</option>';
                data.forEach(p => {
                    select.innerHTML += `<option value="${p.id}" data-name="${p.name}">${p.name}</option>`;
                });
            } catch (err) {
                console.error(err);
                document.getElementById('coyProductSelect').innerHTML = '<option value="">Failed to load</option>';
            }
        }

        async function fetchCoyItems() {
            try {
                const res = await fetch(`${API_BASE_URL}/api/coy-items`);
                const data = await res.json();
                const grid = document.getElementById('adminCoyGrid');
                grid.innerHTML = '';
                data.forEach(item => {
                    grid.innerHTML += `
                        <div class="coy-item" style="position:relative; height:420px; border-radius:24px; overflow:hidden;">
                            <div class="admin-item-actions" style="position:absolute; top:12px; right:12px; z-index:20; display:flex; gap:8px;">
                                <button class="admin-action-btn delete" onclick="deleteCoy('${item.id}')" title="Delete"><i class="fas fa-trash"></i></button>
                            </div>
                            <div class="coy-content split-layout" style="width:100%; height:100%; display:flex; flex-direction:column;">
                                <div class="coy-img-wrap" style="height:50%; position:relative;">
                                    <img class="coy-fg" src="${item.top_image_url}" alt="${item.title}" style="width:100%; height:100%; object-fit:cover;">
                                </div>
                                <div class="coy-img-wrap" style="height:50%; position:relative;">
                                    <img class="coy-bg" src="${item.bottom_image_url}" alt="${item.title} Room" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover;">
                                    <div class="coy-text-wrap" style="position:absolute; inset:0; padding:24px; display:flex; flex-direction:column; justify-content:space-between; align-items:flex-start; background: linear-gradient(180deg, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0) 25%, rgba(0,0,0,0) 65%, rgba(0,0,0,0.85) 100%);">
                                        <h3 class="coy-title" style="margin:0; color:#fff; font-size:24px; font-weight:800; text-shadow:0 2px 10px rgba(0,0,0,0.4);">${item.title}</h3>
                                        <p class="coy-desc" style="margin:0 0 20px 0; color:rgba(255,255,255,0.95); font-size:14px; text-align:left; max-width:90%; text-shadow:0 2px 6px rgba(0,0,0,0.6);">${item.description}</p>
                                        <span class="coy-explore" style="position:absolute; bottom:20px; right:24px; color:#fff; font-size:16px;"><i class="fas fa-chevron-right"></i></span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
            } catch (err) {
                console.error(err);
            }
        }

        function openModal() {
            document.getElementById('coyModal').style.display = 'flex';
            document.getElementById('coyForm').reset();
            updatePreview();
        }

        function closeModal() {
            document.getElementById('coyModal').style.display = 'none';
        }

        function onProductSelect() {
            const select = document.getElementById('coyProductSelect');
            const selectedOption = select.options[select.selectedIndex];
            if (selectedOption.value) {
                const titleInput = document.getElementById('coyTitle');
                const descInput = document.getElementById('coyDescription');
                if (!titleInput.value) titleInput.value = selectedOption.getAttribute('data-name');
                if (!descInput.value) descInput.value = 'description';
            }
            updatePreview();
        }

        function updatePreview() {
            document.getElementById('previewTitle').innerText = document.getElementById('coyTitle').value || 'Title';
            document.getElementById('previewDesc').innerText = document.getElementById('coyDescription').value || 'Description';
            
            const topFile = document.getElementById('coyTopImage').files[0];
            if (topFile) {
                document.getElementById('previewTopImg').src = URL.createObjectURL(topFile);
                document.getElementById('previewTopImg').style.display = 'block';
            } else {
                document.getElementById('previewTopImg').style.display = 'none';
            }
            
            const bottomFile = document.getElementById('coyBottomImage').files[0];
            if (bottomFile) {
                document.getElementById('previewBottomImg').src = URL.createObjectURL(bottomFile);
                document.getElementById('previewBottomImg').style.display = 'block';
            } else {
                document.getElementById('previewBottomImg').style.display = 'none';
            }
        }

        async function submitCoy(e) {
            e.preventDefault();
            document.getElementById('formLoading').style.display = 'flex';
            
            const formData = new FormData();
            formData.append('product_id', document.getElementById('coyProductSelect').value);
            formData.append('title', document.getElementById('coyTitle').value);
            formData.append('description', document.getElementById('coyDescription').value);
            formData.append('top_image', document.getElementById('coyTopImage').files[0]);
            formData.append('bottom_image', document.getElementById('coyBottomImage').files[0]);
            
            try {
                const token = localStorage.getItem('adminToken') || 'super-secret-nanco-token';
                const res = await fetch(`${API_BASE_URL}/api/coy-items`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` },
                    body: formData
                });
                if (res.ok) {
                    closeModal();
                    fetchCoyItems();
                } else {
                    const data = await res.json();
                    alert(data.error || 'Failed to save');
                }
            } catch (err) {
                alert('Error saving product');
            } finally {
                document.getElementById('formLoading').style.display = 'none';
            }
        }

        async function deleteCoy(id) {
            if (!confirm('Are you sure you want to delete this featured product?')) return;
            const token = localStorage.getItem('adminToken') || 'super-secret-nanco-token';
            try {
                const res = await fetch(`${API_BASE_URL}/api/coy-items/${id}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    fetchCoyItems();
                } else {
                    alert('Failed to delete');
                }
            } catch (err) {
                alert('Error deleting');
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            fetchProducts();
            fetchCoyItems();
        });
    </script>
</body>
"""

# Replace static grid and add an ID for dynamic injection
grid_pattern = r'<div class="admin-coy-grid">.*?</div>\s*</div>\s*</main>'
new_grid = '<div class="admin-coy-grid" id="adminCoyGrid"></div>\n        </div>\n    </main>'
html = re.sub(grid_pattern, new_grid, html, flags=re.DOTALL)

# Add modal trigger
html = html.replace('<button class="btn-primary"><i class="fas fa-plus"></i> Add New Product</button>',
                    '<button class="btn-primary" onclick="openModal()"><i class="fas fa-plus"></i> Add New Product</button>')

html = html.replace('</body>', modal_html_js)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
