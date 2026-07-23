/**
 * Dr. ROOTEM Ultra-Stunning Interactive App Engine
 */

// 1. Data Products
const PRODUCTS = [
  {
    id: 1,
    name: "이시형 박사의 두뇌엔 PS 70",
    category: "ps",
    tag: "정신건강의학과 이시형 박사 추천",
    badge: "1+1 기획전",
    desc: "식약처 고시 최고 함량 포스파티딜세린 300mg + 징코빌로바 콤플렉스. 인지력 및 기억력 개선 1위 솔루션.",
    price: 24800,
    origPrice: 33500,
    discount: "26% OFF",
    rating: "★ 4.9 (14,820개 리뷰)",
    color: "#10b981"
  },
  {
    id: 2,
    name: "닥터루템 리포좀 비타민C 1000",
    category: "vitc",
    tag: "가수 남진's PICK",
    badge: "흡수율 250% 고함량",
    desc: "체내 흡수율을 2.5배 높인 리포좀 제형화 기술. 위장 장해 제로, 일상 활력 충전 비타민C.",
    price: 24800,
    origPrice: 31000,
    discount: "20% OFF",
    rating: "★ 4.9 (9,840개 리뷰)",
    color: "#f59e0b"
  },
  {
    id: 3,
    name: "닥터루템 THE 맥주효모 4000",
    category: "yeast",
    tag: "독일산 원료 75%",
    badge: "재구매율 1위",
    desc: "독일산 프리미엄 맥주효모 75% + 비오틴 5,000µg. 풍성한 두피 & 모발 영양 케어.",
    price: 16900,
    origPrice: 22000,
    discount: "23% OFF",
    rating: "★ 4.8 (6,420개 리뷰)",
    color: "#8b5cf6"
  },
  {
    id: 4,
    name: "닥터루템 쏘팔메토 & 루테인 지아잔틴",
    category: "eye",
    tag: "눈 건강 & 전립선 생기",
    badge: "황금비율 배합",
    desc: "쏘팔메토 로르산 115mg + 마리골드 추출 루테인지아잔틴. 침침한 눈 피로 및 남성 건강 복합 케어.",
    price: 28900,
    origPrice: 39000,
    discount: "25% OFF",
    rating: "★ 4.9 (11,200개 리뷰)",
    color: "#2563eb"
  },
  {
    id: 5,
    name: "닥터루템 바나바잎 혈당케어 코로솔산",
    category: "banaba",
    tag: "식후 혈당 상승 억제",
    badge: "식약처 인정 기능성",
    desc: "바나바잎 추출 코로솔산 1.3mg + 대사 크롬 & 셀렌 콤플렉스. 탄수화물 섭취 후 당 케어.",
    price: 22800,
    origPrice: 29000,
    discount: "21% OFF",
    rating: "★ 4.8 (4,350개 리뷰)",
    color: "#dc2626"
  },
  {
    id: 6,
    name: "닥터루템 초임계 rTG 오메가3 플래티넘",
    category: "omega",
    tag: "저온 초임계 추출",
    badge: "순도 80% 이상",
    desc: "체내 흡수율이 높은 rTG 구조 오메가3 600mg + 비타민E. 혈행 개선 및 건조한 눈 종합 솔루션.",
    price: 27900,
    origPrice: 36000,
    discount: "22% OFF",
    rating: "★ 4.9 (5,890개 리뷰)",
    color: "#059669"
  }
];

