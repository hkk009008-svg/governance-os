/**
 * 닥터루템 (Dr. ROOTEM) Official Store Interactive App
 */

// 1. Official Product Data (drrootem.com)
const OFFICIAL_PRODUCTS = [
  {
    id: 1,
    name: "이시형 박사의 두뇌엔 PS 70",
    category: "brain",
    tag: "이시형 박사 추천",
    badge: "1+1 기획전",
    desc: "식약처 인증 포스파티딜세린 300mg 최고 함량 + 징코빌로바. 인지력 & 중장년 기억력 개선 1위 솔루션.",
    salePrice: 24800,
    origPrice: 33500,
    discount: "26% OFF",
    rating: 4.9,
    reviews: 14820,
    theme: "ps-theme",
    color: "#047857"
  },
  {
    id: 2,
    name: "닥터루템 리포좀 비타민C 1000",
    category: "immune",
    tag: "가수 남진's PICK",
    badge: "체내 흡수율 250%",
    desc: "위장 장애 없는 리포좀 제형화 기술. 프리미엄 고함량 항산화 & 일상 활력 케어 비타민.",
    salePrice: 24800,
    origPrice: 31000,
    discount: "20% OFF",
    rating: 4.9,
    reviews: 9840,
    theme: "vitc-theme",
    color: "#d97706"
  },
  {
    id: 3,
    name: "닥터루템 THE 맥주효모 4000",
    category: "hair",
    tag: "독일산 원료 75%",
    badge: "재구매율 1위",
    desc: "독일산 프리미엄 건조맥주효모 + 프랑스산 비오틴 5,000µg. 풍성한 모발 생기 & 두피 영양 밸런스.",
    salePrice: 16900,
    origPrice: 22000,
    discount: "23% OFF",
    rating: 4.8,
    reviews: 6420,
    theme: "hair-theme",
    color: "#7c3aed"
  },
  {
    id: 4,
    name: "닥터루템 쏘팔메토 & 루테인 지아잔틴",
    category: "eye",
    tag: "남성 전립선 + 눈 건강",
    badge: "황금비율 복합배합",
    desc: "쏘팔메토 로르산 115mg + 마리골드 꽃 추출 루테인지아잔틴 24:4. 눈 피로 개선 & 남성 생기 충전.",
    salePrice: 28900,
    origPrice: 39000,
    discount: "25% OFF",
    rating: 4.9,
    reviews: 11200,
    theme: "eye-theme",
    color: "#2563eb"
  },
  {
    id: 5,
    name: "닥터루템 바나바잎 혈당케어 코로솔산",
    category: "metabolic",
    tag: "식후 혈당 억제",
    badge: "식약처 인정 기능성",
    desc: "바나바잎 추출 코로솔산 1.3mg + 크롬 & 셀렌. 탄수화물 섭취 후 식후 혈당 수치 밸런스 케어.",
    salePrice: 22800,
    origPrice: 29000,
    discount: "21% OFF",
    rating: 4.8,
    reviews: 4350,
    theme: "blood-theme",
    color: "#dc2626"
  },
  {
    id: 6,
    name: "닥터루템 초임계 rTG 오메가3 플래티넘",
    category: "metabolic",
    tag: "혈행 & 건조한 눈",
    badge: "저온 초임계 추출",
    desc: "체내 흡수율이 높은 rTG 구조 오메가3 600mg + 비타민E. 순도 80% 이상의 혈행 개선 및 눈 건강.",
    salePrice: 27900,
    origPrice: 36000,
    discount: "22% OFF",
    rating: 4.9,
    reviews: 5890,
    theme: "omega-theme",
    color: "#059669"
  }
];

const REVIEWS_DATA = [
  {
    user: "김*원 님 (50대)",
    rating: "★★★★★ 5.0",
    product: "이시형 박사의 두뇌엔 PS 70",
    text: "이시형 박사님 추천이라 믿고 1+1 구성 구매했습니다. 자주 깜빡거리던 게 3주 정도 섭취 후 한결 머리가 맑아진 느낌이에요!"
  },
  {
    user: "박*호 님 (40대)",
    rating: "★★★★★ 5.0",
    product: "닥터루템 리포좀 비타민C 1000",
    text: "가수 남진 씨 광고 보고 샀는데 일반 비타민C와 달리 속 쓰림이 전혀 없네요. 피로감이 덜해서 매일 아침 꼭 챙깁니다."
  },
  {
    user: "최*진 님 (30대)",
    rating: "★★★★★ 5.0",
    product: "닥터루템 THE 맥주효모 4000",
    text: "머리 감을 때 빠지는 양이 현저히 줄었어요. 비오틴까지 고함량으로 들어있어서 가성비 최고입니다."
  }
];

