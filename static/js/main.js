/* ================================================================
   SpamShield AI - Main JavaScript (Detector Page)
   ================================================================ */

const SPAM_SAMPLES = [
  "WINNER!! You have been selected to receive a £900 prize reward! Call 0800-PRIZE now to claim your FREE gift. Limited time offer!",
  "FREE ENTRY: Win a brand new iPhone 15 Pro! Text WIN to 80087. T&C apply. £1.50/msg. 18+ only. Don't miss out!",
  "Congratulations! You are our lucky winner! Click here to claim your $5000 prize: http://claim-now.fake.com",
  "URGENT! Your account will be suspended in 24 hours. Verify now: http://secure-bankupdate.com/verify",
  "You have been pre-approved for a £5000 loan. No credit check needed. Call 0800-LOANS now! Reply STOP to opt out.",
];

const HAM_SAMPLES = [
  "Hey, are you free for lunch tomorrow? I was thinking we could try that new Italian restaurant near the office.",
  "Don't forget about the team meeting at 3 PM today. I've sent the agenda to your email.",
  "Happy birthday! Hope you have an amazing day. Can't wait to celebrate with you this weekend!",
  "I finished the assignment. Can you review it before I submit? No rush, just whenever you have time.",
  "The bus is running late so I'll be there around 7:30 instead. Sorry for the inconvenience!",
];

let isAnalyzing = false;

// ── DOM Helpers ──────────────────────────────────────────────────
function $(id) { return document.getElementById(id); }
function setText(id, val) { const el = $(id); if (el) el.textContent = val; }

// ── Character Counter ──────────────────────────────────────────
const textarea = $('messageInput');
if (textarea) {
  textarea.addEventListener('input', () => {
    const count = textarea.value.length;
    const counter = $('charCount');
    if (counter) counter.textContent = count;
    counter && (counter.style.color = count > 1800 ? '#ef4444' : '');
  });

  textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      analyzeMessage();
    }
  });
}

// ── Load Sample ──────────────────────────────────────────────────
function loadSample(type, btn) {
  const samples = type === 'spam' ? SPAM_SAMPLES : HAM_SAMPLES;
  const message = samples[Math.floor(Math.random() * samples.length)];
  if (textarea) {
    textarea.value = message;
    textarea.dispatchEvent(new Event('input'));
    textarea.focus();
  }
  
  // Visual feedback
  if (btn) {
    btn.style.transform = 'scale(0.95)';
    setTimeout(() => btn.style.transform = '', 150);
  }
}

// ── Analyze Message ──────────────────────────────────────────────
async function analyzeMessage() {
  if (isAnalyzing) return;
  
  const message = textarea ? textarea.value.trim() : '';
  if (!message) {
    shakeTextarea();
    return;
  }
  
  isAnalyzing = true;
  setLoading(true);
  hideResult();
  
  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      showError(data.error || 'An unexpected error occurred.');
      return;
    }
    
    displayResult(data);
    
  } catch (err) {
    showError('Could not connect to server. Make sure the Flask app is running.');
  } finally {
    isAnalyzing = false;
    setLoading(false);
  }
}

