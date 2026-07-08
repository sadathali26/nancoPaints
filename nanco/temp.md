import React, { useState, useEffect } from 'react';

// Mock Database for Icons & Features (simulating Supabase relational data)
const mockDb = {
  productFeatures: ["icon-abc", "icon-def"],
  productWarranty: "icon-xyz",
  icons: [
    { id: "icon-abc", name: "Water Resistant", category: "Specification", image_url: "https://cdn-icons-png.flaticon.com/512/427/427112.png" },
    { id: "icon-def", name: "Anti-Fungal", category: "Specification", image_url: "https://cdn-icons-png.flaticon.com/512/2061/2061125.png" },
    { id: "icon-xyz", name: "5 Year Warranty", category: "Warranty Icon", image_url: "https://cdn-icons-png.flaticon.com/512/6561/6561081.png" }
  ]
};

// Pricing Data configuration
const productData = {
  basePrice: {
    "20L": { mrp: 6500, price: 5200, code: "NC-EL-20" },
    "10L": { mrp: 3400, price: 2750, code: "NC-EL-10" },
    "4L":  { mrp: 1450, price: 1180, code: "NC-EL-4" },
    "1L":  { mrp: 400,  price: 325,  code: "NC-EL-1" }
  }
};

const shades = [
  { name: "Oceanic Blue", color: "#2665d6" },
  { name: "Crimson Red", color: "#780016" },
  { name: "Forest Green", color: "#254f1a" },
  { name: "Mustard Pop", color: "#d6a337" }
];

