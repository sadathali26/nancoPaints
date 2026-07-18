import re

file_path = r"d:\Users\user\Desktop\working files\nanco_main\nanco\admin_products_of_the_year.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# Replace the entire modal and JS section
new_modal_and_js = """
    <!-- ── MODAL ── -->
    <div id="coyModal" class="modal-overlay" style="display: none;">
        <div class="modal-content" style="max-width: 400px; padding: 24px;">
            <div class="modal-header" style="margin-bottom: 16px;">
                <h3>Add Product</h3>
                <button type="button" class="close-btn" onclick="closeModal()"><i class="fas fa-times"></i></button>
            </div>
            
            <div id="formLoading" class="loading-overlay" style="border-radius: 24px;">Saving...</div>
            
            <div class="form-group" style="margin-bottom: 16px;">
                <select id="coyProductSelect" required onchange="onProductSelect()" style="width: 100%; padding: 12px; border-radius: 12px; border: 1px solid rgba(0,0,0,0.1); font-weight: 600; appearance: none; background: #f9f9f9;">
                    <option value="">Select a product...</option>
                </select>
            </div>

            <!-- Interactive Card -->
            <div style="display: flex; justify-content: center; margin-bottom: 24px;">
                <div class="coy-item" style="margin: 0; position: relative; height: 420px; width: 280px; border-radius: 24px; overflow: hidden; background: #eee; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                    
                    <div class="coy-content split-layout" style="width:100%; height:100%; display:flex; flex-direction:column; justify-content:space-between;">
                        
                        <!-- Top Half (Foreground) -->
                        <div class="coy-img-wrap" style="position:relative; height:50%; width:100%; background: #e0e0e0; display:flex; align-items:center; justify-content:center; cursor: pointer;" onclick="document.getElementById('coyTopImage').click()">
                            <img id="previewTopImg" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:none; pointer-events: none;">
                            <div style="z-index:10; background:rgba(255,255,255,0.9); padding:8px 16px; border-radius:99px; font-size:12px; font-weight:700; box-shadow:0 4px 12px rgba(0,0,0,0.1);"><i class="fas fa-upload"></i> Top Image</div>
                            <input type="file" id="coyTopImage" accept="image/*" style="display:none;" onchange="handleImageUpload(this, 'previewTopImg')">
                        </div>

                        <!-- Bottom Half (Background) -->
                        <div class="coy-img-wrap" style="position:relative; height:50%; width:100%; background: #d0d0d0; display:flex; align-items:center; justify-content:center;">
                            <img id="previewBottomImg" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:none; pointer-events: none;">
                            
                            <!-- Upload Button overlaid on bottom half -->
                            <div style="position:absolute; top: 16px; left: 50%; transform: translateX(-50%); z-index:20; background:rgba(255,255,255,0.9); padding:8px 16px; border-radius:99px; font-size:12px; font-weight:700; box-shadow:0 4px 12px rgba(0,0,0,0.1); cursor: pointer;" onclick="document.getElementById('coyBottomImage').click()"><i class="fas fa-upload"></i> Bottom Image</div>
                            <input type="file" id="coyBottomImage" accept="image/*" style="display:none;" onchange="handleImageUpload(this, 'previewBottomImg')">

                            <div class="coy-text-wrap" style="position:absolute; inset:0; display:flex; flex-direction:column; justify-content:space-between; align-items:flex-start; padding:24px; background: linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0) 25%, rgba(0,0,0,0) 50%, rgba(0,0,0,0.9) 100%); pointer-events: none;">
                                
                                <!-- Editable Title -->
                                <h3 id="previewTitle" class="coy-title" contenteditable="true" style="margin:0; color:#fff; font-size:24px; font-weight:800; text-shadow:0 2px 10px rgba(0,0,0,0.4); pointer-events: all; border-bottom: 1px dashed rgba(255,255,255,0.5); min-width: 100px; outline: none;" onfocus="this.style.borderBottom='1px solid #fff'" onblur="this.style.borderBottom='1px dashed rgba(255,255,255,0.5)'">Title</h3>
                                
                                <!-- Editable Description -->
                                <p id="previewDesc" class="coy-desc" contenteditable="true" style="margin:0 0 20px 0; color:rgba(255,255,255,0.95); font-size:13px; text-align:left; max-width:90%; text-shadow:0 2px 6px rgba(0,0,0,0.6); pointer-events: all; border-bottom: 1px dashed rgba(255,255,255,0.3); min-width: 100px; outline: none;" onfocus="this.style.borderBottom='1px solid #fff'" onblur="this.style.borderBottom='1px dashed rgba(255,255,255,0.3)'">Edit this description directly...</p>
                                
                                <span class="coy-explore" style="position:absolute; bottom:20px; right:24px; color:#fff; font-size:16px;"><i class="fas fa-chevron-right"></i></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <button type="button" class="btn-primary" style="width: 100%; justify-content: center; padding: 14px; font-size: 16px;" onclick="submitCoy()">Save Featured Product</button>
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
                select.innerHTML = '<option value="">Select a product...</option>';
                data.forEach(p => {
                    select.innerHTML += `<option value="${p.id}" data-name="${p.item_name}">${p.item_name}</option>`;
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
            document.getElementById('coyProductSelect').value = '';
            document.getElementById('previewTitle').innerText = 'Title';
            document.getElementById('previewDesc').innerText = 'Edit this description directly...';
            document.getElementById('previewTopImg').style.display = 'none';
            document.getElementById('previewBottomImg').style.display = 'none';
            document.getElementById('coyTopImage').value = '';
            document.getElementById('coyBottomImage').value = '';
        }

        function closeModal() {
            document.getElementById('coyModal').style.display = 'none';
        }

        function onProductSelect() {
            const select = document.getElementById('coyProductSelect');
            const selectedOption = select.options[select.selectedIndex];
            if (selectedOption.value) {
                document.getElementById('previewTitle').innerText = selectedOption.getAttribute('data-name');
            }
        }

        function handleImageUpload(input, targetId) {
            const file = input.files[0];
            const target = document.getElementById(targetId);
            if (file) {
                target.src = URL.createObjectURL(file);
                target.style.display = 'block';
            } else {
                target.style.display = 'none';
            }
        }

        async function submitCoy() {
            const productId = document.getElementById('coyProductSelect').value;
            const title = document.getElementById('previewTitle').innerText.trim();
            const desc = document.getElementById('previewDesc').innerText.trim();
            const topFile = document.getElementById('coyTopImage').files[0];
            const bottomFile = document.getElementById('coyBottomImage').files[0];

            if (!productId || !title || !desc || !topFile || !bottomFile) {
                alert('Please select a product, add a title/description, and upload both images.');
                return;
            }

            document.getElementById('formLoading').style.display = 'flex';
            
            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('title', title);
            formData.append('description', desc);
            formData.append('top_image', topFile);
            formData.append('bottom_image', bottomFile);
            
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

html = re.sub(r'<!-- ── MODAL ── -->.*</body>', new_modal_and_js, html, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