// ── Display Result ───────────────────────────────────────────────
function displayResult(data) {
  const section = $('resultSection');
  const card    = $('resultCard');
  
  if (!section || !card) return;
  
  const isSpam  = data.is_spam;
  const spamPct = data.spam_probability;
  const hamPct  = data.ham_probability;
  
  // Card class
  card.className = `result-card ${isSpam ? 'is-spam' : 'is-ham'}`;
  
  // Icon & Label
  setText('resultIcon', isSpam ? '🚫' : '✅');
  
  const labelEl = $('resultLabel');
  if (labelEl) {
    labelEl.textContent = isSpam ? 'SPAM DETECTED' : 'LEGITIMATE MESSAGE';
    labelEl.style.color = isSpam ? '#ef4444' : '#22c55e';
  }
  
  setText('resultConfidence', `Confidence: ${data.confidence}% | Spam: ${spamPct}% | Ham: ${hamPct}%`);
  
  // Probability Bar (animate)
  const hamBar  = $('hamBar');
  const spamBar = $('spamBar');
  
  if (hamBar && spamBar) {
    // Force reset — disable transition, snap to 0, then re-enable and animate
    hamBar.style.transition  = 'none';
    spamBar.style.transition = 'none';
    hamBar.style.width  = '0%';
    spamBar.style.width = '0%';
    // Force reflow so the browser registers the 0% state
    void hamBar.offsetWidth;
    void spamBar.offsetWidth;
    // Re-enable transition and animate to real values
    hamBar.style.transition  = 'width 0.9s cubic-bezier(0.4,0,0.2,1)';
    spamBar.style.transition = 'width 0.9s cubic-bezier(0.4,0,0.2,1)';
    hamBar.style.width  = `${hamPct}%`;
    spamBar.style.width = `${spamPct}%`;
  }
  
  setText('hamPct',  `${hamPct}%`);
  setText('spamPct', `${spamPct}%`);
  
  // Feature Chips
  renderFeatures(data.features, isSpam);
  
  // Show section
  section.style.display = 'block';
  section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ── Feature Chips ────────────────────────────────────────────────
function renderFeatures(features, isSpam) {
  const grid = $('featuresGrid');
  if (!grid || !features) return;

  function flag(val, warn, danger) {
    if (val >= danger) return 'highlight-red';
    if (val >= warn)   return 'highlight-orange';
    return 'highlight-green';
  }
  function boolChip(val) {
    return val ? { txt: 'Detected ⚠', cls: 'highlight-red' } : { txt: 'None ✓', cls: 'highlight-green' };
  }

  const ph   = boolChip(features.has_phone);
  const url  = boolChip(features.has_url);
  const sc   = boolChip(features.has_shortcode);
  const em   = boolChip(features.has_email);
  const cur  = boolChip(features.has_currency);
  const rep  = boolChip(features.has_repeated_chars);

  // Total spam signal score visual
  const score = features.total_spam_signal_score || 0;
  const scoreColor = score >= 6 ? '#ef4444' : score >= 3 ? '#f97316' : score >= 1 ? '#facc15' : '#22c55e';
  const scoreWidth = Math.min(100, score * 8);

  grid.innerHTML = `
    <!-- ── Section 1: Structural ── -->
    <div class="feature-section-title">📐 Message Structure</div>
    <div class="feature-chip">
      <div class="fc-label">Length</div>
      <div class="fc-value">${features.length} chars</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Word Count</div>
      <div class="fc-value">${features.word_count} words</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Avg Word Length</div>
      <div class="fc-value">${features.avg_word_length} chars</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">ALL-CAPS Words</div>
      <div class="fc-value ${flag(features.num_caps_words, 1, 3)}">${features.num_caps_words}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Capitals %</div>
      <div class="fc-value ${features.capital_ratio > 30 ? 'highlight-red' : ''}">${features.capital_ratio}%</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Repeated Chars</div>
      <div class="fc-value ${rep.cls}">${rep.txt}</div>
    </div>

    <!-- ── Section 2: Contact / Network ── -->
    <div class="feature-section-title">🔗 Contact & Network</div>
    <div class="feature-chip">
      <div class="fc-label">URL / Link</div>
      <div class="fc-value ${url.cls}">${url.txt}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Phone Number</div>
      <div class="fc-value ${ph.cls}">${ph.txt}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Shortcode (4-6 digit)</div>
      <div class="fc-value ${sc.cls}">${sc.txt}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Email Address</div>
      <div class="fc-value ${em.cls}">${em.txt}</div>
    </div>

    <!-- ── Section 3: Money / Symbols ── -->
    <div class="feature-section-title">💰 Money & Symbols</div>
    <div class="feature-chip">
      <div class="fc-label">Currency ($£€)</div>
      <div class="fc-value ${cur.cls}">${cur.txt}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Exclamation (!) Count</div>
      <div class="fc-value ${flag(features.num_exclamation, 1, 3)}">${features.num_exclamation}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Percent (%) Count</div>
      <div class="fc-value ${flag(features.num_percent, 1, 2)}">${features.num_percent}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Asterisk (*) Count</div>
      <div class="fc-value ${flag(features.num_asterisk, 1, 2)}">${features.num_asterisk}</div>
    </div>

    <!-- ── Section 4: Spam Keyword Groups ── -->
    <div class="feature-section-title">🔍 Spam Keyword Groups</div>
    <div class="feature-chip">
      <div class="fc-label">⏰ Urgency Words</div>
      <div class="fc-value ${flag(features.urgency_count, 1, 2)}">${features.urgency_count}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">🎰 Prize / Lottery</div>
      <div class="fc-value ${flag(features.prize_count, 1, 2)}">${features.prize_count}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">💵 Money / Financial</div>
      <div class="fc-value ${flag(features.money_count, 1, 3)}">${features.money_count}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">📢 Action Imperatives</div>
      <div class="fc-value ${flag(features.action_count, 1, 3)}">${features.action_count}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">🏛 Fake Authority</div>
      <div class="fc-value ${flag(features.authority_count, 1, 2)}">${features.authority_count}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">📅 Subscription Traps</div>
      <div class="fc-value ${flag(features.subscription_count, 1, 2)}">${features.subscription_count}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">🔞 Adult / Pharma</div>
      <div class="fc-value ${flag(features.adult_count, 1, 2)}">${features.adult_count}</div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">🎣 Phishing Cues</div>
      <div class="fc-value ${flag(features.phishing_count, 1, 2)}">${features.phishing_count}</div>
    </div>

    <!-- ── Section 5: Overall Spam Signal Score ── -->
    <div class="feature-section-title">📊 Overall Spam Signal Score</div>
    <div class="feature-chip spam-score-chip">
      <div class="fc-label">Total Signal Score</div>
      <div class="fc-value" style="font-size:1.4rem;font-weight:800;color:${scoreColor}">${score}</div>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width:${scoreWidth}%;background:${scoreColor}"></div>
      </div>
      <div style="font-size:0.72rem;color:var(--text-secondary);margin-top:4px">
        ${score === 0 ? 'No spam signals detected' : score < 3 ? 'Low risk signals' : score < 6 ? 'Moderate spam signals' : 'High spam signal density'}
      </div>
    </div>
    <div class="feature-chip">
      <div class="fc-label">Total Spam Keywords</div>
      <div class="fc-value ${flag(features.spam_keywords, 2, 5)}">${features.spam_keywords}</div>
    </div>
  `;
}

// ── UI Helpers ───────────────────────────────────────────────────
function setLoading(loading) {
  const btn     = $('analyzeBtn');
  const btnText = btn ? btn.querySelector('.btn-text') : null;
  const btnLoad = btn ? btn.querySelector('.btn-loader') : null;
  
  if (!btn) return;
  
  btn.disabled = loading;
  if (btnText) btnText.style.display = loading ? 'none' : 'flex';
  if (btnLoad) btnLoad.style.display = loading ? 'flex' : 'none';
}

function hideResult() {
  const section = $('resultSection');
  if (section) section.style.display = 'none';
}

function shakeTextarea() {
  if (!textarea) return;
  textarea.style.animation = 'none';
  textarea.offsetHeight; // Reflow
  textarea.style.animation = 'shake 0.4s ease';
  textarea.focus();
  setTimeout(() => textarea.style.animation = '', 500);
}

function showError(message) {
  const section = $('resultSection');
  const card    = $('resultCard');
  if (!section || !card) return;
  
  card.className = 'result-card';
  card.style.borderColor = 'rgba(249,115,22,0.35)';
  card.style.background  = 'rgba(249,115,22,0.05)';
  card.innerHTML = `
    <div style="text-align:center;padding:1rem">
      <div style="font-size:2.5rem;margin-bottom:0.75rem">⚠️</div>
      <div style="font-weight:700;margin-bottom:0.4rem;color:#f97316">Error</div>
      <div style="color:var(--text-secondary);font-size:0.9rem">${message}</div>
    </div>
  `;
  section.style.display = 'block';
}

// ── CSS shake keyframe (injected) ─────────────────────────────
const style = document.createElement('style');
style.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20%       { transform: translateX(-6px); }
    40%       { transform: translateX(6px); }
    60%       { transform: translateX(-4px); }
    80%       { transform: translateX(4px); }
  }
`;
document.head.appendChild(style);