export default function App() {
  const [isOpen, setIsOpen] = useState(false);
  const [unit, setUnit] = useState("20L");
  const [qty, setQty] = useState(1);
  const [selectedShade, setSelectedShade] = useState(null);
  const [showDatasheet, setShowDatasheet] = useState(false);
  const [toast, setToast] = useState({ show: false, message: "", type: "success" });

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  // Toast auto-hide logic
  useEffect(() => {
    if (toast.show) {
      const timer = setTimeout(() => setToast({ ...toast, show: false }), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast.show]);

  const currentPricing = productData.basePrice[unit];
  const totalMrp = currentPricing.mrp * qty;
  const totalPrice = currentPricing.price * qty;
  const savings = totalMrp - totalPrice;

  const formatCurrency = (num) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(num);

  const handleQtyChange = (e) => {
    let val = parseInt(e.target.value);
    if (isNaN(val) || val < 1) val = 1;
    setQty(val);
  };

  const showMessage = (message, type = 'success') => {
    setToast({ show: true, message, type });
  };

  const openCalculator = () => {
    const params = new URLSearchParams({ name: "Nanco Gloss Enamel", coverage: "120" });
    showMessage(`Redirecting to Paint Calculator...`, 'success');
    // window.location.href = `calculator.html?${params.toString()}`;
  };

  const handleSelectShade = () => {
    const randomShade = shades[Math.floor(Math.random() * shades.length)];
    setSelectedShade(randomShade);
    showMessage(`Shade '${randomShade.name}' selected`, 'success');
  };

  const handleAddToCart = (isBuyNow) => {
    const shadeText = selectedShade ? ` (${selectedShade.name})` : "";
    const action = isBuyNow ? "Redirecting to checkout..." : "Added to Cart!";
    showMessage(`${qty}x ${unit} Enamel${shadeText} ${action}`, 'success');
    if (isBuyNow) {
      setTimeout(() => setIsOpen(false), 1200);
    }
  };

  return (
    <div className="min-h-screen bg-[#f3f3f1] font-sans flex items-center justify-center p-4 selection:bg-[#d2e823] selection:text-black">
      {/* Injecting Tailwind and FontAwesome via CDN for the environment */}
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800;900&display=swap" rel="stylesheet" />
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
      
      <style dangerouslySetInnerHTML={{__html: `
        :root {
          --color-lime-spark: #d2e823;
          --color-linen-canvas: #f3f3f1;
          --color-white-plate: #ffffff;
          --color-ink-black: #000000;
          --color-maroon-plate: #780016;
          --color-cobalt-band: #2665d6;
          --color-leaf-wash: #ebffc5;
          --color-lavender-mist: #e9c0e9;
          --color-moss-tint: #e8efd6;
          --color-sage-mute: #676b5f;
        }
        body { font-family: 'Inter', sans-serif; background-image: radial-gradient(var(--color-sage-mute) 1px, transparent 1px); background-size: 24px 24px; }
        .bento-border { border: 2.5px solid var(--color-ink-black); }
        .bento-border-thick { border: 3px solid var(--color-ink-black); }
        .custom-scrollbar::-webkit-scrollbar { width: 8px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: var(--color-white-plate); border-left: 2px solid var(--color-ink-black); }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: var(--color-ink-black); border-radius: 99px; }
      `}} />

      {}
      <button 
        onClick={() => setIsOpen(true)}
        className="bg-[var(--color-lime-spark)] text-black font-black text-lg px-8 py-4 rounded-[99px] bento-border-thick transition-transform hover:-translate-y-1 active:translate-y-0 flex items-center gap-3"
      >
        <i className="fas fa-eye text-xl"></i> Quick View Product
      </button>

      {}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
          
          <div 
            className="w-full max-w-[1100px] max-h-[95vh] bg-[var(--color-linen-canvas)] rounded-[32px] md:rounded-[40px] bento-border-thick flex flex-col md:flex-row relative overflow-hidden animate-in zoom-in-95 duration-300 shadow-none"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button 
              onClick={() => setIsOpen(false)}
              className="absolute top-4 right-4 md:top-6 md:right-6 z-10 w-12 h-12 bg-white rounded-[99px] bento-border flex items-center justify-center text-xl hover:bg-red-100 transition-colors"
            >
              <i className="fas fa-times"></i>
            </button>

            {}
            <div className="w-full md:w-[45%] flex flex-col items-center justify-start p-6 md:p-10 border-b-[3px] md:border-b-0 md:border-r-[3px] border-black bg-[var(--color-linen-canvas)] overflow-y-auto custom-scrollbar relative">
              
              {/* Product Image */}
              <div className="w-full max-w-[280px] md:max-w-[340px] aspect-square rounded-[32px] bento-border-thick overflow-hidden bg-white mb-8 shrink-0 relative">
                <img 
                  src="https://sawbglsfqyayuysqcjto.supabase.co/storage/v1/object/public/item-images/ITM-5479-17.jpeg" 
                  alt="Product" 
                  className="absolute inset-0 w-full h-full object-cover mix-blend-multiply p-4"
                />
              </div>

              {/* Dynamic Icons Block */}
              <div className="w-full flex flex-wrap justify-center gap-6 mb-10">
                {mockDb.productFeatures.map(fId => {
                  const icon = mockDb.icons.find(i => i.id === fId);
                  if (!icon) return null;
                  return (
                    <div key={fId} className="flex flex-col items-center gap-2 w-20 group cursor-default">
                      <div className="w-14 h-14 bg-white rounded-[24px] bento-border flex items-center justify-center p-3 group-hover:-translate-y-1 transition-transform">
                        <img src={icon.image_url} alt={icon.name} className="w-full h-full object-contain opacity-90" />
                      </div>
                      <span className="text-[10px] font-black text-center uppercase leading-tight tracking-tight">{icon.name}</span>
                    </div>
                  );
                })}
                {mockDb.productWarranty && (
                  <div className="flex flex-col items-center gap-2 w-20 group cursor-default">
                    <div className="w-14 h-14 bg-[var(--color-cobalt-band)] rounded-[24px] bento-border flex items-center justify-center p-3 group-hover:-translate-y-1 transition-transform">
                      <img src={mockDb.icons.find(i => i.id === mockDb.productWarranty)?.image_url} alt="Warranty" className="w-full h-full object-contain brightness-0 invert" />
                    </div>
                    <span className="text-[10px] font-black text-[var(--color-cobalt-band)] text-center uppercase leading-tight tracking-tight">
                      {mockDb.icons.find(i => i.id === mockDb.productWarranty)?.name}
                    </span>
                  </div>
                )}
              </div>

              {/* Paint Calculator Button */}
              <button 
                onClick={openCalculator}
                className="w-full py-4 px-6 rounded-[99px] font-black text-sm uppercase tracking-wider bento-border bg-white hover:bg-[var(--color-leaf-wash)] hover:-translate-y-1 transition-transform flex justify-center items-center gap-3 mt-auto shrink-0"
              >
                <i className="fas fa-calculator text-lg"></i> Paint Calculator
              </button>
            </div>

            {}
            <div className="w-full md:w-[55%] p-6 md:p-10 flex flex-col bg-white overflow-y-auto custom-scrollbar">
              
              <div className="flex gap-2 mb-6 flex-wrap">
                <span className="bg-[var(--color-linen-canvas)] bento-border px-4 py-1.5 rounded-[99px] text-[11px] font-black uppercase tracking-widest">Interior</span>
                <span className="bg-[var(--color-cobalt-band)] text-white bento-border px-4 py-1.5 rounded-[99px] text-[11px] font-black uppercase tracking-widest">Best Seller</span>
              </div>
              
              <h2 className="text-4xl md:text-6xl font-black mb-2 uppercase leading-[0.95] tracking-[-0.04em]">Nanco Gloss Enamel</h2>
              <div className="text-sm font-black text-[var(--color-sage-mute)] mb-8 uppercase tracking-widest">Nanco Paints</div>

              <p className="text-base font-semibold leading-relaxed mb-8">
                High-quality, durable enamel paint providing a rich glossy finish. Perfect for interior wood, metal, and masonry surfaces. Offers excellent coverage and washability.
              </p>

              {/* Bento Feature Grid */}
              <div className="grid grid-cols-3 gap-3 mb-8">
                <div className="p-4 rounded-[24px] bento-border text-center flex flex-col items-center justify-center bg-[var(--color-leaf-wash)]">
                  <i className="fas fa-paint-brush mb-3 text-xl"></i>
                  <div className="text-sm font-black uppercase tracking-tight">Glossy</div>
                  <div className="text-[10px] font-black text-[var(--color-sage-mute)] mt-1 uppercase tracking-wider">Finish</div>
                </div>
                <div className="p-4 rounded-[24px] bento-border text-center flex flex-col items-center justify-center bg-[var(--color-lavender-mist)]">
                  <i className="fas fa-ruler-combined mb-3 text-xl"></i>
                  <div className="text-sm font-black uppercase tracking-tight">120 sq.ft</div>
                  <div className="text-[10px] font-black text-[var(--color-sage-mute)] mt-1 uppercase tracking-wider">Coverage</div>
                </div>
                <div className="p-4 rounded-[24px] bento-border text-center flex flex-col items-center justify-center bg-[var(--color-moss-tint)]">
                  <i className="fas fa-layer-group mb-3 text-xl"></i>
                  <div className="text-sm font-black uppercase tracking-tight">Premium</div>
                  <div className="text-[10px] font-black text-[var(--color-sage-mute)] mt-1 uppercase tracking-wider">Range</div>
                </div>
              </div>

              {/* Shade Selector Section */}
              {selectedShade ? (
                <div className="flex items-center gap-4 mb-6 p-4 rounded-[24px] bento-border bg-[var(--color-linen-canvas)]">
                  <div className="w-12 h-12 rounded-[99px] bento-border" style={{ backgroundColor: selectedShade.color }}></div>
                  <div className="flex-1">
                    <div className="text-[10px] font-black text-[var(--color-sage-mute)] uppercase tracking-wider">Selected Shade</div>
                    <div className="text-base font-black uppercase tracking-tight">{selectedShade.name}</div>
                  </div>
                  <button onClick={() => setSelectedShade(null)} className="w-10 h-10 rounded-[99px] bento-border bg-white flex items-center justify-center hover:bg-[var(--color-maroon-plate)] hover:text-white transition-colors">
                    <i className="fas fa-times"></i>
                  </button>
                </div>
              ) : (
                <button 
                  onClick={handleSelectShade}
                  className="w-full py-4 px-6 rounded-[99px] font-black text-sm mb-6 flex items-center justify-center gap-3 bento-border bg-white hover:bg-black hover:text-white transition-all uppercase tracking-wide"
                >
                  <i className="fas fa-palette text-lg"></i> <span>Select Shade</span>
                </button>
              )}

              {/* Expandable Specifications */}
              <button 
                onClick={() => setShowDatasheet(!showDatasheet)}
                className="w-fit py-2.5 px-6 rounded-[99px] font-black text-xs mb-4 flex items-center gap-2 bento-border bg-white hover:bg-[var(--color-linen-canvas)] transition-colors uppercase tracking-wider"
              >
                <i className="fas fa-file-pdf"></i> <span>View Datasheet</span> 
                <i className={`fas fa-chevron-down transition-transform duration-300 ${showDatasheet ? 'rotate-180' : ''}`}></i>
              </button>

              {showDatasheet && (
                <div className="flex flex-col md:flex-row gap-6 mb-8 p-6 rounded-[24px] bento-border bg-[var(--color-linen-canvas)] animate-in slide-in-from-top-2">
                  <div className="flex-1">
                    <h4 className="text-xs font-black uppercase mb-3 tracking-widest">Specs</h4>
                    <ul className="text-sm font-bold space-y-2">
                      <li><i className="fas fa-circle text-[8px] mr-2"></i> Enamel Paint</li>
                      <li><i className="fas fa-circle text-[8px] mr-2"></i> Oil Based</li>
                      <li><i className="fas fa-circle text-[8px] mr-2"></i> Deep Base</li>
                    </ul>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-xs font-black uppercase mb-3 tracking-widest text-[var(--color-maroon-plate)]">Notes</h4>
                    <ul className="text-sm font-bold space-y-2 text-[var(--color-maroon-plate)]">
                      <li><i className="fas fa-exclamation-triangle text-[10px] mr-2"></i> Primer recommended</li>
                      <li><i className="fas fa-exclamation-triangle text-[10px] mr-2"></i> 24hr drying time</li>
                    </ul>
                  </div>
                </div>
              )}

              {}
              <div className="flex gap-4 mb-8 mt-auto pt-4">
                <div className="flex-1 relative">
                  <label className="text-[11px] font-black uppercase mb-2 block tracking-widest">Unit</label>
                  <select 
                    value={unit} 
                    onChange={(e) => setUnit(e.target.value)}
                    className="w-full p-4 rounded-[16px] bento-border bg-white font-black text-base appearance-none cursor-pointer focus:outline-none focus:ring-4 focus:ring-[var(--color-leaf-wash)]"
                  >
                    <option value="20L">20 Ltr</option>
                    <option value="10L">10 Ltr</option>
                    <option value="4L">4 Ltr</option>
                    <option value="1L">1 Ltr</option>
                  </select>
                  <i className="fas fa-chevron-down absolute right-5 top-[45px] pointer-events-none"></i>
                </div>
                <div className="w-28">
                  <label className="text-[11px] font-black uppercase mb-2 block tracking-widest">Qty</label>
                  <input 
                    type="number" 
                    value={qty} 
                    onChange={handleQtyChange}
                    min="1"
                    className="w-full p-4 rounded-[16px] bento-border bg-white font-black text-base text-center focus:outline-none focus:ring-4 focus:ring-[var(--color-leaf-wash)]"
                  />
                </div>
              </div>
              
              <div className="flex justify-between items-center mb-8 p-6 rounded-[24px] bento-border bg-[var(--color-linen-canvas)]">
                <div>
                  <div className="text-sm font-black line-through mb-1 text-[var(--color-sage-mute)]">MRP: {formatCurrency(totalMrp)}</div>
                  <div className="text-4xl md:text-5xl font-black tracking-tighter leading-none">{formatCurrency(totalPrice)}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-black text-[var(--color-forest-ink)] mb-1 uppercase tracking-wide">Save {formatCurrency(savings)}</div>
                  <div className="text-[11px] font-black text-[var(--color-sage-mute)] uppercase tracking-wider">Code: {currentPricing.code}</div>
                </div>
              </div>

              {/* Bottom Actions */}
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={() => handleAddToCart(false)}
                  className="flex-1 py-4 px-6 rounded-[99px] font-black text-sm uppercase tracking-wide bento-border bg-white hover:bg-[var(--color-linen-canvas)] hover:-translate-y-1 transition-transform flex justify-center items-center gap-3"
                >
                  <i className="fas fa-cart-plus text-lg"></i> Add to Cart
                </button>
                <button 
                  onClick={() => handleAddToCart(true)}
                  className="flex-1 py-4 px-6 rounded-[99px] font-black text-sm uppercase tracking-wide bento-border bg-[var(--color-lime-spark)] hover:brightness-95 hover:-translate-y-1 transition-transform flex justify-center items-center gap-3"
                >
                  <i className="fas fa-bolt text-lg"></i> Buy Now
                </button>
              </div>

            </div>
          </div>
        </div>
      )}

      {}
      <div 
        className={`fixed top-6 right-6 z-[9999] flex items-center gap-4 p-4 rounded-[24px] bento-border-thick shadow-none transition-transform duration-300 ${toast.show ? 'translate-x-0' : 'translate-x-[150%]'}`}
        style={{
          backgroundColor: toast.type === 'success' ? 'var(--color-lime-spark)' : 'var(--color-maroon-plate)',
          color: toast.type === 'success' ? 'black' : 'white'
        }}
      >
        <i className={`fas ${toast.type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} text-2xl`}></i>
        <span className="font-black uppercase tracking-wide text-sm">{toast.message}</span>
      </div>

    </div>
  );
}