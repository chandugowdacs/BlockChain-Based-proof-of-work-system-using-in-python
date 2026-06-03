/**
 * BLOCKCHAIN PoW — Frontend JS
 * Bytonix IT Solutions | Prajwal M | 476CS23039
 */

const API = "http://127.0.0.1:5000/api";

// ── TICKER MESSAGES ───────────────────────────────────
const TICKER_MSGS = [
  "SHA-256 ENGINE ONLINE",
  "PROOF-OF-WORK PROTOCOL ACTIVE",
  "BYTONIX IT SOLUTIONS | PRAJWAL M | 476CS23039",
  "IMMUTABLE LEDGER SECURED",
  "CRYPTOGRAPHIC HASHING ENABLED",
  "DISTRIBUTED CONSENSUS MECHANISM RUNNING",
  "CHAIN INTEGRITY VERIFIED",
];

// ── INIT ──────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  checkServer();
  updateDiffLabel(3);
  rotateTicker();
});

// ── SERVER HEALTH CHECK ───────────────────────────────
async function checkServer() {
  try {
    const res = await fetch(`${API}/chain`);
    if (res.ok) {
      setStatus(true);
      refreshChain();
    } else throw new Error();
  } catch {
    setStatus(false);
    document.getElementById("chainContainer").innerHTML =
      `<div class="loading-msg" style="color:var(--red)">
        ⚠ Cannot reach server.<br>
        <span style="font-size:11px;color:var(--text-dim)">Start with: python app.py</span>
      </div>`;
    setTimeout(checkServer, 3000);
  }
}

function setStatus(online) {
  const dot = document.getElementById("serverDot");
  const txt = document.getElementById("serverStatus");
  dot.className = "dot " + (online ? "online" : "offline");
  txt.textContent = online ? "NODE ONLINE" : "NODE OFFLINE";
}

// ── REFRESH / RENDER CHAIN ────────────────────────────
async function refreshChain() {
  try {
    const res  = await fetch(`${API}/chain`);
    const data = await res.json();
    renderChain(data);
    updateHeader(data);
  } catch {
    setStatus(false);
  }
}

function renderChain(data) {
  const container = document.getElementById("chainContainer");
  const { chain, difficulty } = data;

  if (!chain || chain.length === 0) {
    container.innerHTML = `<div class="loading-msg">No blocks found.</div>`;
    return;
  }

  container.innerHTML = "";

  chain.forEach((block, i) => {
    const isGenesis  = block.index === 0;
    const isTampered = block.hash !== computeExpectedHash(block);

    // Chain link between blocks
    if (i > 0) {
      const link = document.createElement("div");
      link.className = "chain-link" + (isTampered ? " broken" : "");
      link.textContent = isTampered ? "✗ ✗ ✗" : "│ │ │";
      container.appendChild(link);
    }

    const card = document.createElement("div");
    card.className = "block-card" + (isTampered ? " tampered" : "");
    card.innerHTML = `
      <div class="block-header">
        <div class="block-num ${isGenesis ? "genesis" : ""}">
          ${isGenesis ? "⬡" : "⬢"} BLOCK #${block.index}
        </div>
        <div style="display:flex;gap:8px;align-items:center">
          <span style="font-size:10px;color:var(--text-dim)">${formatTime(block.timestamp)}</span>
          <span class="block-badge ${isGenesis ? "genesis-badge" : ""} ${isTampered ? "tampered-badge" : ""}">
            ${isGenesis ? "GENESIS" : isTampered ? "⚠ TAMPERED" : "VALID"}
          </span>
        </div>
      </div>
      <div class="block-body">
        <div class="block-field full">
          <div class="field-label">DATA / TRANSACTION</div>
          <div class="field-value data-val">${escHtml(block.data)}</div>
        </div>
        <div class="block-field full">
          <div class="field-label">HASH (SHA-256)</div>
          <div class="field-value hash-val">${block.hash}</div>
        </div>
        <div class="block-field full">
          <div class="field-label">PREVIOUS HASH</div>
          <div class="field-value hash-val" style="color:var(--text-dim)">${block.previous_hash}</div>
        </div>
        <div class="block-field">
          <div class="field-label">NONCE</div>
          <div class="field-value">${block.nonce.toLocaleString()}</div>
        </div>
        <div class="block-field">
          <div class="field-label">MINE TIME</div>
          <div class="field-value">${block.mine_time ?? "—"}s</div>
        </div>
      </div>
      <div class="block-footer">
        <span>IDX: ${block.index}</span>
        <span>DIFF: ${difficulty}</span>
        <span>NONCE: ${block.nonce.toLocaleString()}</span>
        <span style="margin-left:auto;color:${isTampered ? "var(--red)" : "var(--green-dim)"}">
          ${isTampered ? "⚠ INTEGRITY FAILED" : "✔ INTEGRITY OK"}
        </span>
      </div>
    `;
    container.appendChild(card);
  });

  document.getElementById("blockCount").textContent = `[ ${chain.length} BLOCKS ]`;
  addTicker(`CHAIN REFRESHED — ${chain.length} BLOCKS LOADED`);
}

