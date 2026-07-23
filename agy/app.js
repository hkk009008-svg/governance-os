/**
 * Dr. Rootem (닥터루템) Interactive E-Commerce & Health App
 */

// 1. Data Store
const PRODUCTS = [
  {
    id: 1,
    name: "닥터루템 포스파티딜세린 70",
    category: "brain",
    categoryLabel: "뇌 & 기억력",
    desc: "식약처 고시 최고 함량 포스파티딜세린 300mg + 징코 빌로바 콤플렉스. 뇌 세포막 건강 및 중장년 기억력 개선.",
    price: 48000,
    originalPrice: 65000,
    discount: "26% OFF",
    rating: 4.9,
    reviews: 3420,
    badge: "BEST SELL",
    color: "#10b981"
  },
  {
    id: 2,
    name: "닥터루템 리포좀 비타민C 1000",
    category: "immune",
    categoryLabel: "면역 & 항산화",
    desc: "체내 흡수율 2.5배 높인 리포좀 제형 기술. 위장 장애 없는 프리미엄 위드 아세로라 고함량 항산화 케어.",
    price: 36000,
    originalPrice: 45000,
    discount: "20% OFF",
    rating: 4.8,
    reviews: 2150,
    badge: "흡수율 UP",
    color: "#f59e0b"
  },
  {
    id: 3,
    name: "닥터루템 맥주효모 비오틴 콤플렉스",
    category: "hair",
    categoryLabel: "두피 & 모발",
    desc: "독일산 프리미엄 맥주효모 75% + 프랑스산 비오틴 5,000µg (16,666%). 풍성하고 탄탄한 두피 모근 완성.",
    price: 32000,
    originalPrice: 42000,
    discount: "23% OFF",
    rating: 4.9,
    reviews: 1890,
    badge: "재구매 1위",
    color: "#8b5cf6"
  },
  {
    id: 4,
    name: "닥터루템 쏘팔메토 & 루테인 지아잔틴",
    category: "eye",
    categoryLabel: "눈 & 활력",
    desc: "남성 전립선 건강 쏘팔메토 로르산 + 마리골드꽃 추출 루테인지아잔틴 24:4 황금비율. 눈 피로 & 생기 개선.",
    price: 42000,
    originalPrice: 58000,
    discount: "27% OFF",
    rating: 4.9,
    reviews: 4120,
    badge: "복합 배합",
    color: "#3b82f6"
  },
  {
    id: 5,
    name: "닥터루템 바나바잎 혈당케어",
    category: "metabolic",
    categoryLabel: "혈당 & 대사",
    desc: "식후 혈당 상승 억제 코로솔산 1.3mg + 크롬 & 셀렌 콤플렉스. 탄수화물 섭취 후 당 대사 밸런스 유지.",
    price: 38000,
    originalPrice: 49000,
    discount: "22% OFF",
    rating: 4.7,
    reviews: 1240,
    badge: "식후 필수",
    color: "#ef4444"
  }
];

const INITIAL_REVIEWS = [
  {
    id: 1,
    user: "김*진 님",
    rating: 5,
    product: "닥터루템 포스파티딜세린 70",
    content: "부모님 선물로 사드렸는데 깜빡거리시던 게 확실히 줄었다고 좋아하세요. 알약 크기도 작아서 목넘김이 편합니다!"
  },
  {
    id: 2,
    user: "박*우 님",
    rating: 5,
    product: "닥터루템 리포좀 비타민C 1000",
    content: "기존 비타민C는 속이 쓰렸는데 리포좀 제형이라 그런지 속도 속 편하고 피부 톤도 맑아진 느낌입니다. 재구매 3번째!"
  },
  {
    id: 3,
    user: "이*혜 님",
    rating: 5,
    product: "닥터루템 맥주효모 비오틴 콤플렉스",
    content: "머리 감을 때 빠지는 양이 확연히 달라졌어요. 맥주효모 비오틴 조합 강력 추천합니다."
  }
];