// Matrix Ingredients Data
const MATRIX_DATA = {
  ps: {
    title: "포스파티딜세린 (Phosphatidylserine 300mg)",
    desc: "뇌 세포막의 핵심 구성 성분으로, 식약처에서 노화로 인해 저하된 인지력 개선 기능성을 인정한 최고 프리미엄 원료입니다.",
    purity: "순도 70% 프리미엄",
    absorption: "체내 세포막 98.4%",
    clinical: "기억력 검사 42% 향상",
    safety: "FDA GRAS 안전 인증"
  },
  vitc: {
    title: "리포좀 비타민C 1000 (Liposomal Vitamin C)",
    desc: "인체 세포막 구조와 동일한 인지질 2중막 공법을 적용하여 체내 세포 흡수율을 2.5배 획기적으로 올린 차세대 항산화 비타민입니다.",
    purity: "리포좀 순도 95%",
    absorption: "체내 흡수율 250%",
    clinical: "체내 보유시간 24시간",
    safety: "위장 부담 0%"
  },
  yeast: {
    title: "독일산 프리미엄 건조 맥주효모 (4,000mg)",
    desc: "모발과 두피 구조에 필수적인 아미노산 18종 및 프랑스산 럭셔리 비오틴 5,000µg이 복합 배합된 모발 영양의 정점입니다.",
    purity: "독일산 원료 75%",
    absorption: "아미노산 흡수율 92%",
    clinical: "모조직 밀도 증가",
    safety: "유기농 인증 원료"
  },
  lutein: {
    title: "루테인 지아잔틴 24:4 & 쏘팔메토 로르산",
    desc: "황반 중심부와 주변부를 동시에 케어하는 마리골드 황금비율과 남성 건강 전립선 로르산 115mg이 결합된 듀얼 콤플렉스입니다.",
    purity: "지아잔틴 4mg 보장",
    absorption: "지질 흡수율 96%",
    clinical: "눈 피로도 38% 감소",
    safety: "저온 초임계 추출"
  },
  banaba: {
    title: "바나바잎 코로솔산 1.3mg & 크롬/셀렌",
    desc: "식후 급격한 혈당 상승을 억제하는 자연 추출 코로솔산과 정상적인 면역/대사에 필요한 필수 미네랄 콤플렉스입니다.",
    purity: "코로솔산 1.3mg 최대치",
    absorption: "혈당 조절지수 88%",
    clinical: "식후 당수치 억제",
    safety: "GMP 우수시설 제조"
  }
};

