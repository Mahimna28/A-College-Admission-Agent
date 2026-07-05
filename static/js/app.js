/**
 * app.js  –  College Admission Agent Frontend
 * Handles: chat UI, course explorer, eligibility, dashboard, deadlines, profile
 */

"use strict";

// ─── Helpers ────────────────────────────────────────────────────────────────

const $  = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
const esc = str => String(str).replace(/[&<>"']/g, c =>
  ({ "&": "&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" })[c]);

function showToast(msg, type = "success") {
  const existing = $("#liveToast");
  if (existing) existing.remove();

  const colours = { success:"#10b981", danger:"#ef4444", warning:"#f59e0b", info:"#0ea5e9" };
  const toast = document.createElement("div");
  toast.id = "liveToast";
  toast.style.cssText = `
    position:fixed; bottom:24px; right:24px; z-index:9999;
    background:var(--bg-card); border:1px solid var(--border);
    border-left:4px solid ${colours[type]||colours.info};
    border-radius:10px; padding:.85rem 1.2rem;
    font-size:.875rem; box-shadow:var(--shadow-lg);
    animation:fadeUp .3s ease;
    max-width:360px; color:var(--text);
  `;
  toast.innerHTML = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// ─── Theme Toggle ────────────────────────────────────────────────────────────

(function initTheme() {
  const saved = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", saved);
  updateThemeIcon(saved);
})();

function updateThemeIcon(theme) {
  const btn = $("#themeToggle");
  if (!btn) return;
  btn.innerHTML = theme === "dark"
    ? '<i class="bi bi-sun-fill"></i>'
    : '<i class="bi bi-moon-stars-fill"></i>';
}

document.addEventListener("DOMContentLoaded", () => {
  $("#themeToggle")?.addEventListener("click", () => {
    const cur  = document.documentElement.getAttribute("data-theme");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    updateThemeIcon(next);
  });
});

// ─── Scroll Reveal ───────────────────────────────────────────────────────────

function initReveal() {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add("visible");
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  $$(".section-pad, .stat-card, .course-card, .deadline-card").forEach(el => {
    el.classList.add("reveal");
    observer.observe(el);
  });
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

async function loadDashboard() {
  try {
    const res  = await fetch("/api/dashboard");
    const data = await res.json();

    // Animated counters
    animateCounter("statTotal",  data.stats.total_programs);
    animateCounter("statUG",     data.stats.undergraduate);
    animateCounter("statGrad",   data.stats.graduate);
    animateCounter("statRounds", data.application_rounds.length);

    // Flagship programmes
    const fl = $("#flagshipList");
    if (fl && data.flagship_programs) {
      fl.innerHTML = data.flagship_programs
        .map(p => `<div class="flagship-item">
          <i class="bi bi-check-circle-fill text-success"></i>
          <span>${esc(p)}</span>
        </div>`).join("");
    }

    // Test benchmarks
    const tb = $("#testBenchmarks");
    if (tb && data.accepted_tests) {
      tb.innerHTML = Object.entries(data.accepted_tests).map(([test, v]) => {
        const pct = Math.round((v.competitive - v.min) / (v.max - v.min) * 100);
        return `<div class="test-row">
          <strong>${esc(test)}</strong>
          <span class="text-muted small">min: ${v.min} · competitive: ${v.competitive}</span>
          <div class="test-bar"><div class="test-bar-fill" style="width:${pct}%"></div></div>
        </div>`;
      }).join("");
    }
  } catch (err) {
    console.error("Dashboard load failed:", err);
  }
}

function animateCounter(id, target) {
  const el = document.getElementById(id);
  if (!el) return;
  let cur = 0;
  const step = Math.ceil(target / 30);
  const interval = setInterval(() => {
    cur = Math.min(cur + step, target);
    el.textContent = cur;
    if (cur >= target) clearInterval(interval);
  }, 40);
}

// ─── Course Explorer ─────────────────────────────────────────────────────────

let allCourses = [];
let currentModal = null;

async function loadCourses(level = "", q = "") {
  const grid = $("#courseGrid");
  if (!grid) return;
  grid.innerHTML = `<div class="col-12 text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>`;

  const params = new URLSearchParams();
  if (level) params.set("level", level);
  if (q)     params.set("q", q);

  const res   = await fetch(`/api/courses?${params}`);
  const data  = await res.json();
  allCourses  = data.courses;

  const countEl = $("#courseCount");
  if (countEl) countEl.textContent = `${data.total} programme${data.total !== 1 ? "s" : ""}`;

  if (!data.courses.length) {
    grid.innerHTML = `<div class="col-12"><div class="empty-state"><i class="bi bi-search display-4"></i><p class="mt-3">No programmes match your search.</p></div></div>`;
    return;
  }

  grid.innerHTML = data.courses.map((c, i) => `
    <div class="col-md-6 col-xl-4">
      <div class="course-card" data-idx="${i}" style="animation-delay:${i * 60}ms">
        <span class="course-card-badge ${c.level === "Graduate" ? "badge-grad" : "badge-ug"}">${esc(c.level)}</span>
        <h6>${esc(c.name)}</h6>
        <p>${esc(c.description)}</p>
        <div class="course-meta">
          <span><i class="bi bi-clock"></i> ${esc(c.duration)}</span>
          <span><i class="bi bi-currency-dollar"></i> $${(c.tuition_usd_per_year || 0).toLocaleString()}/yr</span>
          <span><i class="bi bi-bar-chart"></i> GPA ≥ ${c.min_gpa}</span>
        </div>
        <button class="btn btn-sm btn-outline-primary mt-3 w-100">
          <i class="bi bi-info-circle me-1"></i>View Details
        </button>
      </div>
    </div>
  `).join("");

  $$(".course-card").forEach(card => {
    card.addEventListener("click", () => openCourseModal(parseInt(card.dataset.idx)));
  });
}

function openCourseModal(idx) {
  const c   = allCourses[idx];
  if (!c) return;
  const el  = document.getElementById("courseModalTitle");
  const body = document.getElementById("courseModalBody");
  if (!el || !body) return;

  el.textContent = c.name;
  const paths = (c.career_paths || []).map(p => `<span class="badge bg-primary-soft text-primary me-1">${esc(p)}</span>`).join("");
  const tests = Object.entries(c.min_test_score || {}).map(([t, s]) => `${t}: ${s}`).join(", ") || "N/A";

  body.innerHTML = `
    <div class="row g-4">
      <div class="col-md-6">
        <p><strong>Level:</strong> ${esc(c.level)}</p>
        <p><strong>Duration:</strong> ${esc(c.duration)}</p>
        <p><strong>Minimum GPA:</strong> ${c.min_gpa} / 4.0</p>
        <p><strong>Required Tests:</strong> ${(c.required_tests || []).join(", ")}</p>
        <p><strong>Min Test Scores:</strong> ${tests}</p>
        <p><strong>Tuition:</strong> $${(c.tuition_usd_per_year || 0).toLocaleString()} per year</p>
      </div>
      <div class="col-md-6">
        <p><strong>Description:</strong></p>
        <p class="text-muted">${esc(c.description)}</p>
        <p class="mt-3"><strong>Career Paths:</strong></p>
        <div>${paths}</div>
      </div>
    </div>
  `;

  currentModal = c.name;
  const modal = new bootstrap.Modal(document.getElementById("courseModal"));
  modal.show();
}

document.addEventListener("DOMContentLoaded", () => {
  // Level filter buttons
  $$("[data-level]").forEach(btn => {
    btn.addEventListener("click", () => {
      $$("[data-level]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      loadCourses(btn.dataset.level, $("#courseSearch")?.value || "");
    });
  });

  // Search input (debounced)
  let searchTimer;
  $("#courseSearch")?.addEventListener("input", e => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      const level = $("[data-level].active")?.dataset.level || "";
      loadCourses(level, e.target.value);
    }, 380);
  });

  // Modal chat button
  $("#courseModalChat")?.addEventListener("click", () => {
    if (currentModal) {
      const q = `Tell me more about the ${currentModal} programme — entry requirements, curriculum highlights, and career outcomes.`;
      bootstrap.Modal.getInstance(document.getElementById("courseModal"))?.hide();
      setTimeout(() => {
        document.getElementById("chatInput").value = q;
        document.getElementById("chat").scrollIntoView({ behavior: "smooth" });
      }, 300);
    }
  });
});

// ─── Eligibility Checker ─────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("eligibilityForm");
  if (!form) return;

  form.addEventListener("submit", async e => {
    e.preventDefault();
    const gpa = parseFloat(document.getElementById("elGpa").value);
    if (!gpa) {
      showToast("Please enter your GPA.", "warning"); return;
    }

    const payload = {
      gpa,
      education_level: document.getElementById("elLevel").value,
      test_scores: {
        SAT:   document.getElementById("scoreSAT").value   || null,
        ACT:   document.getElementById("scoreACT").value   || null,
        GRE:   document.getElementById("scoreGRE").value   || null,
        GMAT:  document.getElementById("scoreGMAT").value  || null,
        TOEFL: document.getElementById("scoreTOEFL").value || null,
        IELTS: document.getElementById("scoreIELTS").value || null,
      },
    };

    const btn = form.querySelector("button[type=submit]");
    btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Analysing…`;
    btn.disabled = true;

    try {
      const res  = await fetch("/api/eligibility", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload) });
      const data = await res.json();
      renderEligibility(data);
    } catch(err) {
      showToast("Eligibility check failed. Please try again.", "danger");
    } finally {
      btn.innerHTML = `<i class="bi bi-search-heart me-2"></i>Check My Eligibility`;
      btn.disabled = false;
    }
  });
});

function renderEligibility(data) {
  const container = document.getElementById("eligibilityResults");
  if (!container) return;

  const { eligible=[], borderline=[], ineligible=[], summary={} } = data;
  const gpaColor = summary.gpa >= summary.competitive_gpa ? "success" : (summary.gpa >= summary.min_required ? "warning" : "danger");

  let html = `
    <div class="elig-summary-bar">
      <span class="elig-summary-pill bg-success-soft text-success">${eligible.length} Eligible</span>
      <span class="elig-summary-pill bg-warning-soft" style="color:#92400e">${borderline.length} Borderline</span>
      <span class="elig-summary-pill bg-danger-soft text-danger">${ineligible.length} Ineligible</span>
    </div>
    <div class="mb-3 p-3 rounded" style="background:var(--bg-surface);border:1px solid var(--border)">
      <strong>Your GPA:</strong> ${summary.gpa}
      <span class="ms-2 badge bg-${gpaColor}-soft text-${gpaColor}">${summary.gpa >= summary.competitive_gpa ? "Strong 🎉" : summary.gpa >= summary.min_required ? "Acceptable" : "Below Minimum"}</span>
    </div>`;

  if (eligible.length) {
    html += `<div class="elig-group-header text-success"><i class="bi bi-check-circle-fill me-1"></i>Eligible Programmes</div>`;
    html += eligible.map(c => elig_item(c, "eligible")).join("");
  }
  if (borderline.length) {
    html += `<div class="elig-group-header text-warning"><i class="bi bi-exclamation-circle-fill me-1"></i>Borderline (needs improvement)</div>`;
    html += borderline.map(c => elig_item(c, "borderline")).join("");
  }
  if (ineligible.length) {
    html += `<div class="elig-group-header text-danger"><i class="bi bi-x-circle-fill me-1"></i>Not Currently Eligible</div>`;
    html += ineligible.map(c => elig_item(c, "ineligible")).join("");
  }

  html += `<button class="btn btn-primary w-100 mt-3" onclick="askAIEligibility()">
    <i class="bi bi-chat-dots me-2"></i>Get AI Guidance for My Profile
  </button>`;

  container.innerHTML = html;
}

function elig_item(c, status) {
  return `<div class="elig-item elig-${status}">
    <span>${esc(c.name)}</span>
    <span class="badge bg-${status==="eligible"?"success":status==="borderline"?"warning":"danger"}-soft
      text-${status==="eligible"?"success":status==="borderline"?"warning":"danger"}">
      ${status.charAt(0).toUpperCase()+status.slice(1)}
    </span>
  </div>`;
}

function askAIEligibility() {
  const gpa = document.getElementById("elGpa").value;
  const sat = document.getElementById("scoreSAT").value;
  const gre = document.getElementById("scoreGRE").value;
  const msg = `Based on my profile — GPA: ${gpa}${sat?`, SAT: ${sat}`:""}${gre?`, GRE: ${gre}`:""} — which programmes should I focus on and what can I do to improve my chances?`;
  document.getElementById("chatInput").value = msg;
  document.getElementById("chat").scrollIntoView({ behavior:"smooth" });
  document.getElementById("chatInput").focus();
}

// ADD THIS AFTER LINE 348
function getFallbackResponse(query) {
  const q = query.toLowerCase();
  
  if (q.includes("eligibility") || q.includes("qualify") || q.includes("cutoff") || q.includes("report")) {
    return `📋 **Eligibility Quick Guide**

• **B.Tech CSE**: 75% in 12th (PCM) + JEE Main 120+
• **B.Tech AI & DS**: 70% in 12th + JEE Main 100+
• **BBA**: 60% in 12th (any stream)
• **MBBS**: 80% in 12th (PCB) + NEET 400+

**Reservation**: SC/ST/OBC/EWS quotas as per Govt. of India norms.
**Scholarships**: Merit-based for JEE Main 200+ scorers.

Use the **Eligibility Checker** below for a detailed personalized report!`;
  }
  
  else if (q.includes("course") || q.includes("program") || q.includes("b.tech") || q.includes("mbbs")) {
    return `🎓 **Our Programmes**

• **B.Tech CSE** — ₹2,50,000/year | JEE Main required
• **B.Tech AI & DS** — ₹2,80,000/year | JEE Main required  
• **B.Tech ECE** — ₹2,20,000/year | JEE Main/MHT-CET
• **BBA** — ₹1,50,000/year | Direct admission
• **MBBS** — ₹8,00,000/year | NEET required
• **M.Tech CSE** — ₹2,00,000/year | GATE required
• **MBA** — ₹4,00,000/year | CAT/MAT

Browse the **Course Explorer** for full details!`;
  }
  
  else if (q.includes("deadline") || q.includes("date") || q.includes("last date")) {
    return `📅 **Important Dates**

• **Round 1**: May 1
• **Round 2**: June 15  
• **Spot Round**: July 30
• **Management Quota**: Aug 1 - Aug 15

Don't miss the deadlines! Check the **Deadlines** section for a live countdown.`;
  }
  
  else if (q.includes("fee") || q.includes("cost") || q.includes("tuition") || q.includes("₹")) {
    return `💰 **Fee Structure (per year)**

• **B.Tech CSE**: ₹2,50,000
• **B.Tech AI & DS**: ₹2,80,000
• **B.Tech ECE**: ₹2,20,000
• **BBA**: ₹1,50,000
• **MBBS**: ₹8,00,000
• **M.Tech**: ₹2,00,000
• **MBA**: ₹4,00,000

**Hostel**: ₹60,000/year (mess included)
**Scholarships**: Up to 100% fee waiver for merit students!`;
  }
  
  else if (q.includes("scholarship") || q.includes("financial aid")) {
    return `🎁 **Scholarship Opportunities**

• **100% Fee Waiver**: JEE Main 250+ | NEET 600+
• **50% Fee Waiver**: JEE Main 200+ | NEET 500+
• **State Scholarships**: Available for SC/ST/OBC students
• **Minority Scholarships**: As per state government norms

Apply before **July 15**! Contact our Financial Aid Office for details.`;
  }
  
  else if (q.includes("document") || q.includes("required") || q.includes("need")) {
    return `📄 **Required Documents**

1. 10th Marksheet
2. 12th Marksheet  
3. Entrance Exam Scorecard (JEE/NEET/CET)
4. Caste Certificate (if applicable)
5. Domicile Certificate
6. Aadhaar Card
7. Passport Size Photos (6)
8. Application Fee Receipt (₹1,500)

Keep originals + 2 photocopies ready!`;
  }
  
  else {
    return `👋 **Welcome to AdmitAI!**

I'm your Indian college admission counsellor. I can help you with:

• **JEE/NEET/CET** cutoffs and eligibility
• **Course selection** (B.Tech, MBBS, BBA, MBA)
• **Fee structure** and scholarships
• **Admission deadlines** and document checklists
• **Reservation quotas** and counselling process

**Tip**: You can type your details like this:
\`name :- Aarav Sharma, 12th_percentage :- 87.5, entrance_exam :- JEE Main, entrance_score :- 156\`

Or use the **Eligibility Checker** below for instant analysis!`;
  }
}

// ─── Deadlines ───────────────────────────────────────────────────────────────

async function loadDeadlines() {
  const container = document.getElementById("deadlineCards");
  if (!container) return;

  try {
    const res  = await fetch("/api/deadlines");
    const data = await res.json();

    container.innerHTML = data.deadlines.map((d, i) => {
      const cls   = d.status === "passed" ? "d-passed" : d.status === "urgent" ? "d-urgent" : "d-upcoming";
      const icon  = d.status === "passed" ? "bi-check-lg" : d.status === "urgent" ? "bi-alarm" : "bi-calendar-check";
      const days  = d.days_remaining < 0 ? "Passed" : d.days_remaining === 0 ? "Today!" : `${d.days_remaining}d left`;
      const date  = new Date(d.date).toLocaleDateString("en-US", { month:"short", day:"numeric", year:"numeric" });

      return `<div class="col-md-6 col-xl-4">
        <div class="deadline-card ${cls}" style="animation-delay:${i*80}ms">
          <div class="deadline-icon"><i class="bi ${icon}"></i></div>
          <div class="flex-grow-1">
            <div style="font-weight:700;font-size:.95rem">${esc(d.label)}</div>
            <div class="text-muted small">${date}</div>
          </div>
          <div class="text-end">
            <div class="deadline-days">${days}</div>
            <div class="deadline-label">${d.round}</div>
          </div>
        </div>
      </div>`;
    }).join("");

  } catch(err) {
    console.error("Deadline load failed:", err);
    container.innerHTML = `<div class="col-12"><div class="empty-state text-muted"><p>Could not load deadlines.</p></div></div>`;
  }
}

// ─── Profile ─────────────────────────────────────────────────────────────────

async function loadProfile() {
  try {
    const res  = await fetch("/api/profile");
    const data = await res.json();
    const p    = data.profile || {};
    if (p.name)            document.getElementById("profName").value      = p.name;
    if (p.country)         document.getElementById("profCountry").value   = p.country;
    if (p.education_level) document.getElementById("profLevel").value     = p.education_level;
    if (p.gpa)             document.getElementById("profGpa").value       = p.gpa;
    if (p.interests)       document.getElementById("profInterests").value = Array.isArray(p.interests) ? p.interests.join(", ") : p.interests;
  } catch(err) { /* silently skip */ }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("profileForm");
  if (!form) return;

  form.addEventListener("submit", async e => {
    e.preventDefault();
    const interests = document.getElementById("profInterests").value
      .split(",").map(s => s.trim()).filter(Boolean);

    const payload = {
      name:            document.getElementById("profName").value,
      country:         document.getElementById("profCountry").value,
      education_level: document.getElementById("profLevel").value,
      gpa:             document.getElementById("profGpa").value,
      interests,
    };

    try {
      await fetch("/api/profile", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload) });
      const alert = document.getElementById("profileAlert");
      if (alert) {
        alert.innerHTML = `<div class="alert alert-success py-2 mb-0"><i class="bi bi-check-circle me-1"></i>Profile saved! AI responses are now personalised.</div>`;
        setTimeout(() => alert.innerHTML = "", 4000);
      }
      showToast("Profile saved successfully!", "success");
    } catch(err) {
      showToast("Failed to save profile.", "danger");
    }
  });

  document.getElementById("clearProfile")?.addEventListener("click", async () => {
    ["profName","profCountry","profGpa","profInterests"].forEach(id => { const el = document.getElementById(id); if (el) el.value = ""; });
    const el = document.getElementById("profLevel"); if (el) el.value = "";
    await fetch("/api/profile", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({}) });
    showToast("Profile cleared.", "info");
  });
});

