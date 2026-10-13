/**
 * GST Verify - Developer Terminal & Live Verification Controller
 */

// Enterprise preset dictionary for instant sample verification
const ENTERPRISE_BENCHMARKS = {
  reliance: {
    gstin: "27AABCR1718E1ZP",
    legalName: "RELIANCE RETAIL LIMITED",
    tradeName: "RELIANCE RETAIL",
    pan: "AABCR1718E",
    state: "27",
    stateName: "MH",
    entity: "1",
    z: "Z",
    checksum: "P",
    constitution: "Public Limited Company",
    taxpayerType: "Regular",
    jurisdiction: "Mumbai East",
    address: "3rd Floor, Court House, Dhobi Talao, Lokmanya Tilak Marg, Kalbadevi, Mumbai, Maharashtra, 400002",
    pincode: "400002",
    city: "Mumbai",
    stateFull: "Maharashtra (27)",
    regDate: "01/07/2017",
    activities: ["Retail Trade", "Wholesale Trade", "Provision of Services"]
  },
  tcs: {
    gstin: "27AAACT2727Q1ZW",
    legalName: "TATA CONSULTANCY SERVICES LIMITED",
    tradeName: "TCS",
    pan: "AAACT2727Q",
    state: "27",
    stateName: "MH",
    entity: "1",
    z: "Z",
    checksum: "W",
    constitution: "Public Limited Company",
    taxpayerType: "Regular",
    jurisdiction: "LTU Division, Mumbai",
    address: "TCS House, Raveline Street, Fort, Mumbai, Maharashtra, 400001",
    pincode: "400001",
    city: "Mumbai",
    stateFull: "Maharashtra (27)",
    regDate: "01/07/2017",
    activities: ["Information Technology", "Cloud Infrastructure", "Enterprise AI"]
  },
  infosys: {
    gstin: "29AABCI1234F1Z8",
    legalName: "INFOSYS LIMITED",
    tradeName: "INFOSYS",
    pan: "AABCI1234F",
    state: "29",
    stateName: "KA",
    entity: "1",
    z: "Z",
    checksum: "8",
    constitution: "Public Limited Company",
    taxpayerType: "Regular",
    jurisdiction: "Large Taxpayer Unit, Bengaluru",
    address: "Electronics City, Hosur Road, Bengaluru, Karnataka, 560100",
    pincode: "560100",
    city: "Bengaluru",
    stateFull: "Karnataka (29)",
    regDate: "01/07/2017",
    activities: ["Software Engineering", "Digital Consulting", "Cloud Services"]
  },
  zomato: {
    gstin: "07AADCZ8098Q1ZU",
    legalName: "ZOMATO LIMITED",
    tradeName: "ZOMATO / BLINKIT",
    pan: "AADCZ8098Q",
    state: "07",
    stateName: "DL",
    entity: "1",
    z: "Z",
    checksum: "U",
    constitution: "Public Limited Company",
    taxpayerType: "Regular",
    jurisdiction: "Ward 104, New Delhi",
    address: "Ground Floor, 12A, 94, Meghdoot Building, Nehru Place, New Delhi, 110019",
    pincode: "110019",
    city: "New Delhi",
    stateFull: "Delhi (07)",
    regDate: "14/08/2017",
    activities: ["Hyperlocal Delivery", "Food Marketplace", "Quick Commerce"]
  }
};

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements - Form & Inputs
  const gstinInput = document.getElementById("gstin-input");
  const clearGstinBtn = document.getElementById("clear-gstin-btn");
  const charCounter = document.getElementById("char-counter");

  // Decomposition Elements
  const segmentState = document.getElementById("segment-state");
  const segmentStateName = document.getElementById("segment-state-name");
  const segmentPan = document.getElementById("segment-pan");
  const segmentEntity = document.getElementById("segment-entity");
  const segmentZ = document.getElementById("segment-z");
  const segmentChecksum = document.getElementById("segment-checksum");
  const checksumBox = document.getElementById("checksum-box");
  const segmentCheckStatus = document.getElementById("segment-check-status");
  const valChecksumText = document.getElementById("val-checksum-text");
  const checksumStatusPill = document.getElementById("checksum-status-pill");

  // Captcha Elements
  const captchaImg = document.getElementById("captcha-img");
  const captchaLoader = document.getElementById("captcha-loader");
  const captchaInput = document.getElementById("captcha-input");
  const refreshCaptchaBtn = document.getElementById("refresh-captcha-btn");
  const sessionTimerEl = document.getElementById("session-timer");

  // Verification Form & Action
  const verificationForm = document.getElementById("verification-form");
  const submitVerifyBtn = document.getElementById("submit-verify-btn");
  const btnSpinner = submitVerifyBtn.querySelector(".btn-spinner");
  const btnText = submitVerifyBtn.querySelector(".btn-text");

  // Error Alert
  const errorAlert = document.getElementById("error-alert");
  const errorTitle = document.getElementById("error-title");
  const errorDesc = document.getElementById("error-desc");

  // Taxpayer Output Elements
  const resLegalName = document.getElementById("res-legal-name");
  const resTradeName = document.getElementById("res-trade-name");
  const resStatusBadge = document.getElementById("res-status-badge");
  const resStatusText = document.getElementById("res-status-text");
  const resGstin = document.getElementById("res-gstin");
  const resPan = document.getElementById("res-pan");
  const resRegDate = document.getElementById("res-reg-date");
  const resTaxpayerType = document.getElementById("res-taxpayer-type");
  const resConstitution = document.getElementById("res-constitution");
  const resJurisdiction = document.getElementById("res-jurisdiction");
  const resAddress = document.getElementById("res-address");
  const resCity = document.getElementById("res-city");
  const resState = document.getElementById("res-state");
  const resPincode = document.getElementById("res-pincode");
  const resMapLink = document.getElementById("res-map-link");
  const resActivitiesTags = document.getElementById("res-activities-tags");

  // Tabs & Payloads
  const rawJsonOutput = document.getElementById("raw-json-output");
  const responseStatusBadge = document.getElementById("response-status-badge");
  const copyResultBtn = document.getElementById("copy-result-btn");
  const curlSessionIdToken = document.getElementById("curl-session-id-token");

  // Telemetry Badges
  const portalLatencyVal = document.getElementById("portal-latency-val");
  const portalHealthLabel = document.getElementById("portal-health-label");

  // Internal State
  let currentSessionId = null;
  let timerInterval = null;
  let remainingSeconds = 300;
  let lastVerifiedData = null;
  let debounceTimer = null;

  // 1. Initial Checks
  checkPortalHealth();
  fetchFreshCaptcha();

  // 2. Preset Benchmarks Click Handlers
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const gstin = btn.getAttribute("data-gstin");
      const nameKey = btn.getAttribute("data-name");

      // Set active chip styling
      document.querySelectorAll(".preset-btn").forEach(b => {
        b.className = "preset-btn px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 hover:text-white hover:border-slate-700 transition-colors whitespace-nowrap active:scale-95";
      });
      btn.className = "preset-btn px-2.5 py-1.5 rounded-lg bg-sky-950/50 border border-sky-500 text-xs font-mono text-sky-300 hover:border-sky-400 transition-colors whitespace-nowrap active:scale-95";

      gstinInput.value = gstin;
      clearGstinBtn.style.display = "block";
      handleGstinInput(gstin);

      if (ENTERPRISE_BENCHMARKS[nameKey]) {
        renderBenchmarkPreview(ENTERPRISE_BENCHMARKS[nameKey]);
      }

      captchaInput.focus();
    });
  });

  // 3. GSTIN Input & Offline Modulo-36 Dissection
  gstinInput.addEventListener("input", (e) => {
    e.target.value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
    const val = e.target.value;
    clearGstinBtn.style.display = val ? "block" : "none";
    handleGstinInput(val);
  });

  clearGstinBtn.addEventListener("click", () => {
    gstinInput.value = "";
    clearGstinBtn.style.display = "none";
    resetDecomposition();
    hideError();
    gstinInput.focus();
  });

  function handleGstinInput(val) {
    const len = val.length;
    charCounter.textContent = len === 15 ? "15/15 Valid Format" : `${len}/15 Chars`;
    charCounter.className = len === 15 ? "font-mono text-[11px] text-emerald-400" : "font-mono text-[11px] text-slate-400";

    if (len >= 2) {
      segmentState.textContent = val.slice(0, 2);
    } else {
      segmentState.textContent = "--";
      segmentStateName.textContent = "MH";
    }

    if (len >= 12) {
      segmentPan.textContent = val.slice(2, 12);
    } else {
      segmentPan.textContent = len > 2 ? val.slice(2).padEnd(10, "-") : "----------";
    }

    segmentEntity.textContent = len >= 13 ? val.slice(12, 13) : "-";
    segmentZ.textContent = len >= 14 ? val.slice(13, 14) : "-";

    if (len === 15) {
      segmentChecksum.textContent = val.slice(14, 15);
    } else {
      segmentChecksum.textContent = "-";
      segmentCheckStatus.textContent = "INGEST";
      segmentCheckStatus.className = "text-[9px] text-sky-400 font-semibold";
      checksumBox.className = "p-2 rounded-lg bg-slate-900 border border-slate-800";
      valChecksumText.textContent = `${len}/15 Ingest`;
      checksumStatusPill.className = "text-[10px] text-sky-400 flex items-center gap-1";
    }

    clearTimeout(debounceTimer);
    if (!val || val.length < 2) {
      resetDecomposition();
      return;
    }

    // Call instant 0ms offline validator endpoint
    debounceTimer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/v1/gstin/${encodeURIComponent(val)}/validate`);
        const json = await res.json();
        const v = json.validation;

        if (v.stateName) {
          segmentStateName.textContent = v.stateName.slice(0, 8);
          segmentStateName.title = v.stateName;
        }

        if (v.valid) {
          valChecksumText.textContent = "Valid Checksum";
          checksumStatusPill.className = "text-[10px] text-emerald-400 flex items-center gap-1";
          checksumBox.className = "p-2 rounded-lg bg-emerald-950/40 border border-emerald-500/60";
          segmentChecksum.className = "text-sm font-bold text-emerald-300 mt-0.5";
          segmentCheckStatus.textContent = "PASS";
          segmentCheckStatus.className = "text-[9px] text-emerald-400 font-semibold";
        } else if (v.checksum && !v.checksum.valid && len === 15) {
          valChecksumText.textContent = `Exp [${v.checksum.expected}]`;
          checksumStatusPill.className = "text-[10px] text-red-400 flex items-center gap-1";
          checksumBox.className = "p-2 rounded-lg bg-red-950/40 border border-red-500/60";
          segmentChecksum.className = "text-sm font-bold text-red-400 mt-0.5";
          segmentCheckStatus.textContent = "FAIL";
          segmentCheckStatus.className = "text-[9px] text-red-400 font-semibold";
        }
      } catch (err) {
        console.error("Offline validation error:", err);
      }
    }, 80);
  }

  function resetDecomposition() {
    segmentState.textContent = "--";
    segmentStateName.textContent = "MH";
    segmentPan.textContent = "----------";
    segmentEntity.textContent = "-";
    segmentZ.textContent = "-";
    segmentChecksum.textContent = "-";
    valChecksumText.textContent = "Standby";
    checksumStatusPill.className = "text-[10px] text-slate-400 flex items-center gap-1";
    checksumBox.className = "p-2 rounded-lg bg-slate-900 border border-slate-800";
    segmentCheckStatus.textContent = "IDLE";
    segmentCheckStatus.className = "text-[9px] text-slate-400 font-semibold";
    charCounter.textContent = "0/15 Chars";
  }

  // 4. Captcha Fetching & Refresh
  refreshCaptchaBtn.addEventListener("click", () => {
    fetchFreshCaptcha();
  });

  async function fetchFreshCaptcha() {
    try {
      captchaLoader.style.display = "flex";
      captchaImg.style.display = "none";
      refreshCaptchaBtn.disabled = true;
      captchaInput.value = "";
      hideError();

      const res = await fetch("/api/v1/captcha");
      const data = await res.json();

      if (data.success && data.captcha) {
        currentSessionId = data.sessionId;
        if (curlSessionIdToken) curlSessionIdToken.textContent = currentSessionId;
        captchaImg.src = data.captcha;
        captchaImg.onload = () => {
          captchaLoader.style.display = "none";
          captchaImg.style.display = "block";
        };
        startTimer(data.expiresIn || 300);
      } else {
        throw new Error(data.message || "Failed to load captcha challenge");
      }
    } catch (err) {
      showError("Captcha Error", err.message || "Could not retrieve captcha from GST portal. Click refresh to retry.");
      captchaLoader.innerHTML = '<span class="text-xs text-red-400">Failed to load. Click Refresh.</span>';
    } finally {
      refreshCaptchaBtn.disabled = false;
    }
  }

  function startTimer(seconds) {
    clearInterval(timerInterval);
    remainingSeconds = seconds;
    updateTimerDisplay();

    timerInterval = setInterval(() => {
      remainingSeconds--;
      if (remainingSeconds <= 0) {
        clearInterval(timerInterval);
        sessionTimerEl.textContent = "Expired";
        sessionTimerEl.className = "text-xs font-mono text-red-400 font-medium";
      } else {
        updateTimerDisplay();
      }
    }, 1000);
  }

  function updateTimerDisplay() {
    const mins = Math.floor(remainingSeconds / 60);
    const secs = remainingSeconds % 60;
    sessionTimerEl.textContent = `Expires in ${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    sessionTimerEl.className = remainingSeconds < 60 ? "text-xs font-mono text-amber-400 font-medium" : "text-xs font-mono text-sky-400 font-medium";
  }

  // 5. Form Submission
  verificationForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();

    const gstin = gstinInput.value.trim().toUpperCase();
    const captcha = captchaInput.value.trim();

    if (!gstin || gstin.length !== 15) {
      showError("Invalid GSTIN", "Please enter a 15-character Goods and Services Tax Identification Number.");
      return;
    }

    if (!captcha || captcha.length !== 6) {
      showError("Captcha Required", "Please enter the 6-character captcha code from the portal image.");
      captchaInput.focus();
      return;
    }

    if (!currentSessionId) {
      showError("Session Missing", "Captcha session is missing. Click refresh to get a challenge.");
      fetchFreshCaptcha();
      return;
    }

    setLoading(true);
    const startTime = performance.now();

    try {
      const response = await fetch("/api/v1/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: currentSessionId,
          gstin,
          captcha
        })
      });

      const elapsed = (performance.now() - startTime).toFixed(0);
      const result = await response.json();

      if (response.ok && result.success) {
        lastVerifiedData = result;
        renderTaxpayerProfile(result.data, result.raw, elapsed);
        responseStatusBadge.textContent = `200 OK (${elapsed}ms)`;
        responseStatusBadge.className = "text-[11px] font-mono text-emerald-400 px-2 py-0.5 rounded bg-emerald-950/50 border border-emerald-800/50";
        switchTab("profile");
        if (window.innerWidth < 1024 && window.switchMobileView) {
          window.switchMobileView("dossier");
        }
      } else {
        showError(result.error || "Verification Failed", result.message || "Invalid Captcha code or GSTIN not found.");
        fetchFreshCaptcha();
      }
    } catch (err) {
      showError("Network Error", err.message || "Failed to communicate with verification microservice.");
    } finally {
      setLoading(false);
    }
  });

  function setLoading(loading) {
    submitVerifyBtn.disabled = loading;
    btnSpinner.style.display = loading ? "inline-block" : "none";
    btnText.textContent = loading ? "Verifying with Portal..." : "Verify Taxpayer Identity";
  }

  // 6. Profile Rendering
  function renderTaxpayerProfile(data, raw, latencyMs) {
    resLegalName.textContent = data.legalName || "N/A";
    resTradeName.textContent = data.tradeName || data.legalName || "N/A";

    if (data.isActive) {
      resStatusBadge.className = "flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/60";
      resStatusText.textContent = "ACTIVE TAXPAYER";
      resStatusText.className = "text-xs font-mono font-bold text-emerald-300";
    } else {
      resStatusBadge.className = "flex items-center gap-2 px-3 py-1 rounded-full bg-red-950/80 border border-red-500/60";
      resStatusText.textContent = data.status || "INACTIVE";
      resStatusText.className = "text-xs font-mono font-bold text-red-300";
    }

    resGstin.textContent = data.gstin || "-";
    resPan.textContent = data.pan || "-";
    resRegDate.textContent = data.registrationDate || "-";
    resTaxpayerType.textContent = data.taxpayerType || "Regular";
    resConstitution.textContent = data.constitutionOfBusiness || "-";
    resJurisdiction.textContent = data.jurisdiction?.state || (data.state?.name ? `${data.state.name} Ward` : "Central");

    resAddress.textContent = data.address?.full || "Not recorded";
    resCity.textContent = data.address?.city || "-";
    resState.textContent = data.address?.state || data.state?.name || "-";
    resPincode.textContent = data.address?.pincode || "-";

    if (resMapLink) {
      const q = encodeURIComponent(`${data.address?.city || ""} ${data.address?.pincode || ""}`.trim() || data.legalName);
      resMapLink.href = `https://maps.google.com?q=${q}`;
    }

    resActivitiesTags.innerHTML = "";
    if (data.natureOfBusiness && data.natureOfBusiness.length > 0) {
      data.natureOfBusiness.forEach(act => {
        const span = document.createElement("span");
        span.className = "px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300";
        span.textContent = act;
        resActivitiesTags.appendChild(span);
      });
    } else {
      resActivitiesTags.innerHTML = '<span class="text-xs text-slate-500 font-mono">No specific activities listed</span>';
    }

    rawJsonOutput.textContent = JSON.stringify({
      status: "SUCCESS",
      statusCode: 200,
      latencyMs: parseInt(latencyMs) || 120,
      taxpayer: {
        gstin: data.gstin,
        legalName: data.legalName,
        tradeName: data.tradeName,
        status: data.status,
        isActive: data.isActive,
        pan: data.pan,
        taxpayerType: data.taxpayerType,
        constitutionOfBusiness: data.constitutionOfBusiness,
        registrationDate: data.registrationDate,
        address: data.address,
        natureOfBusiness: data.natureOfBusiness
      },
      rawResponse: raw
    }, null, 2);
  }

  function renderBenchmarkPreview(p) {
    resLegalName.textContent = p.legalName;
    resTradeName.textContent = p.tradeName;
    resStatusBadge.className = "flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/60";
    resStatusText.textContent = "ACTIVE TAXPAYER";
    resStatusText.className = "text-xs font-mono font-bold text-emerald-300";

    resGstin.textContent = p.gstin;
    resPan.textContent = p.pan;
    resRegDate.textContent = p.regDate;
    resTaxpayerType.textContent = p.taxpayerType;
    resConstitution.textContent = p.constitution;
    resJurisdiction.textContent = p.jurisdiction;

    resAddress.textContent = p.address;
    resCity.textContent = p.city;
    resState.textContent = p.stateFull;
    resPincode.textContent = p.pincode;

    resActivitiesTags.innerHTML = "";
    p.activities.forEach(act => {
      const span = document.createElement("span");
      span.className = "px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300";
      span.textContent = act;
      resActivitiesTags.appendChild(span);
    });

    rawJsonOutput.textContent = JSON.stringify({
      status: "SUCCESS",
      statusCode: 200,
      taxpayer: {
        gstin: p.gstin,
        legalName: p.legalName,
        tradeName: p.tradeName,
        status: "Active",
        pan: p.pan,
        taxpayerType: p.taxpayerType,
        registrationDate: p.regDate,
        constitutionOfBusiness: p.constitution,
        address: {
          city: p.city,
          pincode: p.pincode,
          state: p.stateFull
        }
      }
    }, null, 2);
  }

  // 7. Tab Switching
  window.switchTab = function(type) {
    const paneProfile = document.getElementById("pane-profile");
    const paneJson = document.getElementById("pane-json");
    const paneCurl = document.getElementById("pane-curl");

    const tabBtnProfile = document.getElementById("tab-btn-profile");
    const tabBtnJson = document.getElementById("tab-btn-json");
    const tabBtnCurl = document.getElementById("tab-btn-curl");

    paneProfile.classList.add("hidden");
    paneJson.classList.add("hidden");
    paneCurl.classList.add("hidden");

    const inactiveClass = "px-3 py-1.5 rounded-lg text-xs font-mono font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors";
    const activeClass = "px-3 py-1.5 rounded-lg text-xs font-mono font-semibold text-sky-400 bg-sky-950/60 border border-sky-800/60 transition-colors";

    tabBtnProfile.className = inactiveClass;
    tabBtnJson.className = inactiveClass;
    tabBtnCurl.className = inactiveClass;

    if (type === "profile") {
      paneProfile.classList.remove("hidden");
      tabBtnProfile.className = activeClass;
    } else if (type === "json") {
      paneJson.classList.remove("hidden");
      tabBtnJson.className = activeClass;
    } else if (type === "curl") {
      paneCurl.classList.remove("hidden");
      tabBtnCurl.className = activeClass;
    }
  };

  // 8. Mobile & Dock View Switcher
  window.switchMobileView = function(view) {
    const colConsole = document.getElementById("col-console");
    const colDossier = document.getElementById("col-dossier");
    const btnConsole = document.getElementById("view-toggle-console");
    const btnDossier = document.getElementById("view-toggle-dossier");

    const activeBtnClass = "flex-1 py-1.5 text-xs font-mono font-semibold rounded-lg bg-sky-950/80 text-sky-400 border border-sky-800/60 transition-all flex items-center justify-center gap-1.5";
    const inactiveBtnClass = "flex-1 py-1.5 text-xs font-mono font-medium rounded-lg text-slate-400 hover:text-white transition-all flex items-center justify-center gap-1.5";

    if (view === "console") {
      colConsole.style.display = "block";
      colDossier.style.display = "none";
      if (btnConsole) btnConsole.className = activeBtnClass;
      if (btnDossier) btnDossier.className = inactiveBtnClass;
    } else {
      colConsole.style.display = "none";
      colDossier.style.display = "block";
      if (btnConsole) btnConsole.className = inactiveBtnClass;
      if (btnDossier) btnDossier.className = activeBtnClass;
    }
  };

  function syncViewportLayout() {
    const colConsole = document.getElementById("col-console");
    const colDossier = document.getElementById("col-dossier");
    if (!colConsole || !colDossier) return;
    if (window.innerWidth >= 1024) {
      colConsole.style.display = "block";
      colDossier.style.display = "block";
    } else {
      window.switchMobileView("console");
    }
  }
  syncViewportLayout();
  window.addEventListener("resize", syncViewportLayout);

  // 9. Copy Handlers
  copyResultBtn.addEventListener("click", () => {
    const text = rawJsonOutput.textContent;
    navigator.clipboard.writeText(text).then(() => {
      const orig = copyResultBtn.innerHTML;
      copyResultBtn.innerHTML = '<span class="material-symbols-outlined text-sm text-emerald-400">check</span><span class="text-emerald-400">Copied</span>';
      setTimeout(() => { copyResultBtn.innerHTML = orig; }, 1800);
    });
  });

  // 9. Error Helpers
  function showError(title, desc) {
    errorTitle.textContent = title;
    errorDesc.textContent = desc;
    errorAlert.style.display = "flex";
  }

  function hideError() {
    errorAlert.style.display = "none";
  }

  // 10. Portal Health Check
  async function checkPortalHealth() {
    try {
      const res = await fetch("/health");
      const data = await res.json();
      
      if (data.gstPortal && data.gstPortal.healthy) {
        portalHealthLabel.textContent = "Online";
        portalHealthLabel.className = "text-emerald-400 font-medium";
        portalLatencyVal.textContent = `${data.gstPortal.latencyMs}ms`;
      } else {
        portalHealthLabel.textContent = "Slow";
        portalHealthLabel.className = "text-amber-400 font-medium";
        portalLatencyVal.textContent = "Degraded";
      }
    } catch {
      portalHealthLabel.textContent = "Offline";
      portalHealthLabel.className = "text-red-400 font-medium";
      portalLatencyVal.textContent = "Timeout";
    }
  }
});