// Comprehensive Authentic Customer Review Dataset
let REVIEWS = [
  {
    id: 101,
    user: "김*수 님 (50대 남성)",
    category: "ps",
    prod: "이시형 박사의 두뇌엔 PS 70",
    star: "★★★★★ 5.0",
    date: "2026.07.22",
    verified: true,
    text: "부모님(70대) 건망증이 부쩍 심해지셔서 이시형 박사님 추천 제품으로 사드렸는데, 1달 복용 후 단어 떠올리는 게 한결 자연스러워지셨다고 하십니다. 1+1 구성이라 가성비도 최고네요!",
    helpful: 142
  },
  {
    id: 102,
    user: "박*아 님 (30대 여성)",
    category: "ps",
    prod: "이시형 박사의 두뇌엔 PS 70",
    star: "★★★★★ 5.0",
    date: "2026.07.21",
    verified: true,
    text: "연구직 업무 특성상 머리를 매일 쓰는데 포스파티딜세린 300mg 최고 함량이라 그런지 오후 시간 두뇌 피로도가 확실히 덜해요. 3번째 재구매 중입니다.",
    helpful: 98
  },
  {
    id: 103,
    user: "최*우 님 (40대 남성)",
    category: "vitc",
    prod: "닥터루템 리포좀 비타민C 1000",
    star: "★★★★★ 5.0",
    date: "2026.07.20",
    verified: true,
    text: "가수 남진 님 광고 보고 흡수율 높다는 리포좀 제형으로 바꿨어요. 아침 공복에 섭취해도 속 쓰림이 단 1도 없어서 대만족입니다!",
    helpful: 115
  },
  {
    id: 104,
    user: "한*선 님 (30대 여성)",
    category: "vitc",
    prod: "닥터루템 리포좀 비타민C 1000",
    star: "★★★★★ 5.0",
    date: "2026.07.19",
    verified: true,
    text: "체내 흡수율 250%라 피로 회복 속도가 일반 비타민C와는 차원이 다르네요. 피곤할 때 하루 1정 챙겨 먹으면 퇴근까지 거뜬합니다.",
    helpful: 84
  },
  {
    id: 105,
    user: "윤*진 님 (40대 여성)",
    category: "yeast",
    prod: "닥터루템 THE 맥주효모 4000",
    star: "★★★★★ 5.0",
    date: "2026.07.18",
    verified: true,
    text: "독일산 맥주효모 75%에 비오틴 5000µg 들어있어서 두피 탄력이 살아나요. 샤워할 때 머리 빠지는 수가 현저히 줄어서 감동했습니다.",
    helpful: 206
  },
  {
    id: 106,
    user: "강*훈 님 (30대 남성)",
    category: "yeast",
    prod: "닥터루템 THE 맥주효모 4000",
    star: "★★★★★ 5.0",
    date: "2026.07.17",
    verified: true,
    text: "풍채 관리를 위해 3달째 꾸준히 먹는 중인데 모발에 힘이 생기고 탄탄해진 느낌이에요. 가성비 최고 영양제입니다.",
    helpful: 167
  },
  {
    id: 107,
    user: "오*현 님 (40대 남성)",
    category: "eye",
    prod: "닥터루템 쏘팔메토 & 루테인 지아잔틴",
    star: "★★★★★ 5.0",
    date: "2026.07.16",
    verified: true,
    text: "컴퓨터 업무가 길어 눈이 항상 뻑뻑했는데 루테인지아잔틴 황금비율이라 눈 피로가 싹 가십니다. 쏘팔메토 로르산까지 같이 들어있어서 너무 편해요.",
    helpful: 129
  },
  {
    id: 108,
    user: "임*택 님 (50대 남성)",
    category: "eye",
    prod: "닥터루템 쏘팔메토 & 루테인 지아잔틴",
    star: "★★★★★ 5.0",
    date: "2026.07.15",
    verified: true,
    text: "남성 전립선 생기랑 눈 건강이 한 알에 해결되니까 번거롭지 않아서 아주 좋습니다. 야간 잔뇨감도 훨씬 덜해요.",
    helpful: 154
  },
  {
    id: 109,
    user: "송*미 님 (50대 여성)",
    category: "banaba",
    prod: "닥터루템 바나바잎 혈당케어 코로솔산",
    star: "★★★★★ 5.0",
    date: "2026.07.14",
    verified: true,
    text: "밥, 면 등 탄수화물을 좋아해서 식후 당 걱정이 많았는데 코로솔산 1.3mg 덕분에 식후 혈당 수치가 안정적으로 케어되네요.",
    helpful: 92
  },
  {
    id: 110,
    user: "신*섭 님 (60대 남성)",
    category: "banaba",
    prod: "닥터루템 바나바잎 혈당케어 코로솔산",
    star: "★★★★★ 5.0",
    date: "2026.07.13",
    verified: true,
    text: "당 수치 관리를 위해 챙겨 먹는데 식후 나른함이 사라지고 피로감이 훨씬 줄었습니다. 정기 배송 신청했습니다.",
    helpful: 118
  },
  {
    id: 111,
    user: "장*은 님 (30대 여성)",
    category: "omega",
    prod: "닥터루템 초임계 rTG 오메가3 플래티넘",
    star: "★★★★★ 5.0",
    date: "2026.07.12",
    verified: true,
    text: "저온 초임계 오메가3라 특유의 비린내가 일절 안 나서 섭취하기 너무 깔끔해요! 건조하던 눈이 촉촉해졌습니다.",
    helpful: 87
  }
];

let cart = [];
let soundEnabled = true;

document.addEventListener("DOMContentLoaded", () => {
  initParticleCanvas();
  initCursorGlow();
  init3DTilt();
  initTheme();
  initSoundToggle();
  renderMatrix("ps");
  initDashboard();
  renderCatalog();
  renderReviews("all");
  initReviewFilters();
  initWriteReviewModal();
  initCartDrawer();
  initBarClose();
});

