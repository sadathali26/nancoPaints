const NancoAssets = {
  logos: {
    light: "../nanco/assets/light-logo.png",
    dark: "../nanco/assets/dark-logo.png",
    main: "../nanco/assets/logo.png"
  },
  hero: {
    houseBg: "../nanco/assets/house-bg.png",
    houseBg1: "../nanco/assets/house-bg1.png",
    bucket: "../nanco/assets/bucket.png",
    heroPaint: "../nanco/assets/HERO-PAINT.png"
  },
  palettes: {
    bg1: "../nanco/assets/pallette-bg/1.jpg",
    bg2: "../nanco/assets/pallette-bg/2.jpg",
    bg3: "../nanco/assets/pallette-bg/3.jpg",
    bg4: "../nanco/assets/pallette-bg/4.jpg",
    bg5: "../nanco/assets/pallette-bg/5.jpg",
    bg6: "../nanco/assets/pallette-bg/6.jpg",
    bg8: "../nanco/assets/pallette-bg/8.jpg",
    fg1: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/colour-of-the-year/desktop/moonlit-silk-updated-desktop.webp",
    fg2: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/colour-of-the-year/desktop/cardinal-room-desktop.webp",
    fg3: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/colour-of-the-year/desktop/terra-room-desktop.webp",
    fg4: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/colour-of-the-year/desktop/silver-escapade-room-desktop.webp",
    fg5: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/colour-of-the-year/desktop/transcendent-pink-room-desktop.webp",
    fg6: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/colour-of-the-year/desktop/cherish-room-desktop.webp",
    fg8: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/colour-of-the-year/desktop/curiosity-room-desktop.webp"
  },
  featured: {
    glitzDesktop: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/featured-products/featured-product-royale-glitz-desk-updated.webp",
    glitzMobile: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/featured-products/royale-glitz-mobile-updated.webp",
    protekDesktop: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/featured-products/all-protek-desktop-updated.webp",
    protekMobile: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/featured-products/all-protek-mobile-updated.webp",
    ultimaDesktop: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/featured-products/ultima-protek-desktop-updated.webp",
    ultimaMobile: "https://static.asianpaints.com/content/dam/asian_paints/home-ph2/featured-products/ultima-protek-mobile-updated.webp"
  },
  videos: {
    v1: "../nanco/videos/1.mp4",
    v2: "../nanco/videos/2.mp4",
    v3: "../nanco/videos/3.mp4",
    v4: "../nanco/videos/4.mp4",
    v5: "../nanco/videos/5.mp4",
    v6: "../nanco/videos/6.mp4",
    v7: "../nanco/videos/7.mp4",
    v8: "../nanco/videos/8.mp4",
    v9: "../nanco/videos/9.mp4"
  },
  misc: {
    pattern: "../nanco/assets/pattern.jpg",
    servicesHero: "../nanco/assets/sa.png",
    visualizerBg: "../nanco/assets/visualizer bg.jpg",
    calcBg: "../nanco/assets/calcbg.jpg",
    aboutBg: "../nanco/assets/outlet.png",
    addressBg: "../nanco/assets/Why Humidity Matters.jpg"
  }
};

document.addEventListener('DOMContentLoaded', () => {
  // Inject attributes into image and source tags
  document.querySelectorAll('[data-asset]').forEach(el => {
    const keys = el.getAttribute('data-asset').split('.');
    let value = NancoAssets;
    for (const key of keys) {
      if (value) value = value[key];
    }
    if (value) {
      el.src = value;
    }
  });

  document.querySelectorAll('[data-asset-srcset]').forEach(el => {
    const keys = el.getAttribute('data-asset-srcset').split('.');
    let value = NancoAssets;
    for (const key of keys) {
      if (value) value = value[key];
    }
    if (value) {
      el.srcset = value;
    }
  });

  // Inject favicons dynamically as well to avoid hardcoding
  document.querySelectorAll('link[data-asset-href]').forEach(el => {
    const keys = el.getAttribute('data-asset-href').split('.');
    let value = NancoAssets;
    for (const key of keys) {
      if (value) value = value[key];
    }
    if (value) {
      el.href = value;
    }
  });
});