const WIZARD_STEPS = [
  {
    question: "가장 개선하고 싶은 건강 고민은 무엇인가요?",
    options: [
      { text: "잦은 건망증과 집중력 감소 (뇌 & 기억력)", category: "brain" },
      { text: "스마트폰/모니터로 인한 눈 피로 (눈 건강)", category: "eye" },
      { text: "환절기 면역력 및 피부 항산화 케어", category: "immune" },
      { text: "두피 가려움과 모발 가늘어짐", category: "hair" },
      { text: "식후 식곤증과 혈당 조절 걱정", category: "metabolic" }
    ]
  },
  {
    question: "평소 하루 생활 습관은 어떤 편인가요?",
    options: [
      { text: "하루 8시간 이상 PC/스마트폰 업무", value: "high_screen" },
      { text: "잦은 외식과 탄수화물/디저트 선호", value: "high_carb" },
      { text: "스트레스가 많고 야근이 잦음", value: "high_stress" },
      { text: "불규칙한 식사와 야채 섭취 부족", value: "low_nutrition" }
    ]
  }
];

// App State
let cart = [];
let reviews = [...INITIAL_REVIEWS];
let currentWizardStep = 0;
let wizardAnswers = [];

// DOM Elements
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  renderProducts("all");
  renderReviews("all");
  initWizard();
  initCalculator();
  initCartEvents();
  initReviewModal();
});

// Theme Switcher
function initTheme() {
  const toggleBtn = document.getElementById("themeToggle");
  const savedTheme = localStorage.getItem("drrootem_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);

  toggleBtn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("drrootem_theme", next);
    showToast(`화면 테마가 ${next === "dark" ? "다크" : "라이트"} 모드로 변경되었습니다.`);
  });
}

// Render Products Catalog
function renderProducts(categoryFilter = "all") {
  const grid = document.getElementById("productGrid");
  const filtered = categoryFilter === "all" 
    ? PRODUCTS 
    : PRODUCTS.filter(p => p.category === categoryFilter);

  grid.innerHTML = filtered.map(product => `
    <div class="glass-card product-card" data-category="${product.category}">
      <div>
        <div class="product-tag">${product.badge} · ${product.categoryLabel}</div>
        <div class="product-img-box">
          <div class="bottle-mockup" style="transform: scale(0.9);">
            <div class="cap"></div>
            <div class="body" style="background: linear-gradient(135deg, ${product.color}, #047857);">
              <div class="label-brand">Dr.Rootem</div>
              <div class="label-title">${product.name.replace("닥터루템 ", "")}</div>
            </div>
          </div>
        </div>
        <h3 class="product-name">${product.name}</h3>
        <p class="product-desc">${product.desc}</p>
      </div>

      <div>
        <div class="product-price-row">
          <span class="price-current">₩${product.price.toLocaleString()}</span>
          <span class="price-original">₩${product.originalPrice.toLocaleString()}</span>
          <span class="price-discount">${product.discount}</span>
        </div>
        <button class="btn btn-primary w-full" onclick="addToCart(${product.id})">
          <span>장바구니 담기</span>
        </button>
      </div>
    </div>
  `).join("");

  // Tab Active State
  const tabs = document.querySelectorAll("#filterTabs .tab-btn");
  tabs.forEach(tab => {
    tab.classList.toggle("active", tab.dataset.category === categoryFilter);
    tab.onclick = () => renderProducts(tab.dataset.category);
  });
}

// Cart Logic
function addToCart(productId) {
  const product = PRODUCTS.find(p => p.id === productId);
  if (!product) return;

  const existing = cart.find(item => item.id === productId);
  if (existing) {
    existing.qty += 1;
  } else {
    cart.push({ ...product, qty: 1 });
  }

  updateCartUI();
  openCartDrawer();
  showToast(`${product.name}이(가) 장바구니에 추가되었습니다.`);
}

function updateCartUI() {
  const badge = document.getElementById("cartBadge");
  const countTitle = document.getElementById("cartCountTitle");
  const itemsList = document.getElementById("cartItemsList");
  const subtotalEl = document.getElementById("cartSubtotal");
  const totalEl = document.getElementById("cartTotalPrice");

  const totalQty = cart.reduce((acc, item) => acc + item.qty, 0);
  const totalPrice = cart.reduce((acc, item) => acc + (item.price * item.qty), 0);

  badge.textContent = totalQty;
  countTitle.textContent = `${totalQty}개`;

  if (cart.length === 0) {
    itemsList.innerHTML = `<div class="text-center" style="padding: 40px; color: var(--text-muted);">장바구니가 비어 있습니다.</div>`;
  } else {
    itemsList.innerHTML = cart.map(item => `
      <div class="cart-item">
        <div class="cart-item-details">
          <div class="cart-item-title">${item.name}</div>
          <div class="cart-item-price">₩${(item.price * item.qty).toLocaleString()}</div>
          <div class="qty-controls">
            <button class="qty-btn" onclick="changeCartQty(${item.id}, -1)">-</button>
            <span>${item.qty}</span>
            <button class="qty-btn" onclick="changeCartQty(${item.id}, 1)">+</button>
          </div>
        </div>
        <button class="close-btn" onclick="removeFromCart(${item.id})" style="font-size: 1.2rem;">&times;</button>
      </div>
    `).join("");
  }

  subtotalEl.textContent = `₩${totalPrice.toLocaleString()}`;
  totalEl.textContent = `₩${totalPrice.toLocaleString()}`;
}