// App State
let cart = [];
let currentCategory = "all";

document.addEventListener("DOMContentLoaded", () => {
  initNavbar();
  initCarousel();
  renderProducts("all");
  renderReviews();
  initCartDrawer();
  initCouponModal();
  initTheme();
});

// Theme Switcher
function initTheme() {
  const toggle = document.getElementById("themeToggle");
  const saved = localStorage.getItem("drrootem_theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);

  toggle.addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("drrootem_theme", next);
    showToast(`테마가 ${next === "dark" ? "다크" : "라이트"} 모드로 전환되었습니다.`);
  });
}

// Navbar & Announcement Top Bar
function initNavbar() {
  const closeBar = document.getElementById("topBarClose");
  if (closeBar) {
    closeBar.addEventListener("click", () => {
      document.querySelector(".top-bar").style.display = "none";
    });
  }

  // Category Shortcut Chips
  const chips = document.querySelectorAll(".cat-chip");
  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      renderProducts(chip.dataset.cat);
    });
  });
}

// Carousel Banner
function initCarousel() {
  const dots = document.querySelectorAll(".dot");
  let slideIndex = 0;

  dots.forEach(dot => {
    dot.addEventListener("click", () => {
      slideIndex = parseInt(dot.dataset.slide);
      updateCarousel(slideIndex);
    });
  });

  setInterval(() => {
    slideIndex = (slideIndex + 1) % 2;
    updateCarousel(slideIndex);
  }, 5000);
}

function updateCarousel(index) {
  const dots = document.querySelectorAll(".dot");
  const slides = document.querySelectorAll(".carousel-slide");
  dots.forEach((d, i) => d.classList.toggle("active", i === index));
  slides.forEach((s, i) => s.classList.toggle("active", i === index));
}

// Products Catalog Render
function renderProducts(category = "all") {
  const grid = document.getElementById("productsGrid");
  const filtered = category === "all" ? OFFICIAL_PRODUCTS : OFFICIAL_PRODUCTS.filter(p => p.category === category);

  grid.innerHTML = filtered.map(p => `
    <div class="p-card">
      <div>
        <div class="p-badge">${p.badge} · ${p.tag}</div>
        <h3 class="p-title">${p.name}</h3>
        <p class="p-desc">${p.desc}</p>
        <div class="p-price-box">
          <span class="p-disc">${p.discount}</span>
          <span class="p-sale">${p.salePrice.toLocaleString()}원</span>
          <span class="p-orig">${p.origPrice.toLocaleString()}원</span>
        </div>
      </div>

      <div style="display: flex; gap: 8px;">
        <button class="btn btn-primary w-full" onclick="openOptionModal(${p.id})">
          <span>옵션선택 & 구매</span>
        </button>
      </div>
    </div>
  `).join("");
}

// Reviews Render
function renderReviews() {
  const grid = document.getElementById("reviewGrid");
  grid.innerHTML = REVIEWS_DATA.map(r => `
    <div class="rev-card">
      <div class="rev-head">
        <span>${r.user}</span>
        <span class="rev-star">${r.rating}</span>
      </div>
      <div class="rev-prod">[공식몰 구매] ${r.product}</div>
      <p class="rev-text">${r.text}</p>
    </div>
  `).join("");
}