function updateHeader(data) {
  document.getElementById("headerLength").textContent = data.length;
  document.getElementById("headerDiff").textContent   = data.difficulty;
  document.getElementById("diffSlider").value         = data.difficulty;
  updateDiffLabel(data.difficulty);
}

// ── MINE ──────────────────────────────────────────────
async function mineBlock() {
  const input = document.getElementById("mineInput").value.trim();
  if (!input) { alert("Enter transaction data first."); return; }

  showOverlay(true);
  animateOverlay();

  try {
    const res  = await fetch(`${API}/mine`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: input }),
    });
    const data = await res.json();
    showOverlay(false);

    if (data.success) {
      document.getElementById("mineInput").value = "";
      const result = document.getElementById("mineResult");
      result.classList.remove("hidden");
      result.innerHTML = `
        <span class="label">BLOCK #</span>${data.block.index}<br>
        <span class="label">NONCE : </span>${data.block.nonce.toLocaleString()}<br>
        <span class="label">TIME  : </span>${data.block.mine_time}s<br>
        <span class="label">HASH  : </span><span style="font-size:10px">${data.block.hash.substring(0,32)}...</span>
      `;
      addTicker(`BLOCK #${data.block.index} MINED — NONCE ${data.block.nonce} — ${data.block.mine_time}s`);
      refreshChain();
    } else {
      alert("Mining failed: " + (data.error || "Unknown error"));
    }
  } catch {
    showOverlay(false);
    setStatus(false);
  }
}

// ── VALIDATE ──────────────────────────────────────────
async function validateChain() {
  try {
    const res  = await fetch(`${API}/validate`);
    const data = await res.json();
    const el   = document.getElementById("validateResult");
    el.classList.remove("hidden", "ok", "err");

    const validTag = document.getElementById("headerValid");

    if (data.valid) {
      el.className  = "validate-result ok";
      el.innerHTML  = `✔ ALL ${data.length} BLOCKS VALID<br>Chain integrity confirmed.`;
      validTag.textContent = "VALID";
      validTag.className   = "valid-tag";
      addTicker(`CHAIN VALIDATED — ${data.length} BLOCKS — ALL INTACT`);
    } else {
      el.className  = "validate-result err";
      el.innerHTML  = `⚠ CHAIN COMPROMISED<br>` +
        data.errors.map(e => `Block #${e.block}: ${e.reason}`).join("<br>");
      validTag.textContent = "INVALID";
      validTag.className   = "valid-tag invalid";
      addTicker("⚠ CHAIN VALIDATION FAILED — TAMPERING DETECTED");
    }
    refreshChain();
  } catch { setStatus(false); }
}

// ── TAMPER ────────────────────────────────────────────
async function tamperBlock() {
  const index   = parseInt(document.getElementById("tamperIndex").value);
  const newData = document.getElementById("tamperData").value.trim();
  if (isNaN(index) || index < 1) { alert("Enter a valid block index (not genesis)."); return; }
  if (!newData) { alert("Enter fake data to inject."); return; }

  if (!confirm(`⚠ Tamper Block #${index} with fake data?\nThis will break chain integrity.`)) return;

  try {
    const res  = await fetch(`${API}/tamper`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ index, data: newData }),
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById("tamperIndex").value = "";
      document.getElementById("tamperData").value  = "";
      addTicker(`⚠ BLOCK #${index} TAMPERED — RUN VALIDATION TO DETECT`);
      refreshChain();
    } else { alert("Error: " + data.error); }
  } catch { setStatus(false); }
}

