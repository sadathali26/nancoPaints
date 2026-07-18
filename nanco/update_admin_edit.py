import re

file_path = r"d:\Users\user\Desktop\working files\nanco_main\nanco\admin_products_of_the_year.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

# I need to update the <script> block to handle the new functionality.
script_pattern = re.compile(r'<script>.*?</script>', re.DOTALL)
old_script = script_pattern.search(html).group(0)

new_script = """<script>
        const API_BASE_URL = 'http://127.0.0.1:5000';
        let productsData = [];
        let coyItemsData = [];
        let editingCoyId = null;

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
                coyItemsData = data;
                const grid = document.getElementById('adminCoyGrid');
                grid.innerHTML = '';
                data.forEach(item => {
                    grid.innerHTML += `
                        <div class="coy-item" style="position:relative; height:420px; border-radius:24px; overflow:hidden;">
                            <div class="admin-item-actions" style="position:absolute; top:12px; right:12px; z-index:20; display:flex; gap:8px;">
                                <button class="admin-action-btn edit" onclick="editCoy('${item.id}')" title="Edit"><i class="fas fa-edit"></i></button>
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
            editingCoyId = null;
            document.getElementById('coyModal').style.display = 'flex';
            document.getElementById('coyProductSelect').value = '';
            document.getElementById('previewTitle').innerText = 'Title';
            document.getElementById('previewDesc').innerText = 'Edit this description directly...';
            document.getElementById('previewTopImg').style.display = 'none';
            document.getElementById('previewBottomImg').style.display = 'none';
            document.getElementById('coyTopImage').value = '';
            document.getElementById('coyBottomImage').value = '';
        }

        function editCoy(id) {
            const item = coyItemsData.find(i => i.id === id);
            if (!item) return;

            editingCoyId = id;
            document.getElementById('coyModal').style.display = 'flex';
            document.getElementById('coyProductSelect').value = item.product_id;
            document.getElementById('previewTitle').innerText = item.title;
            document.getElementById('previewDesc').innerText = item.description;

            const topImg = document.getElementById('previewTopImg');
            topImg.src = item.top_image_url;
            topImg.style.display = 'block';

            const bottomImg = document.getElementById('previewBottomImg');
            bottomImg.src = item.bottom_image_url;
            bottomImg.style.display = 'block';

            document.getElementById('coyTopImage').value = '';
            document.getElementById('coyBottomImage').value = '';
        }

        function closeModal() {
            document.getElementById('coyModal').style.display = 'none';
            editingCoyId = null;
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
                // If they cancel out of file picker, we don't want to hide if we're editing
                if (!editingCoyId) target.style.display = 'none';
            }
        }

        async function submitCoy() {
            const productId = document.getElementById('coyProductSelect').value;
            const title = document.getElementById('previewTitle').innerText.trim();
            const desc = document.getElementById('previewDesc').innerText.trim();
            const topFile = document.getElementById('coyTopImage').files[0];
            const bottomFile = document.getElementById('coyBottomImage').files[0];

            if (!productId || !title || !desc) {
                alert('Please select a product, add a title and description.');
                return;
            }

            if (!editingCoyId && (!topFile || !bottomFile)) {
                alert('Please upload both top and bottom images for a new product.');
                return;
            }

            document.getElementById('formLoading').style.display = 'flex';
            
            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('title', title);
            formData.append('description', desc);
            if (topFile) formData.append('top_image', topFile);
            if (bottomFile) formData.append('bottom_image', bottomFile);
            
            try {
                const token = localStorage.getItem('adminToken') || 'super-secret-nanco-token';
                
                const url = editingCoyId 
                    ? `${API_BASE_URL}/api/coy-items/${editingCoyId}` 
                    : `${API_BASE_URL}/api/coy-items`;
                
                const method = editingCoyId ? 'PUT' : 'POST';

                const res = await fetch(url, {
                    method: method,
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
            if (!confirm('Are you sure you want to delete this featured product? This will permanently delete its images.')) return;
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
    </script>"""

html = html.replace(old_script, new_script)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