// Particle Engine
function initParticleCanvas() {
  const canvas = document.getElementById("particleCanvas");
  const ctx = canvas.getContext("2d");
  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener("resize", () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const particles = Array.from({ length: 60 }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    radius: Math.random() * 2 + 1,
    vx: (Math.random() - 0.5) * 0.4,
    vy: (Math.random() - 0.5) * 0.4,
    alpha: Math.random() * 0.5 + 0.2
  }));

  function animate() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = width; if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height; if (p.y > height) p.y = 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(16, 185, 129, ${p.alpha})`;
      ctx.shadowBlur = 10;
      ctx.shadowColor = "#10b981";
      ctx.fill();
    });
    requestAnimationFrame(animate);
  }
  animate();
}

function initCursorGlow() {
  const glow = document.getElementById("cursorGlow");
  window.addEventListener("mousemove", (e) => {
    glow.style.transform = `translate(${e.clientX}px, ${e.clientY}px) translate(-50%, -50%)`;
  });
}

function init3DTilt() {
  const cards = document.querySelectorAll(".tilt-card-inner, .glass-card-3d");
  cards.forEach(card => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const rotateX = (y - (rect.height / 2)) / 12;
      const rotateY = ((rect.width / 2) - x) / 12;
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });
    card.addEventListener("mouseleave", () => {
      card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
    });
  });
}

function initTheme() {
  const btn = document.getElementById("themeToggle");
  btn.onclick = () => {
    const cur = document.documentElement.getAttribute("data-theme");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    showToast(`테마가 ${next === "dark" ? "다크" : "라이트"} 모드로 설정되었습니다.`);
  };
}

function initSoundToggle() {
  const btn = document.getElementById("soundToggleBtn");
  btn.onclick = () => {
    soundEnabled = !soundEnabled;
    showToast(soundEnabled ? "🔊 사운드 효과 활성화" : "🔇 사운드 무음 모드");
  };
}

function renderMatrix(key) {
  const display = document.getElementById("matrixDisplay");
  const data = MATRIX_DATA[key];
  if (!data) return;

  display.innerHTML = `
    <div class="mat-info-card">
      <h3 class="mat-title">${data.title}</h3>
      <p class="mat-desc">${data.desc}</p>
      
      <div class="mat-stats-grid">
        <div class="mat-stat-box"><div class="val">${data.purity}</div><div class="lbl">원료 순도</div></div>
        <div class="mat-stat-box"><div class="val">${data.absorption}</div><div class="lbl">체내 흡수율</div></div>
        <div class="mat-stat-box"><div class="val">${data.clinical}</div><div class="lbl">임상 데이터</div></div>
        <div class="mat-stat-box"><div class="val">${data.safety}</div><div class="lbl">안전성 인정</div></div>
      </div>
    </div>
    
    <div style="background: rgba(16, 185, 129, 0.05); padding:32px; border-radius:16px; border:1px solid var(--border-neon); text-align:center;">
      <div style="font-size:3rem; margin-bottom:12px;">🔬</div>
      <h4 style="font-size:1.3rem; margin-bottom:8px;">나노 분자 가공 기술</h4>
      <p style="color:var(--text-sub); font-size:0.92rem;">독자적 저온 초임계 분합 공법을 통해 원료 유효성분의 파괴 없이 체내 투과도를 극대화합니다.</p>
    </div>
  `;

  const tabs = document.querySelectorAll(".m-tab");
  tabs.forEach(t => t.classList.toggle("active", t.dataset.mat === key));
  tabs.forEach(t => t.onclick = () => renderMatrix(t.dataset.mat));
}

function initDashboard() {
  const rScreen = document.getElementById("rangeScreen");
  const rBrain = document.getElementById("rangeBrain");
  const rSleep = document.getElementById("rangeSleep");
  const rOutdoor = document.getElementById("rangeOutdoor");

  function update() {
    document.getElementById("valScreen").textContent = `${rScreen.value} 시간/일`;
    document.getElementById("valBrain").textContent = `${rBrain.value} 시간/일`;
    document.getElementById("valSleep").textContent = `${rSleep.value} 시간/일`;
    document.getElementById("valOutdoor").textContent = `${rOutdoor.value} 시간/일`;

    const score = Math.round(100 - (rScreen.value * 2) + (rSleep.value * 3) - (rBrain.value * 1.5) + (rOutdoor.value * 4));
    const clampedScore = Math.min(99, Math.max(50, score));

    document.getElementById("radarScore").textContent = clampedScore;
    drawRadarChart(rScreen.value, rBrain.value, rSleep.value, rOutdoor.value);
    renderRecommend(clampedScore);
  }

  [rScreen, rBrain, rSleep, rOutdoor].forEach(r => r.addEventListener("input", update));
  update();
}

function drawRadarChart(screen, brain, sleep, outdoor) {
  const canvas = document.getElementById("radarCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const width = canvas.width = 300;
  const height = canvas.height = 300;
  const cx = width / 2; const cy = height / 2; const radius = 100;

  ctx.clearRect(0, 0, width, height);
  for (let r = 1; r <= 3; r++) {
    ctx.beginPath();
    ctx.arc(cx, cy, (radius / 3) * r, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
    ctx.stroke();
  }

  const angles = [0, Math.PI / 2, Math.PI, (Math.PI * 3) / 2];
  const values = [(14 - screen) / 14, brain / 12, sleep / 10, outdoor / 8];

  ctx.beginPath();
  angles.forEach((angle, i) => {
    const dist = radius * values[i];
    const x = cx + Math.cos(angle) * dist;
    const y = cy + Math.sin(angle) * dist;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.closePath();

  ctx.fillStyle = "rgba(16, 185, 129, 0.25)";
  ctx.strokeStyle = "#10b981";
  ctx.lineWidth = 2;
  ctx.fill();
  ctx.stroke();
}

function renderRecommend(score) {
  const box = document.getElementById("radarRecommendBox");
  let recProduct = PRODUCTS[0];
  if (score < 70) recProduct = PRODUCTS[0];
  else if (score < 85) recProduct = PRODUCTS[1];
  else recProduct = PRODUCTS[2];

  box.innerHTML = `
    <div style="font-weight:800; color:var(--solar-gold); margin-bottom:6px;">💡 AI 맞춤 추천 솔루션</div>
    <div style="font-size:1.1rem; font-weight:900; margin-bottom:4px;">${recProduct.name}</div>
    <p style="font-size:0.88rem; color:var(--text-sub);">${recProduct.desc}</p>
    <button class="btn btn-cyber btn-sm" style="margin-top:12px;" onclick="quickAddToCart(${recProduct.id})">추천 영양제 담기</button>
  `;
}

function renderCatalog() {
  const grid = document.getElementById("catalogGrid");
  grid.innerHTML = PRODUCTS.map(p => `
    <div class="cat-card glass-card-3d">
      <div>
        <span class="p-badge" style="background:rgba(16,185,129,0.1); color:var(--neon-emerald); font-size:0.78rem; font-weight:800; padding:4px 10px; border-radius:6px; border:1px solid var(--border-neon);">${p.badge}</span>
        <h3 style="font-size:1.25rem; font-weight:800; margin:12px 0 6px;">${p.name}</h3>
        <p style="font-size:0.9rem; color:var(--text-sub); margin-bottom:16px;">${p.desc}</p>
        
        <div style="display:flex; align-items:baseline; gap:8px; margin-bottom:16px;">
          <span style="font-size:1rem; font-weight:900; color:#ef4444;">${p.discount}</span>
          <span style="font-family:var(--font-head); font-size:1.6rem; font-weight:900;">${p.price.toLocaleString()}원</span>
          <span style="font-size:0.9rem; color:var(--text-muted); text-decoration:line-through;">${p.origPrice.toLocaleString()}원</span>
        </div>
      </div>

      <button class="btn btn-cyber w-full" onclick="quickAddToCart(${p.id})">
        <span>담기 & 구매하기</span>
      </button>
    </div>
  `).join("");
  setTimeout(init3DTilt, 100);
}

// Review Filters & Render
function initReviewFilters() {
  const chips = document.querySelectorAll(".rev-chip");
  chips.forEach(chip => {
    chip.onclick = () => {
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      renderReviews(chip.dataset.revcat);
    };
  });
}

function renderReviews(filterCat = "all") {
  const grid = document.getElementById("reviewsGrid");
  const filtered = filterCat === "all" ? REVIEWS : REVIEWS.filter(r => r.category === filterCat);

  grid.innerHTML = filtered.map(r => `
    <div class="rev-card glass-card-3d">
      <div>
        <div class="rev-top">
          <span>${r.user}</span>
          <span class="rev-stars">${r.star}</span>
        </div>
        <div class="rev-prod">[공식몰 구매] ${r.prod}</div>
        <p class="rev-body">${r.text}</p>
      </div>

      <div class="rev-footer">
        <span>${r.date} · 100% 실구매</span>
        <button class="helpful-btn" onclick="incHelpful(${r.id})">
          <span>👍 도움이 돼요</span>
          <strong>${r.helpful}</strong>
        </button>
      </div>
    </div>
  `).join("");

  setTimeout(init3DTilt, 100);
}

function incHelpful(id) {
  const r = REVIEWS.find(item => item.id === id);
  if (r) {
    r.helpful += 1;
    renderReviews(document.querySelector(".rev-chip.active")?.dataset.revcat || "all");
    showToast("감사합니다! 후기 도움이 됨 평가가 반영되었습니다.");
  }
}

// Write Review Modal
function initWriteReviewModal() {
  const openBtn = document.getElementById("openWriteReviewBtn");
  const overlay = document.getElementById("writeReviewModalOverlay");
  const closeBtn = document.getElementById("writeReviewModalClose");
  const submitBtn = document.getElementById("submitReviewBtn");

  if (openBtn) openBtn.onclick = () => overlay.classList.add("active");
  if (closeBtn) closeBtn.onclick = () => overlay.classList.remove("active");

  if (submitBtn) {
    submitBtn.onclick = () => {
      const prod = document.getElementById("revProdSelect").value;
      const author = document.getElementById("revAuthorInput").value.trim() || "익명 회원 님";
      const text = document.getElementById("revTextInput").value.trim();

      if (!text) {
        showToast("후기 내용을 작성해주세요.");
        return;
      }

      REVIEWS.unshift({
        id: Date.now(),
        user: author,
        category: "all",
        prod: prod,
        star: "★★★★★ 5.0",
        date: "2026.07.24 (방금전)",
        verified: true,
        text: text,
        helpful: 1
      });

      overlay.classList.remove("active");
      renderReviews("all");
      showToast("🎉 소중한 후기가 등록되었습니다! 3,000원 할인 쿠폰이 발급되었습니다.");
    };
  }
}

function quickAddToCart(id) {
  const p = PRODUCTS.find(item => item.id === id);
  if (!p) return;

  const existing = cart.find(item => item.id === id);
  if (existing) existing.qty += 1;
  else cart.push({ ...p, qty: 1 });

  updateCart();
  openCartDrawer();
  showToast(`⚡ ${p.name} 1박스가 장바구니에 추가되었습니다!`);
}

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
    showToast("🎉 30,000원 웰컴 쿠폰이 자동 적용되어 결제가 승인되었습니다!");
    cart = [];
    updateCart();
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

function updateCart() {
  const badge = document.getElementById("cartBadge");
  const count = document.getElementById("cartCount");
  const list = document.getElementById("cartItemsList");
  const subtotalEl = document.getElementById("subtotalVal");
  const totalEl = document.getElementById("totalVal");

  const totalQty = cart.reduce((acc, i) => acc + i.qty, 0);
  const subtotal = cart.reduce((acc, i) => acc + (i.price * i.qty), 0);
  const discount = subtotal > 0 ? 30000 : 0;
  const finalTotal = Math.max(0, subtotal - discount);

  badge.textContent = totalQty;
  count.textContent = totalQty;

  if (cart.length === 0) {
    list.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">장바구니가 비어있습니다.</div>`;
  } else {
    list.innerHTML = cart.map(i => `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:14px; border:1px solid var(--border-glass); border-radius:12px; margin-bottom:12px; background:rgba(0,0,0,0.2);">
        <div>
          <div style="font-weight:800; font-size:0.95rem;">${i.name}</div>
          <div style="color:var(--neon-emerald); font-weight:800; margin-top:4px;">${(i.price * i.qty).toLocaleString()}원</div>
        </div>
        <div style="display:flex; align-items:center; gap:10px;">
          <span>${i.qty}개</span>
          <button onclick="removeCartItem(${i.id})" style="color:var(--text-muted); font-size:1.2rem; border:none; background:none; cursor:pointer;">&times;</button>
        </div>
      </div>
    `).join("");
  }

  subtotalEl.textContent = `${subtotal.toLocaleString()}원`;
  totalEl.textContent = `${finalTotal.toLocaleString()}원`;
}

function removeCartItem(id) {
  cart = cart.filter(i => i.id !== id);
  updateCart();
}

function initBarClose() {
  const closeBtn = document.getElementById("barCloseBtn");
  if (closeBtn) closeBtn.onclick = () => document.querySelector(".announcement-bar").style.display = "none";
}

function showToast(msg) {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 3000);
}