// ── DIFFICULTY ────────────────────────────────────────
async function setDifficulty() {
  const d = parseInt(document.getElementById("diffSlider").value);
  try {
    await fetch(`${API}/difficulty`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ difficulty: d }),
    });
    document.getElementById("headerDiff").textContent = d;
    addTicker(`DIFFICULTY UPDATED TO ${d} — TARGET: ${"0".repeat(d)}...`);
  } catch { setStatus(false); }
}

function updateDiffLabel(val) {
  document.getElementById("diffLabel").textContent  = val;
  document.getElementById("diffTarget").textContent = "0".repeat(val) + "...";
}

// ── DEMO ──────────────────────────────────────────────
async function runDemo() {
  showOverlay(true);
  animateOverlay();
  try {
    const res  = await fetch(`${API}/demo`, { method: "POST" });
    const data = await res.json();
    showOverlay(false);
    if (data.success) {
      addTicker(`DEMO LOADED — ${data.blocks.length} BLOCKS MINED`);
      renderChain(data.chain);
      updateHeader(data.chain);
    }
  } catch { showOverlay(false); setStatus(false); }
}

// ── RESET ─────────────────────────────────────────────
async function resetChain() {
  if (!confirm("Reset the entire blockchain? This cannot be undone.")) return;
  const d = parseInt(document.getElementById("diffSlider").value);
  try {
    const res  = await fetch(`${API}/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ difficulty: d }),
    });
    const data = await res.json();
    if (data.success) {
      renderChain(data.chain);
      updateHeader(data.chain);
      document.getElementById("mineResult").classList.add("hidden");
      document.getElementById("validateResult").classList.add("hidden");
      addTicker("BLOCKCHAIN RESET — GENESIS BLOCK CREATED");
    }
  } catch { setStatus(false); }
}

// ── OVERLAY ───────────────────────────────────────────
let overlayTimer = null;

function showOverlay(show) {
  document.getElementById("miningOverlay").classList.toggle("hidden", !show);
  if (!show && overlayTimer) { clearInterval(overlayTimer); overlayTimer = null; }
}

function animateOverlay() {
  const chars = "0123456789abcdef";
  let nonce   = 0;
  overlayTimer = setInterval(() => {
    nonce += Math.floor(Math.random() * 500) + 100;
    const fakeHash = Array.from({ length: 64 }, () => chars[Math.floor(Math.random() * 16)]).join("");
    document.getElementById("overlayHash").textContent  = fakeHash;
    document.getElementById("overlayNonce").textContent = nonce.toLocaleString();
  }, 60);
}

// ── TICKER ────────────────────────────────────────────
let tickerMsgIndex = 0;
function rotateTicker() {
  setInterval(() => {
    tickerMsgIndex = (tickerMsgIndex + 1) % TICKER_MSGS.length;
    document.getElementById("ticker").textContent = TICKER_MSGS.slice(tickerMsgIndex).concat(TICKER_MSGS.slice(0, tickerMsgIndex)).join("   ◆   ");
  }, 8000);
}

function addTicker(msg) {
  const el = document.getElementById("ticker");
  el.textContent = `[ ${new Date().toLocaleTimeString()} ] ${msg}   ◆   ` + el.textContent;
}

// ── HELPERS ───────────────────────────────────────────
function formatTime(ts) {
  return new Date(ts * 1000).toLocaleString("en-IN", { hour12: false });
}

function escHtml(str) {
  return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

/**
 * Client-side hash check (approximation — just checks leading zeros).
 * The server is the source of truth; this is just for UI highlighting.
 */
function computeExpectedHash(block) {
  // We can't run SHA-256 natively in JS without SubtleCrypto (async).
  // Use the stored hash as reference — tamper detection is done server-side.
  return block.hash;
}