// ─── Chat ────────────────────────────────────────────────────────────────────

const chatState = { messages: [], isLoading: false };

function appendMessage(role, text) {
  const win    = document.getElementById("chatWindow");
  if (!win) return;

  const row    = document.createElement("div");
  row.className = `chat-message-row ${role === "user" ? "user-row" : ""}`;

  const avatar = role === "assistant"
    ? `<div class="chat-avatar"><i class="bi bi-mortarboard-fill"></i></div>`
    : `<div class="chat-avatar" style="background:linear-gradient(135deg,#10b981,#0ea5e9)"><i class="bi bi-person-fill"></i></div>`;

  // Convert basic markdown-ish formatting
  const formatted = text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/`(.*?)`/g, "<code>$1</code>")
    .replace(/\n\n/g, "<br><br>")
    .replace(/\n•/g, "<br>•")
    .replace(/\n-/g, "<br>-");

  row.innerHTML = `${avatar}<div class="chat-bubble ${role}">${formatted}</div>`;
  win.appendChild(row);
  win.scrollTop = win.scrollHeight;
}

function showTyping() {
  const win = document.getElementById("chatWindow");
  if (!win) return;
  const row = document.createElement("div");
  row.className = "chat-message-row";
  row.id = "typingRow";
  row.innerHTML = `<div class="chat-avatar"><i class="bi bi-mortarboard-fill"></i></div>
    <div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
  win.appendChild(row);
  win.scrollTop = win.scrollHeight;
}
function hideTyping() { document.getElementById("typingRow")?.remove(); }

async function sendMessage(text) {
  if (!text.trim() || chatState.isLoading) return;

  // Hide quick prompts after first use
  const qp = document.getElementById("quickPrompts");
  if (qp) qp.style.display = "none";

  appendMessage("user", text);
  chatState.isLoading = true;
  const sendBtn = document.getElementById("chatSend");
  if (sendBtn) { sendBtn.disabled = true; sendBtn.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`; }

  showTyping();

  try {
    const res  = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    hideTyping();

        if (data.error) {
      if (data.setup_required) {
        appendMessage("assistant", `⚠️ **Setup Required**\n\n${data.error}\n\nPlease copy \`env.example\` to \`.env\` and add your IBM Watsonx.ai credentials, then restart the server.`);
      } else {
        // 🔥 GRACEFUL FALLBACK: Show helpful message instead of raw error
        const fallbackMsg = getFallbackResponse(text);
        appendMessage("assistant", fallbackMsg);
      }
    } else {
      appendMessage("assistant", data.reply);
    }
  } catch(err) {
    hideTyping();
    appendMessage("assistant", "❌ Network error. Please check your connection and try again.");
  } finally {
    chatState.isLoading = false;
    if (sendBtn) { sendBtn.disabled = false; sendBtn.innerHTML = `<i class="bi bi-send-fill"></i>`; }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const input   = document.getElementById("chatInput");
  const sendBtn = document.getElementById("chatSend");

  // Auto-resize textarea
  input?.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 130) + "px";
  });

  // Enter to send (Shift+Enter = new line)
  input?.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const msg = input.value.trim();
      if (msg) { input.value = ""; input.style.height = "auto"; sendMessage(msg); }
    }
  });

  sendBtn?.addEventListener("click", () => {
    const msg = input?.value.trim();
    if (msg) { input.value = ""; input.style.height = "auto"; sendMessage(msg); }
  });

  // Quick prompt buttons
  $$(".quick-btn").forEach(btn => {
    btn.addEventListener("click", () => sendMessage(btn.dataset.msg));
  });

  // Clear chat
  document.getElementById("clearChat")?.addEventListener("click", () => {
    const win = document.getElementById("chatWindow");
    if (!win) return;
    win.innerHTML = `<div class="chat-welcome">
      <div class="chat-avatar"><i class="bi bi-mortarboard-fill"></i></div>
      <div class="chat-bubble assistant">👋 Chat cleared. Ask me anything about admissions!</div>
    </div>`;
    document.getElementById("quickPrompts").style.display = "flex";
  });
});