function changeCartQty(productId, delta) {
  const item = cart.find(i => i.id === productId);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) {
    cart = cart.filter(i => i.id !== productId);
  }
  updateCartUI();
}

function removeFromCart(productId) {
  cart = cart.filter(i => i.id !== productId);
  updateCartUI();
}

function initCartEvents() {
  const cartBtn = document.getElementById("cartBtn");
  const closeBtn = document.getElementById("closeCartBtn");
  const overlay = document.getElementById("cartOverlay");
  const checkoutBtn = document.getElementById("checkoutBtn");

  cartBtn.addEventListener("click", openCartDrawer);
  closeBtn.addEventListener("click", closeCartDrawer);
  overlay.addEventListener("click", closeCartDrawer);

  checkoutBtn.addEventListener("click", () => {
    if (cart.length === 0) {
      showToast("장바구니가 비어 있습니다.");
      return;
    }
    showToast("주문 페이지로 이동합니다. (시뮬레이션 완료)");
    cart = [];
    updateCartUI();
    closeCartDrawer();
  });
}

function openCartDrawer() {
  document.getElementById("cartDrawer").classList.add("active");
  document.getElementById("cartOverlay").classList.add("active");
}

function closeCartDrawer() {
  document.getElementById("cartDrawer").classList.remove("active");
  document.getElementById("cartOverlay").classList.remove("active");
}

// Wizard Solution
function initWizard() {
  renderWizardStep();

  document.getElementById("nextStepBtn").onclick = () => {
    if (currentWizardStep < WIZARD_STEPS.length - 1) {
      currentWizardStep++;
      renderWizardStep();
    } else {
      finishWizard();
    }
  };

  document.getElementById("prevStepBtn").onclick = () => {
    if (currentWizardStep > 0) {
      currentWizardStep--;
      renderWizardStep();
    }
  };
}

function renderWizardStep() {
  const stepContainer = document.getElementById("wizardStep");
  const prevBtn = document.getElementById("prevStepBtn");
  const nextBtn = document.getElementById("nextStepBtn");
  const stepData = WIZARD_STEPS[currentWizardStep];

  prevBtn.style.display = currentWizardStep === 0 ? "none" : "inline-flex";
  nextBtn.textContent = currentWizardStep === WIZARD_STEPS.length - 1 ? "맞춤 진단결과 보기" : "다음 단계로";

  stepContainer.innerHTML = `
    <div class="wizard-question">${stepData.question}</div>
    <div class="wizard-options">
      ${stepData.options.map((opt, i) => `
        <button class="opt-btn ${wizardAnswers[currentWizardStep] === i ? 'selected' : ''}" onclick="selectWizardOpt(${i})">
          <span>${opt.text}</span>
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
        </button>
      `).join("")}
    </div>
  `;
}

function selectWizardOpt(optIndex) {
  wizardAnswers[currentWizardStep] = optIndex;
  renderWizardStep();
}

function finishWizard() {
  const wizardBox = document.getElementById("wizardBox");
  const selectedCat = WIZARD_STEPS[0].options[wizardAnswers[0] || 0].category;
  const recommendedProduct = PRODUCTS.find(p => p.category === selectedCat) || PRODUCTS[0];

  wizardBox.innerHTML = `
    <div class="glass-card text-center" style="padding: 40px;">
      <div class="section-subtitle">YOUR PERSONAL RECOMMENDATION</div>
      <h3 style="font-size: 1.8rem; margin-bottom: 12px;">고객님을 위한 닥터루템 맞춤 조합</h3>
      <p style="color: var(--text-secondary); margin-bottom: 24px;">진단하신 라이프스타일 분석 결과, 아래 영양 솔루션이 가장 시급합니다.</p>
      
      <div style="background: var(--bg-surface); padding: 24px; border-radius: 12px; margin-bottom: 24px; border: 1px solid var(--border-hover);">
        <h4 style="color: var(--emerald-primary); font-size: 1.3rem; margin-bottom: 8px;">${recommendedProduct.name}</h4>
        <p style="font-size: 0.9rem; color: var(--text-secondary);">${recommendedProduct.desc}</p>
        <div style="font-size: 1.4rem; font-weight: 800; margin-top: 12px; color: var(--text-primary);">₩${recommendedProduct.price.toLocaleString()}</div>
      </div>

      <div style="display: flex; gap: 12px; justify-content: center;">
        <button class="btn btn-primary btn-lg" onclick="addToCart(${recommendedProduct.id})">추천 상품 담기</button>
        <button class="btn btn-outline btn-lg" onclick="resetWizard()">다시 진단하기</button>
      </div>
    </div>
  `;
}

