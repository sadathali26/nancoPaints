
        // --- ORDER MODE STATE ---
        let isOrderMode = false;
        let reqEmulsion = 0;
        let reqPrimer = 0;
        let addedEmulsion = 0;
        let addedPrimer = 0;

        // --- 1. PRODUCT DATA FETCHING ---
        let products = [];

        function checkOrderMode() {
            const urlParams = new URLSearchParams(window.location.search);
            if(urlParams.get('orderMode') === 'true') {
                isOrderMode = true;
                reqEmulsion = parseFloat(urlParams.get('reqEmulsion')) || 0;
                reqPrimer = parseFloat(urlParams.get('reqPrimer')) || 0;
                renderOrderTracker();
                
                // Auto-filter: if they need both, we don't strict filter, but we could set search to "emulsion" or "primer".
                // Since they might need both, we will just let them browse but with the tracker clearly visible.
            }
        }

        function renderOrderTracker() {
            let tracker = document.getElementById('order-mode-tracker');
            if(!tracker) {
                tracker = document.createElement('div');
                tracker.id = 'order-mode-tracker';
                tracker.style.position = 'fixed';
                tracker.style.bottom = '24px';
                tracker.style.right = '24px';
                tracker.style.background = 'var(--color-ink-black)';
                tracker.style.color = 'var(--color-white-plate)';
                tracker.style.padding = '16px 24px';
                tracker.style.borderRadius = '16px';
                tracker.style.zIndex = '1000';
                tracker.style.boxShadow = '0 10px 30px rgba(0,0,0,0.2)';
                tracker.style.display = 'flex';
                tracker.style.flexDirection = 'column';
                tracker.style.gap = '12px';
                tracker.style.width = '300px';
                document.body.appendChild(tracker);
            }

            let html = `<div style="font-weight:800; font-size:14px; display:flex; justify-content:space-between; align-items:center;">
                            <span><i class="fas fa-clipboard-check" style="color:var(--color-mustard-pop); margin-right:8px;"></i> Order Requirement</span>
                            <button onclick="document.getElementById('order-mode-tracker').remove(); isOrderMode=false;" style="background:none; border:none; color:rgba(255,255,255,0.5); cursor:pointer;"><i class="fas fa-times"></i></button>
                        </div>`;

            if(reqEmulsion > 0) {
                const emulColor = addedEmulsion >= reqEmulsion ? 'var(--color-lime-spark, #d2e823)' : 'var(--color-sage-mute)';
                html += `<div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600;">
                            <span>Emulsion</span>
                            <span style="color:${emulColor};">${addedEmulsion} / ${reqEmulsion} L</span>
                         </div>`;
            }
            if(reqPrimer > 0) {
                const primColor = addedPrimer >= reqPrimer ? 'var(--color-lime-spark, #d2e823)' : 'var(--color-sage-mute)';
                html += `<div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600;">
                            <span>Primer</span>
                            <span style="color:${primColor};">${addedPrimer} / ${reqPrimer} L</span>
                         </div>`;
            }

            if((reqEmulsion === 0 || addedEmulsion >= reqEmulsion) && (reqPrimer === 0 || addedPrimer >= reqPrimer)) {
                html += `<div style="margin-top:8px; padding:8px; background:rgba(210,232,35,0.1); color:var(--color-lime-spark, #d2e823); border-radius:8px; font-size:12px; font-weight:700; text-align:center;">
                            Requirements Met! <br> You can proceed to checkout.
                         </div>`;
            }

            tracker.innerHTML = html;
        }

        function changeCarousel(btn, dir) {
            const container = btn.closest('.prod-carousel');
            const images = JSON.parse(container.getAttribute('data-images'));
            let idx = parseInt(container.getAttribute('data-idx'));
            idx = (idx + dir + images.length) % images.length;
            container.setAttribute('data-idx', idx);
            container.querySelector('.carousel-img').src = images[idx];
            const dots = container.querySelectorAll('.carousel-dots div');
            dots.forEach((dot, i) => {
                dot.style.background = (i === idx) ? 'var(--color-cobalt-band)' : 'rgba(255,255,255,0.8)';
            });
        }

        function generateProductVisualHTML(product) {
            if (product.images && product.images.length > 0) {
                if (product.images.length === 1) {
                    return `<img src="${product.images[0]}" alt="${product.name}" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; border-radius:inherit;">`;
                } else {
                    return `
                        <div style="position:absolute; inset:0; border-radius:inherit; overflow:hidden;" class="prod-carousel" data-images='${JSON.stringify(product.images)}' data-idx="0">
                            <img src="${product.images[0]}" style="width:100%; height:100%; object-fit:cover; transition: opacity 0.3s;" class="carousel-img">
                            <button class="carousel-btn prev-btn" onclick="event.stopPropagation(); changeCarousel(this, -1)" style="position:absolute; left:12px; top:50%; transform:translateY(-50%); background:none; border:none; cursor:pointer; padding:0; display:flex; align-items:center; justify-content:center; z-index:10;"><i class="fas fa-chevron-left"></i></button>
                            <button class="carousel-btn next-btn" onclick="event.stopPropagation(); changeCarousel(this, 1)" style="position:absolute; right:12px; top:50%; transform:translateY(-50%); background:none; border:none; cursor:pointer; padding:0; display:flex; align-items:center; justify-content:center; z-index:10;"><i class="fas fa-chevron-right"></i></button>
                            <div style="position:absolute; bottom:10px; width:100%; display:flex; justify-content:center; gap:6px; z-index:10;" class="carousel-dots">
                                ${product.images.map((_, i) => `<div style="width:8px; height:8px; border-radius:50%; background:${i===0?'var(--color-cobalt-band)':'rgba(255,255,255,0.8)'}; box-shadow:0 1px 2px rgba(0,0,0,0.2);"></div>`).join('')}
                            </div>
                        </div>
                    `;
                }
            }
            return generateBucketHTML(product);
        }

        async function fetchProducts() {
            try {
                const url = 'https://sawbglsfqyayuysqcjto.supabase.co/rest/v1/items?select=*';
                const anonKey = 'sb_publishable_dT1pmAyJdFf1pbGn_yw7_g_E2UFN5l2';
                const response = await fetch(url, {
                    headers: {
                        'apikey': anonKey,
                        'Authorization': `Bearer ${anonKey}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!response.ok) throw new Error('Failed to fetch from Supabase');
                const data = await response.json();
                
                const colors = ['#1e3a8a', '#ea580c', '#475569', '#0d9488', '#be185d', '#b45309', '#65a30d', '#9f1239'];
                
                                const groupedMap = {};
                data.forEach((p, index) => {
                    let images = [];
                    if (Array.isArray(p.images) && p.images.length > 0) {
                        images = p.images;
                    } else if (p.image_url) {
                        images.push(p.image_url);
                    }
                    
                    let id = p.id || String(index + 1);
                    if (images.length === 0 && (typeof id === 'number' || !isNaN(Number(id))) && Number(id) <= 21) {
                        const type1Ext = [null, 'jpeg', 'jpeg', 'jpeg', 'jpeg', 'jpeg', 'jpeg', 'jpg', 'jpg', 'jpg', 'jpg', 'jpg', 'jpg', 'jpeg', 'jpeg', 'jpeg', 'jpeg', 'jpeg', 'jpeg', 'jpeg', 'jpeg', 'jpeg'];
                        const numId = Number(id);
                        if (type1Ext[numId]) {
                            images.push(`product_imgs/product_img_type_1/${numId}.${type1Ext[numId]}`);
                            images.push(`product_imgs/product_img_type_2/${numId}.jpg`);
                        }
                    }

                    const parseField = (field, fallback) => {
                        if (!field) return fallback;
                        if (typeof field === 'string') {
                            try { return JSON.parse(field); } catch(e) { return fallback; }
                        }
                        return field;
                    };

                    let pricing = parseField(p.pricing_table || p.pricing, null);
                    if (!pricing && (p.mrp || p.offer || p.unit || p.unit_number)) {
                        pricing = [{
                            unit: (p.unit_number || '') + ' ' + (p.unit || ''),
                            mrp: p.mrp || 0,
                            retail_price: p.r_price || 0,
                            offer_price: p.offer || 0,
                            save_amount: p.benafit || 0,
                            item_code: String(p.company_item_code || p.item_code || p.id || 'N/A')
                        }];
                        pricing[0].unit = pricing[0].unit.trim() || '1 Ltr';
                    } else if (!pricing) {
                        pricing = [];
                    }
                    if (!Array.isArray(pricing)) pricing = [pricing];

                    let specsRaw = p.features || p.specifications_and_usage || p.specs;
                    let specs = [];
                    if (Array.isArray(specsRaw)) {
                        specs = specsRaw;
                    } else if (typeof specsRaw === 'string') {
                        try {
                            const parsed = JSON.parse(specsRaw);
                            specs = Array.isArray(parsed) ? parsed : [parsed];
                        } catch(e) {
                            specs = specsRaw.split(',').map(s => s.trim()).filter(s => s);
                        }
                    }
                    
                    // Filter out UUIDs from features (since they are now relation IDs)
                    specs = specs.filter(s => typeof s === 'string' && !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(s));
                    if (p.item_group && !specs.includes(p.item_group)) specs.push(p.item_group);
                    if (p.chemistry && !specs.includes(p.chemistry)) specs.push(p.chemistry);
                    if (p.color_shade && !specs.includes(p.color_shade)) specs.push(p.color_shade);

                    const notes = parseField(p.order_notes || p.notes, []);

                    const name = String(p.item_name || p.product_name || p.name || 'Unknown Product');
                    const category = String(p.category || p.sub_category || p.store_type || 'Interior').toLowerCase();
                    const groupKey = name.toLowerCase().trim() + '|' + category;

                    if (!groupedMap[groupKey]) {
                        groupedMap[groupKey] = {
                            id: id,
                            name: name,
                            brand: String(p.brand || 'Nanco'),
                            category: category,
                            finish: String(p.finish || ''),
                            desc: String(p.description || p.desc || p.product_unit || ''),
                            color: colors[index % colors.length],
                            label: String(p.product_line || p.product_range || p.product_range_similar_to || p.brand || 'Nanco'),
                            coverage: String(p.coverage_per_liter || p.coverage || ''),
                            similar: String(p.product_range_similar_to || p.similar || ''),
                            pricing: pricing,
                            specs: specs,
                            notes: Array.isArray(notes) ? notes : [],
                            images: images
                        };
                    } else {
                        if (pricing.length > 0) {
                            groupedMap[groupKey].pricing = groupedMap[groupKey].pricing.concat(pricing);
                        }
                        if (images.length > 0 && groupedMap[groupKey].images.length === 0) {
                            groupedMap[groupKey].images = images;
                        }
                    }
                });

                products = Object.values(groupedMap).map(p => {
                    if (p.pricing && p.pricing.length > 0) {
                        p.pricing.sort((a, b) => (Number(a.offer_price) || 0) - (Number(b.offer_price) || 0));
                        p.priceVal = Number(p.pricing[0].offer_price || 0);
                    } else {
                        p.priceVal = 0;
                    }
                    return p;
                });
                renderProducts();
            } catch (err) {
                console.error("Error loading products:", err);
                document.getElementById('product-grid').innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px;color:red;">Failed to load products.</div>';
            }
        }

        function generateBucketHTML(product) {
            return `
                <div class="bucket-container">
                    <div class="bucket-handle"></div>
                    <div class="bucket-lid"></div>
                    <div class="bucket-body">
                        <div class="bucket-label" style="background-color: ${product.color};">
                            <span style="font-size:9px; font-weight:800; text-transform:uppercase; opacity:0.8; letter-spacing:0.1em;">${product.brand}</span>
                            <span style="font-size:14px; font-weight:800; line-height:1.1; margin-top:2px; display:block; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${product.name}">${product.name}</span>
                            <div style="margin-top:6px; display:flex; gap:4px; flex-wrap:wrap;">
                                <span style="font-size:8px; background:#fff; color:var(--color-ink-black); padding:2px 6px; border-radius:4px; font-weight:800; text-transform:uppercase; box-shadow:0 2px 4px rgba(0,0,0,0.1); display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical; overflow:hidden;">${product.label}</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        // --- 3. RENDERING & FILTERING LOGIC ---
        let currentView = 'grid'; // 'grid' or 'list'

        function renderProducts() {
            const grid = document.getElementById('product-grid');
            const searchQ = document.getElementById('search-input').value.toLowerCase();

            const activeCategories = Array.from(document.querySelectorAll('.filter-pill.filter-category.active')).map(btn => btn.getAttribute('data-value'));
            const activeFinishes = Array.from(document.querySelectorAll('.filter-pill.filter-finish.active')).map(btn => btn.getAttribute('data-value'));
            const activePrices = Array.from(document.querySelectorAll('.filter-pill.filter-price.active')).map(btn => btn.getAttribute('data-value'));

            const filtered = products.filter(p => {
                const matchesSearch = p.name.toLowerCase().includes(searchQ) || p.specs.join(' ').toLowerCase().includes(searchQ) || p.desc.toLowerCase().includes(searchQ);
                
                const matchesCategory = activeCategories.length === 0 || activeCategories.some(cat => {
                    if (cat === 'interior') return p.category.includes('interior') || p.name.toLowerCase().includes('interior');
                    if (cat === 'exterior') return p.category.includes('exterior') || p.name.toLowerCase().includes('exterior');
                    if (cat === 'waterproofing') return p.category.includes('waterproof') || p.name.toLowerCase().includes('waterproof') || p.desc.toLowerCase().includes('waterproof');
                    if (cat === 'wood & metal') return p.category.includes('wood') || p.category.includes('metal') || p.name.toLowerCase().includes('wood') || p.name.toLowerCase().includes('metal');
                    return false;
                });

                const matchesFinish = activeFinishes.length === 0 || activeFinishes.some(fin => {
                    return p.finish.toLowerCase().includes(fin);
                });

                const matchesPrice = activePrices.length === 0 || activePrices.some(pr => {
                    if (pr === 'standard') return p.priceVal > 0 && p.priceVal <= 300;
                    if (pr === 'premium') return p.priceVal > 300 && p.priceVal <= 500;
                    if (pr === 'luxury') return p.priceVal > 500;
                    return false;
                });

                return matchesSearch && matchesCategory && matchesFinish && matchesPrice;
            });

            document.getElementById('product-count').innerText = `Showing ${filtered.length} product${filtered.length !== 1 ? 's' : ''}`;

            if (currentView === 'grid') {
                grid.className = 'bento-grid';
                grid.classList.remove('list-mode');
                grid.style.gridTemplateColumns = '';
            } else {
                grid.className = 'bento-grid';
                grid.classList.add('list-mode');
                grid.style.gridTemplateColumns = '1fr';
            }

            grid.innerHTML = filtered.map(p => {
                const featuresHtml = p.specs.slice(0, 2).map(f => `<span class="feature-badge" style="display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical; overflow:hidden;"><i class="fas fa-check" style="color:var(--color-cobalt-band); margin-right:4px;"></i>${f}</span>`).join('');

                if (currentView === 'grid') {
                    const visualHtml = generateProductVisualHTML(p);
                    const bgStyle = (p.images && p.images.length > 0) ? "" : `background: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)), url('assets/pattern.jpg'); background-color: ${p.color}; background-blend-mode: multiply; background-size: cover; background-position: center;`;
                    return `
                        <div class="bento-card product-card" onclick="openPDP('${p.id}')" style="padding:0; display:flex; flex-direction:column; overflow:hidden;">
                            <div class="bucket-wrapper" style="aspect-ratio:1/1; width:100%; position:relative; overflow:hidden; ${bgStyle} flex-shrink:0;">
                                ${visualHtml}
                            </div>
                            <div class="product-info" style="padding:14px 16px 16px; display:flex; flex-direction:column; flex:1;">
                                <h3 style="font-size:15px; font-weight:800; color:var(--color-ink-black); margin-bottom:8px; line-height:1.2;">${p.name}</h3>
                                <div style="margin-top:auto; display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(0,0,0,0.06); padding-top:12px;">
                                    <div>
                                        <span style="font-size:10px; color:var(--color-sage-mute); text-transform:uppercase; font-weight:800; display:block; margin-bottom:2px;">${p.finish}</span>
                                        <span style="font-size:16px; font-weight:800; color:var(--color-ink-black);">₹${p.priceVal}<span style="font-size:11px; font-weight:400; color:var(--color-sage-mute);"> / Starting</span></span>
                                    </div>
                                    <div style="width:30px; height:30px; border-radius:50%; background:var(--color-linen-canvas); display:flex; align-items:center; justify-content:center; color:var(--color-ink-black); flex-shrink:0;"><i class="fas fa-arrow-right" style="transform:rotate(-45deg); font-size:12px;"></i></div>
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    const visualHtml = generateProductVisualHTML(p);
                    const bgStyle = (p.images && p.images.length > 0) ? "" : `background: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)), url('assets/pattern.jpg'); background-color: ${p.color}; background-blend-mode: multiply; background-size: cover; background-position: center;`;
                    return `
                        <div class="bento-card product-card list-view" onclick="openPDP('${p.id}')">
                            <div class="bucket-wrapper" style="display:flex; align-items:center; justify-content:center; ${bgStyle}">
                                ${visualHtml}
                            </div>
                            <div style="flex:1; min-width:0;">
                                <h3 style="font-size: 20px; font-weight: 800; color: var(--color-ink-black); margin-bottom: 6px;">${p.name}</h3>
                                <p style="font-size: 13px; color: var(--color-sage-mute); margin-bottom: 12px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">${p.desc}</p>
                                <div style="display: flex; gap: 6px; flex-wrap: wrap;">${featuresHtml}</div>
                            </div>
                            <div style="text-align:right; border-left: 1px solid rgba(0,0,0,0.05); padding-left: 24px;">
                                <span style="font-size: 24px; font-weight:800; color:var(--color-ink-black); display:block;">₹${p.priceVal}</span>
                                <span style="font-size:10px; color:var(--color-sage-mute); text-transform:uppercase; font-weight:800;">Starting</span>
                            </div>
                        </div>
                    `;
                }
            }).join('') || '<div style="grid-column: 1 / -1; padding: 60px 20px; text-align: center; color: var(--color-sage-mute);"><i class="fas fa-box-open" style="font-size: 48px; opacity: 0.2; margin-bottom: 16px;"></i><p style="font-weight:700;">No products match your search.</p></div>';
        }

        function setGridMode(mode) {
            currentView = mode;
            const grid = document.getElementById('product-grid');
            if (mode === 'list') {
                grid.classList.add('list-mode');
            } else {
                grid.classList.remove('list-mode');
            }
            renderProducts();
        }

        let _viewMode = 'grid';
        function toggleViewMode() {
            _viewMode = (_viewMode === 'grid') ? 'list' : 'grid';
            document.getElementById('view-toggle-icon').className = (_viewMode === 'grid') ? 'fas fa-list' : 'fas fa-th-large';
            setGridMode(_viewMode);
        }

        function openFilterDrawer() {
            const overlay = document.getElementById('filter-drawer-overlay');
            const drawer  = document.getElementById('filter-drawer');
            overlay.style.display = 'block';
            requestAnimationFrame(() => { overlay.style.opacity = '1'; drawer.classList.add('open'); });
            document.getElementById('filter-toggle-btn').classList.add('active');
        }

        function closeFilterDrawer() {
            const overlay = document.getElementById('filter-drawer-overlay');
            const drawer  = document.getElementById('filter-drawer');
            overlay.style.opacity = '0';
            drawer.classList.remove('open');
            setTimeout(() => { overlay.style.display = 'none'; }, 350);
            document.getElementById('filter-toggle-btn').classList.remove('active');
        }

        function updateFilterBadge() {
            const count = document.querySelectorAll('.filter-pill.active').length;
            const badge = document.getElementById('ftb-count');
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-flex' : 'none';
        }

        // Listeners
        document.getElementById('search-input').addEventListener('input', renderProducts);
        
        // Event delegation for filter pills (sidebar + drawer)
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('filter-pill')) {
                e.target.classList.toggle('active');
                // Sync matching pill in the other panel
                const val = e.target.dataset.value;
                const cls = [...e.target.classList].find(c => c.startsWith('filter-') && c !== 'filter-pill');
                document.querySelectorAll('.' + cls).forEach(btn => {
                    if (btn !== e.target && btn.dataset.value === val) {
                        btn.classList.toggle('active', e.target.classList.contains('active'));
                    }
                });
                updateFilterBadge();
                renderProducts();
            }
        });

        function clearFilters() {
            document.querySelectorAll('.filter-pill').forEach(btn => btn.classList.remove('active'));
            document.getElementById('search-input').value = '';
            updateFilterBadge();
            renderProducts();
        }

        // --- 4. MODALS ---
        let currentPdpProduct = null;

        function openPDP(id) {
            currentPdpProduct = products.find(p => p.id === id);
            if (!currentPdpProduct) return;

            const pdpBucketContainer = document.getElementById('pdp-bucket-container');
            pdpBucketContainer.innerHTML = generateProductVisualHTML(currentPdpProduct);
            if (currentPdpProduct.images && currentPdpProduct.images.length > 0) {
                pdpBucketContainer.style.transform = 'scale(1)';
                pdpBucketContainer.style.width = '100%';
                pdpBucketContainer.style.height = '320px';
            } else {
                pdpBucketContainer.style.transform = 'scale(1.6)';
                pdpBucketContainer.style.width = '';
                pdpBucketContainer.style.height = '';
            }

            document.getElementById('pdp-name').innerText = currentPdpProduct.name;
            document.getElementById('pdp-brand').innerText = currentPdpProduct.brand;
            document.getElementById('pdp-desc').innerText = currentPdpProduct.desc;
            document.getElementById('pdp-finish').innerText = currentPdpProduct.finish;
            document.getElementById('pdp-coverage').innerText = currentPdpProduct.coverage;
            document.getElementById('pdp-similar').innerText = currentPdpProduct.similar || 'N/A';

            document.getElementById('pdp-specs').innerHTML = currentPdpProduct.specs.map(s => `<li style="margin-bottom:4px;"><i class="fas fa-angle-right" style="font-size:10px; margin-right:6px; color:var(--color-cobalt-band);"></i>${s}</li>`).join('');
            document.getElementById('pdp-notes').innerHTML = currentPdpProduct.notes.map(n => `<li style="margin-bottom:4px;"><i class="fas fa-exclamation-circle" style="font-size:10px; margin-right:6px;"></i>${n}</li>`).join('');

            // Reset more details toggle
            document.getElementById('pdp-more-details').style.display = 'none';
            const icon = document.getElementById('icon-pdp-details');
            if (icon) {
                icon.className = 'fas fa-chevron-down';
            }

            const unitSelect = document.getElementById('pdp-unit-select');
            unitSelect.innerHTML = currentPdpProduct.pricing.map((tier, idx) => `<option value="${idx}">${tier.unit}</option>`).join('');
            
            updatePdpPrice();

            document.getElementById('pdp-badges').innerHTML = `<span class="feature-badge">${currentPdpProduct.category}</span>`;
            document.getElementById('pdp-quantity').value = 1;

            const modal = document.getElementById('pdp-modal');
            const content = document.getElementById('pdp-content');
            modal.style.display = 'flex';
            setTimeout(() => {
                modal.style.opacity = '1';
                content.style.transform = 'scale(1)';
            }, 10);
        }

        function updatePdpPrice() {
            if (!currentPdpProduct || !currentPdpProduct.pricing.length) return;
            const idx = document.getElementById('pdp-unit-select').value;
            const tier = currentPdpProduct.pricing[idx];
            document.getElementById('pdp-price-val').innerText = `₹${tier.offer_price}`;
            document.getElementById('pdp-mrp').innerText = `MRP: ₹${tier.mrp}`;
            document.getElementById('pdp-save').innerText = `Save ₹${tier.save_amount}`;
            document.getElementById('pdp-code').innerText = `Item Code: ${tier.item_code}`;
        }

        function togglePdpDetails() {
            const detailsDiv = document.getElementById('pdp-more-details');
            const icon = document.getElementById('icon-pdp-details');
            if (detailsDiv.style.display === 'none') {
                detailsDiv.style.display = 'flex';
                icon.className = 'fas fa-chevron-up';
            } else {
                detailsDiv.style.display = 'none';
                icon.className = 'fas fa-chevron-down';
            }
        }

        function calculateCoverage() {
            const sqft = parseFloat(document.getElementById('est-sqft').value);
            if (!sqft || sqft <= 0) return;
            const liters = (sqft / 80).toFixed(1);
            document.getElementById('est-result').innerText = `${liters} L`;
        }

        function openLeadModal() {
            const modal = document.getElementById('lead-modal');
            const content = document.getElementById('lead-content');
            modal.style.display = 'flex';
            setTimeout(() => {
                modal.style.opacity = '1';
                content.style.transform = 'scale(1)';
            }, 10);
        }

        function closeModal(id) {
            const modal = document.getElementById(id);
            const content = modal.querySelector('.modal-content');
            modal.style.opacity = '0';
            content.style.transform = 'scale(0.95)';
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }

        document.getElementById('lead-form').addEventListener('submit', function (e) {
            e.preventDefault();
            this.innerHTML = `
                <div style="text-align: center; padding: 40px 0;">
                    <div style="width: 64px; height: 64px; background: #dcfce7; color: #16a34a; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; font-size: 32px;">
                        <i class="fas fa-check"></i>
                    </div>
                    <h3 style="font-size: 20px; font-weight: 800; color: var(--color-ink-black); margin-bottom: 8px;">Unlocked!</h3>
                    <p style="font-size: 14px; color: var(--color-sage-mute);">Your download has started. Our expert will text you soon.</p>
                </div>`;
            setTimeout(() => closeModal('lead-modal'), 3000);
        });

        function downloadDatasheetFile(product) {
            const specList = (product.specs && product.specs.length > 0) 
                ? product.specs.map(s => `<li>${s}</li>`).join('') 
                : '<li>N/A</li>';

            const noteList = (product.notes && product.notes.length > 0) 
                ? product.notes.map(n => `<li>${n}</li>`).join('') 
                : '<li>None</li>';

            const priceRows = (product.pricing && product.pricing.length > 0) 
                ? product.pricing.map(t => `<tr><td>${t.unit}</td><td>₹${t.mrp}</td><td>₹${t.offer_price}</td><td>${t.item_code}</td></tr>`).join('') 
                : '<tr><td colspan="4">Contact for pricing</td></tr>';

            const htmlContent = `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>${product.name} - Technical Datasheet</title>
                <style>
                    body { font-family: 'Inter', system-ui, -apple-system, sans-serif; color: #1e293b; line-height: 1.6; padding: 40px; max-width: 800px; margin: 0 auto; background: #fff; }
                    .header { border-bottom: 4px solid #16a34a; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: flex-end; }
                    .logo { font-size: 32px; font-weight: 900; color: #1e3a8a; letter-spacing: -1px; margin: 0; }
                    .doc-title { font-size: 14px; text-transform: uppercase; letter-spacing: 2px; color: #64748b; margin: 0; font-weight: 800; }
                    .product-title { font-size: 36px; font-weight: 800; margin: 0 0 16px 0; color: #0f172a; line-height: 1.2; }
                    .badge-container { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 30px; }
                    .badge { background: #f1f5f9; padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; color: #475569; border: 1px solid #e2e8f0; }
                    .section-title { font-size: 18px; font-weight: 800; color: #1e3a8a; margin-top: 30px; margin-bottom: 16px; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
                    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
                    .desc { font-size: 15px; color: #334155; }
                    ul { padding-left: 20px; margin: 0; color: #334155; }
                    li { margin-bottom: 8px; font-size: 14px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                    th, td { border: 1px solid #e2e8f0; padding: 12px 16px; text-align: left; font-size: 14px; }
                    th { background: #f8fafc; font-weight: 700; color: #0f172a; }
                    td { color: #334155; }
                    .footer { margin-top: 60px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; text-align: center; }
                    .print-btn { background: #1e3a8a; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; font-family: inherit; font-size: 14px; transition: background 0.2s; }
                    .print-btn:hover { background: #172554; }
                    @media print {
                        body { padding: 0; max-width: 100%; }
                        .no-print { display: none !important; }
                    }
                </style>
            </head>
            <body>
                <div class="no-print" style="text-align: right; margin-bottom: 20px;">
                    <button class="print-btn" onclick="window.print()">
                        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M6 9V2h12v7M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2M6 14h12v8H6z"></path></svg>
                        Print / Save as PDF
                    </button>
                </div>
                <div class="header">
                    <h1 class="logo">NANCO</h1>
                    <h2 class="doc-title">Technical Datasheet</h2>
                </div>
                
                <h1 class="product-title">${product.name}</h1>
                <div class="badge-container">
                    <span class="badge">Brand: ${product.brand}</span>
                    <span class="badge">Category: ${product.category}</span>
                    <span class="badge">Finish: ${product.finish}</span>
                    <span class="badge">Coverage: ${product.coverage || 'N/A'}</span>
                </div>
                
                <div class="section-title">Description</div>
                <p class="desc">${product.desc || 'No description available.'}</p>
                
                <div class="grid">
                    <div>
                        <div class="section-title">Specifications</div>
                        <ul>${specList}</ul>
                    </div>
                    <div>
                        <div class="section-title">Usage Notes</div>
                        <ul style="color: #b91c1c;">${noteList}</ul>
                    </div>
                </div>
                
                <div class="section-title">Pricing & Variants</div>
                <table>
                    <thead>
                        <tr>
                            <th>Unit Size</th>
                            <th>MRP</th>
                            <th>Offer Price</th>
                            <th>Item Code</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${priceRows}
                    </tbody>
                </table>
                
                <div class="footer">
                    &copy; ${new Date().getFullYear()} Nanco Paints. All rights reserved. This document is automatically generated.
                </div>
            </body>
            </html>
            `;

            const win = window.open('', '_blank');
            if (win) {
                win.document.write(htmlContent);
                win.document.close();
            } else {
                alert('Please allow popups to view the datasheet.');
            }
        }

        function openDatasheetModal() {
            const modal = document.getElementById('datasheet-modal');
            const content = document.getElementById('datasheet-content');
            modal.style.display = 'flex';
            setTimeout(() => {
                modal.style.opacity = '1';
                content.style.transform = 'scale(1)';
            }, 10);
        }

        document.getElementById('datasheet-form').addEventListener('submit', function (e) {
            e.preventDefault();
            this.innerHTML = `
                <div style="text-align: center; padding: 40px 0;">
                    <div style="width: 64px; height: 64px; background: #dcfce7; color: #16a34a; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; font-size: 32px;">
                        <i class="fas fa-check"></i>
                    </div>
                    <h3 style="font-size: 20px; font-weight: 800; color: var(--color-ink-black); margin-bottom: 8px;">Unlocked!</h3>
                    <p style="font-size: 14px; color: var(--color-sage-mute);">Your download has started.</p>
                </div>`;
            
            if (currentPdpProduct) {
                downloadDatasheetFile(currentPdpProduct);
            }

            const detailsDiv = document.getElementById('pdp-more-details');
            const icon = document.getElementById('icon-pdp-details');
            if (detailsDiv) {
                detailsDiv.style.display = 'flex';
            }
            if (icon) {
                icon.className = 'fas fa-chevron-up';
            }

            setTimeout(() => closeModal('datasheet-modal'), 2500);
        });

        // --- 5. CART & INVOICE LOGIC ---
        let cart = [];

        function updateCartBadge() {
            const badge = document.getElementById('cart-badge');
            const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
            if (totalItems > 0) {
                badge.innerText = totalItems;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        }

        function addToCart(openCart = false) {
            if (!currentPdpProduct) return;
            const unitSelect = document.getElementById('pdp-unit-select');
            const unitIdx = unitSelect.value;
            const tier = currentPdpProduct.pricing[unitIdx];
            if (!tier) return;
            const unitName = tier.unit;
            const priceVal = tier.offer_price;
            const quantity = parseInt(document.getElementById('pdp-quantity').value) || 1;
            
            const existingItem = cart.find(i => i.id === currentPdpProduct.id && i.unitName === unitName);
            if (existingItem) {
                existingItem.quantity += quantity;
            } else {
                cart.push({
                    id: currentPdpProduct.id,
                    name: currentPdpProduct.name,
                    color: currentPdpProduct.color,
                    label: currentPdpProduct.label,
                    priceVal: priceVal,
                    unitName: unitName,
                    quantity: quantity
                });
            }
            updateCartBadge();

            if (isOrderMode) {
                // Determine if it's emulsion or primer
                const pName = currentPdpProduct.name.toLowerCase();
                // extract liter amount from unitName, e.g. "20 LTR", "4 LTR", "1 LTR", "500 ML"
                const match = unitName.match(/(\d+(\.\d+)?)\s*(L|ML)/i);
                let ltrsPerUnit = 0;
                if(match) {
                    ltrsPerUnit = parseFloat(match[1]);
                    if(match[3].toUpperCase() === 'ML') ltrsPerUnit /= 1000;
                }
                const totalLitersAdded = ltrsPerUnit * quantity;

                if(pName.includes('emulsion') || pName.includes('topaz') || pName.includes('emerald') || pName.includes('platinum')) {
                    addedEmulsion += totalLitersAdded;
                } else if(pName.includes('primer')) {
                    addedPrimer += totalLitersAdded;
                }
                renderOrderTracker();
            }
            
            if (openCart) {
                closeModal('pdp-modal');
                openCartModal(); // Show cart after adding
            } else {
                // Show feedback on the Add to Cart button without closing modal
                const btn = document.querySelector('button[onclick="addToCart(false)"]');
                if(btn) {
                    const originalText = btn.innerHTML;
                    btn.innerHTML = '<i class="fas fa-check" style="margin-right: 8px;"></i> Added to Cart';
                    btn.style.background = 'var(--color-lime-spark, #d2e823)';
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.style.background = 'var(--color-white-plate)';
                    }, 1500);
                }
            }
        }

        function openCartModal() {
            const itemsContainer = document.getElementById('cart-items');
            if (cart.length === 0) {
                itemsContainer.innerHTML = '<div style="text-align:center; color:var(--color-sage-mute); padding: 40px 0;"><i class="fas fa-shopping-cart" style="font-size: 48px; opacity: 0.2; margin-bottom: 16px;"></i><p style="font-weight:700;">Your cart is empty.</p></div>';
                document.getElementById('cart-total').innerText = '₹0';
            } else {
                let total = 0;
                itemsContainer.innerHTML = cart.map((item, index) => {
                    const itemTotal = item.priceVal * item.quantity;
                    total += itemTotal;
                    return `
                        <div style="display:flex; align-items:center; gap:16px; margin-bottom:16px; padding-bottom:16px; border-bottom:1px solid rgba(0,0,0,0.05);">
                            <div style="width:60px; height:60px; background:${item.color}; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-size:24px; flex-shrink: 0;">
                                <i class="fas fa-fill-drip"></i>
                            </div>
                            <div style="flex:1;">
                                <h4 style="font-size:16px; font-weight:800; color:var(--color-ink-black); margin-bottom:4px;">${item.name}</h4>
                                <div style="font-size:12px; color:var(--color-sage-mute);">Unit: <strong>${item.unitName}</strong> | Qty: <strong>${item.quantity}</strong></div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:16px; font-weight:800; color:var(--color-ink-black);">₹${itemTotal}</div>
                                <button onclick="removeFromCart(${index})" style="background:none; border:none; color:var(--color-coral-red, #ef4444); font-size:12px; cursor:pointer; margin-top:4px; text-decoration:underline;">Remove</button>
                            </div>
                        </div>
                    `;
                }).join('');
                document.getElementById('cart-total').innerText = `₹${total}`;
            }
            
            const modal = document.getElementById('cart-modal');
            const content = modal.querySelector('.modal-content');
            modal.style.display = 'flex';
            setTimeout(() => {
                modal.style.opacity = '1';
                content.style.transform = 'scale(1)';
            }, 10);
        }

        function removeFromCart(index) {
            cart.splice(index, 1);
            updateCartBadge();
            openCartModal(); // Refresh cart modal
        }

        function checkout(method) {
            if (cart.length === 0) return;
            closeModal('cart-modal');
            
            // Generate Invoice Data
            const invoiceId = Math.floor(100000 + Math.random() * 900000);
            document.getElementById('invoice-id').innerText = invoiceId;
            
            const date = new Date();
            document.getElementById('invoice-date').innerText = `Date: ${date.toLocaleDateString()}`;
            
            const invoiceItemsContainer = document.getElementById('invoice-items');
            let total = 0;
            invoiceItemsContainer.innerHTML = cart.map(item => {
                const itemTotal = item.priceVal * item.quantity;
                total += itemTotal;
                return `
                    <tr>
                        <td style="padding: 12px 8px; font-size: 14px; font-weight: 700; color: var(--color-ink-black); display:flex; align-items:center; gap:8px;">
                            <div style="width:24px; height:24px; background:${item.color}; border-radius:4px; display:flex; align-items:center; justify-content:center; color:white; font-size:12px; flex-shrink: 0; border: 1px solid rgba(0,0,0,0.1);">
                                <i class="fas fa-fill-drip"></i>
                            </div>
                            ${item.name}
                        </td>
                        <td style="padding: 12px 8px; font-size: 14px; color: var(--color-sage-mute);">${item.unitName}</td>
                        <td style="text-align: right; padding: 12px 8px; font-size: 14px; color: var(--color-ink-black); font-weight: 700;">${item.quantity}</td>
                        <td style="text-align: right; padding: 12px 8px; font-size: 14px; color: var(--color-sage-mute);">₹${item.priceVal}</td>
                        <td style="text-align: right; padding: 12px 8px; font-size: 14px; font-weight: 800; color: var(--color-ink-black);">₹${itemTotal}</td>
                    </tr>
                `;
            }).join('');
            
            document.getElementById('invoice-total').innerText = `₹${total}`;
            
            setTimeout(() => {
                const modal = document.getElementById('invoice-modal');
                const content = modal.querySelector('.modal-content');
                modal.style.display = 'flex';
                setTimeout(() => {
                    modal.style.opacity = '1';
                    content.style.transform = 'scale(1)';
                }, 10);
            }, 300); // Wait for cart modal to close smoothly
            
            // Clear cart
            cart = [];
            updateCartBadge();
        }

        function downloadInvoice() {
            const invoiceElement = document.getElementById('invoice-content');
            
            // Use html2canvas to capture the invoice as an image
            if (typeof html2canvas !== 'undefined') {
                html2canvas(invoiceElement, { 
                    scale: 2, 
                    backgroundColor: '#ffffff'
                }).then(canvas => {
                    const link = document.createElement('a');
                    link.download = `Nanco_Invoice_${document.getElementById('invoice-id').innerText}.png`;
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }).catch(err => {
                    console.error("Error generating invoice image:", err);
                    alert("Could not generate image. Please try again.");
                });
            } else {
                alert("Image generation library not loaded. Please print the page instead.");
            }
        }

        // Initialize
        checkOrderMode();
        fetchProducts();
    