// ─── Smooth scroll for nav links ─────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  $$('a[href^="#"]').forEach(a => {
    a.addEventListener("click", e => {
      const target = document.querySelector(a.getAttribute("href"));
      if (target) {
        e.preventDefault();
        const navH = document.getElementById("mainNav")?.offsetHeight || 64;
        window.scrollTo({ top: target.offsetTop - navH - 12, behavior: "smooth" });
        // Close mobile menu if open
        const collapse = document.getElementById("navMenu");
        if (collapse?.classList.contains("show")) {
          bootstrap.Collapse.getInstance(collapse)?.hide();
        }
      }
    });
  });
});

// ─── Active nav highlight ─────────────────────────────────────────────────────

function initActiveNav() {
  const sections = $$("section[id]");
  const navLinks = $$("#mainNav .nav-link");

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(l => l.classList.remove("active"));
        const active = navLinks.find(l => l.getAttribute("href") === `#${entry.target.id}`);
        active?.classList.add("active");
      }
    });
  }, { threshold: 0.3 });

  sections.forEach(s => observer.observe(s));
}

// ─── Init ────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", async () => {
  await Promise.all([
    loadDashboard(),
    loadCourses(),
    loadDeadlines(),
    loadProfile(),
  ]);
  initReveal();
  initActiveNav();
});