// Option Modal & Direct Purchase
function openOptionModal(productId) {
  const p = OFFICIAL_PRODUCTS.find(item => item.id === productId);
  if (!p) return;

  const overlay = document.getElementById("optionModalOverlay");
  const content = document.getElementById("optionModalContent");

  content.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:16px;">
      <div>
        <span class="p-badge">${p.badge}</span>
        <h3 style="font-size: 1.4rem; font-weight:800; margin-top:6px;">${p.name}</h3>
      </div>
    </div>
    
    <p style="color: var(--text-sub); font-size:0.9rem; margin-bottom:20px;">${p.desc}</p>

    <div style="background: var(--bg-card); padding:16px; border-radius:12px; border:1px solid var(--border); margin-bottom:20px;">
      <div style="font-size:0.88rem; font-weight:700; margin-bottom:8px;">수량 및 구성 선택</div>
      <select id="optionQtySelect" style="width:100%; padding:10px; border-radius:8px; background:var(--bg-surface); color:var(--text-main); border:1px solid var(--border);">
        <option value="1">1박스 (1개월분) - ${p.salePrice.toLocaleString()}원</option>
        <option value="2" selected>2박스 [1+1 특별할인] - ${(p.salePrice * 1.8).toLocaleString()}원 (추가 10% OFF)</option>
        <option value="3">3박스 세트 - ${(p.salePrice * 2.5).toLocaleString()}원 (추가 15% OFF)</option>
      </select>
    </div>

    <div style="display:flex; gap:12px;">
      <button class="btn btn-primary btn-lg w-full" onclick="confirmAddToCart(${p.id})">장바구니 담기</button>
    </div>
  `;

  overlay.classList.add("active");
  document.getElementById("optionModalClose").onclick = () => overlay.classList.remove("active");
  overlay.onclick = (e) => { if (e.target === overlay) overlay.classList.remove("active"); };
}

function confirmAddToCart(productId) {
  const p = OFFICIAL_PRODUCTS.find(item => item.id === productId);
  const select = document.getElementById("optionQtySelect");
  const qtyMultiplier = parseInt(select.value);

  const existing = cart.find(i => i.id === productId);
  if (existing) {
    existing.qty += qtyMultiplier;
  } else {
    cart.push({ ...p, qty: qtyMultiplier });
  }

  document.getElementById("optionModalOverlay").classList.remove("active");
  updateCartUI();
  openCartDrawer();
  showToast(`${p.name} ${qtyMultiplier}세트가 장바구니에 담겼습니다!`);
}

// Cart Drawer
function initCartDrawer() {
  const btn = document.getElementById("cartBtn");
  const closeBtn = document.getElementById("cartCloseBtn");
  const overlay = document.getElementById("cartOverlay");
  const checkoutBtn = document.getElementById("checkoutBtn");

  btn.onclick = openCartDrawer;
  closeBtn.onclick = closeCartDrawer;
  overlay.onclick = closeCartDrawer;

  checkoutBtn.onclick = () => {
    if (cart.length === 0) {
      showToast("장바구니가 비어있습니다.");
      return;
    }
    showToast("신규회원 30,000원 쿠폰이 적용되어 주문 완료되었습니다! (시뮬레이션)");
    cart = [];
    updateCartUI();
    closeCartDrawer();
  };
}

function openCartDrawer() {
  document.getElementById("cartDrawer").classList.add("active");
  document.getElementById("cartOverlay").classList.add("active");
}

function closeCartDrawer() {
  document.getElementById("cartDrawer").classList.remove("active");
  document.getElementById("cartOverlay").classList.remove("active");
}

function updateCartUI() {
  const badge = document.getElementById("cartBadge");
  const count = document.getElementById("cartCount");
  const list = document.getElementById("cartItemsList");
  const subtotalEl = document.getElementById("cartSubtotal");
  const discEl = document.getElementById("cartDiscount");
  const totalEl = document.getElementById("cartTotalPrice");

  const totalQty = cart.reduce((acc, i) => acc + i.qty, 0);
  const subtotal = cart.reduce((acc, i) => acc + (i.salePrice * i.qty), 0);
  const discount = subtotal > 0 ? Math.min(30000, subtotal * 0.15) : 0;
  const finalTotal = Math.max(0, subtotal - discount);

  badge.textContent = totalQty;
  count.textContent = totalQty;

  if (cart.length === 0) {
    list.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">장바구니가 비어있습니다.</div>`;
  } else {
    list.innerHTML = cart.map(i => `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; border:1px solid var(--border); border-radius:10px; margin-bottom:12px;">
        <div>
          <div style="font-weight:800; font-size:0.95rem;">${i.name}</div>
          <div style="color:var(--emerald); font-weight:800; margin-top:4px;">${(i.salePrice * i.qty).toLocaleString()}원</div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span>${i.qty}개</span>
          <button onclick="removeFromCart(${i.id})" style="color:var(--text-muted); font-size:1.2rem;">&times;</button>
        </div>
      </div>
    `).join("");
  }

  subtotalEl.textContent = `${subtotal.toLocaleString()}원`;
  discEl.textContent = `-${Math.round(discount).toLocaleString()}원`;
  totalEl.textContent = `${Math.round(finalTotal).toLocaleString()}원`;
}

function removeFromCart(id) {
  cart = cart.filter(i => i.id !== id);
  updateCartUI();
}

// Coupon Modal
function initCouponModal() {
  const btn = document.getElementById("couponClaimBtn");
  const overlay = document.getElementById("couponModalOverlay");
  const closeBtn = document.getElementById("couponModalClose");
  const applyBtn = document.getElementById("applyCouponBtn");

  if (btn) btn.onclick = () => overlay.classList.add("active");
  if (closeBtn) closeBtn.onclick = () => overlay.classList.remove("active");
  if (applyBtn) {
    applyBtn.onclick = () => {
      overlay.classList.remove("active");
      showToast("🎉 30,000원 웰컴 쿠폰팩이 장바구니에 적용되었습니다!");
    };
  }
}

// Toast Helper
function showToast(msg) {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 3000);
}