function resetWizard() {
  currentWizardStep = 0;
  wizardAnswers = [];
  location.hash = "#wizard";
  initWizard();
}

// Calculator Logic
function initCalculator() {
  const screenSlider = document.getElementById("screenTimeSlider");
  const outdoorSlider = document.getElementById("outdoorTimeSlider");
  const brainSlider = document.getElementById("brainWorkSlider");
  const recommendBtn = document.getElementById("calcRecommendBtn");

  function updateCalc() {
    const screenVal = parseInt(screenSlider.value);
    const outdoorVal = parseInt(outdoorSlider.value);
    const brainVal = parseInt(brainSlider.value);

    document.getElementById("screenTimeVal").textContent = screenVal;
    document.getElementById("outdoorTimeVal").textContent = outdoorVal;
    document.getElementById("brainWorkVal").textContent = brainVal;

    // Score Algorithm
    let score = 100 - (screenVal * 3) - (brainVal * 3) + (outdoorVal * 4);
    score = Math.max(30, Math.min(98, score));

    document.getElementById("calcScoreNum").textContent = Math.round(score);

    // Circle progress dashoffset (max 264)
    const progressCircle = document.getElementById("scoreCircleProgress");
    const offset = 264 - (264 * (score / 100));
    progressCircle.style.strokeDashoffset = offset;

    // Bars
    document.getElementById("luteinBar").style.width = `${Math.max(20, 100 - screenVal * 6)}%`;
    document.getElementById("psBar").style.width = `${Math.max(25, 100 - brainVal * 7)}%`;
    document.getElementById("vitCBar").style.width = `${Math.min(95, 30 + outdoorVal * 10)}%`;
  }

  [screenSlider, outdoorSlider, brainSlider].forEach(s => s.addEventListener("input", updateCalc));
  updateCalc();

  recommendBtn.addEventListener("click", () => {
    addToCart(1); // Phosphatidylserine
    addToCart(4); // Lutein Saw Palmetto
  });
}

// Reviews & Modal Logic
function renderReviews(filter = "all") {
  const grid = document.getElementById("reviewsGrid");
  const filtered = reviews.filter(r => {
    if (filter === "5") return r.rating === 5;
    return true;
  });

  grid.innerHTML = filtered.map(rev => `
    <div class="glass-card review-card">
      <div class="rev-card-head">
        <span class="rev-user">${rev.user}</span>
        <span style="color: var(--gold-accent);">★ ${rev.rating}.0</span>
      </div>
      <div class="rev-prod-name">[구매] ${rev.product}</div>
      <p class="rev-body">${rev.content}</p>
    </div>
  `).join("");
}

function initReviewModal() {
  const writeBtn = document.getElementById("writeReviewBtn");
  const overlay = document.getElementById("reviewModalOverlay");
  const closeBtn = document.getElementById("closeReviewModal");
  const form = document.getElementById("reviewForm");

  writeBtn.addEventListener("click", () => overlay.classList.add("active"));
  closeBtn.addEventListener("click", () => overlay.classList.remove("active"));
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.classList.remove("active");
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const prodSelect = document.getElementById("reviewProductSelect");
    const nameInput = document.getElementById("reviewerName");
    const contentInput = document.getElementById("reviewContent");

    const newRev = {
      id: Date.now(),
      user: `${nameInput.value.slice(0, 1)}*${nameInput.value.slice(-1)} 님`,
      rating: 5,
      product: prodSelect.options[prodSelect.selectedIndex].text,
      content: contentInput.value
    };

    reviews.unshift(newRev);
    renderReviews("all");
    overlay.classList.remove("active");
    form.reset();
    showToast("리얼후기가 성공적으로 등록되었습니다!");
  });
}

// Toast Helper
function showToast(message) {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
    <span>${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentNode) toast.parentNode.removeChild(toast);
  }, 3000);
}
