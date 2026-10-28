/* ================================================================
   SpamShield AI - Analytics Dashboard JavaScript
   ================================================================ */

const CHART_COLORS = {
  purple: 'rgba(168,85,247,',
  blue:   'rgba(59,130,246,',
  cyan:   'rgba(6,182,212,',
  green:  'rgba(34,197,94,',
  orange: 'rgba(249,115,22,',
  red:    'rgba(239,68,68,',
};

const MODEL_COLORS = [
  { bg: 'rgba(168,85,247,0.75)', border: 'rgba(168,85,247,1)' },
  { bg: 'rgba(59,130,246,0.75)',  border: 'rgba(59,130,246,1)' },
  { bg: 'rgba(6,182,212,0.75)',   border: 'rgba(6,182,212,1)' },
  { bg: 'rgba(34,197,94,0.75)',   border: 'rgba(34,197,94,1)' },
];

Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'Inter', sans-serif";

function $(id) { return document.getElementById(id); }
function show(id) { const el = $(id); if (el) el.style.display = ''; }
function hide(id) { const el = $(id); if (el) el.style.display = 'none'; }

// ── Fetch & Render ─────────────────────────────────────────────
async function loadAnalytics() {
  try {
    const res  = await fetch('/api/stats');
    const data = await res.json();
    
    if (!res.ok || data.error) {
      hide('loadingState');
      show('errorState');
      return;
    }
    
    hide('loadingState');
    renderStats(data);
    renderTable(data);
    renderCharts(data);
    renderConfusionMatrices(data);
    
  } catch (err) {
    hide('loadingState');
    show('errorState');
  }
}

// ── Stats Overview ─────────────────────────────────────────────
function renderStats(data) {
  const setText = (id, val) => { const el = $(id); if (el) el.textContent = val; };
  setText('bestModelName', data.best_model || '—');
  setText('totalSamples',  data.total_samples?.toLocaleString() || '—');
  setText('spamCount',     data.spam_count?.toLocaleString()    || '—');
  setText('hamCount',      data.ham_count?.toLocaleString()     || '—');
  show('statsRow');
}

// ── Metrics Table ──────────────────────────────────────────────
function renderTable(data) {
  const tbody = $('metricsTableBody');
  if (!tbody || !data.models) return;
  
  const bestName = data.best_model;
  
  tbody.innerHTML = data.models.map(m => {
    const isBest = m.name === bestName;
    return `
      <tr class="${isBest ? 'best-row' : ''}">
        <td>${isBest ? '🏆 ' : ''}${m.name}</td>
        <td>${renderMetricCell(m.accuracy)}</td>
        <td>${renderMetricCell(m.precision)}</td>
        <td>${renderMetricCell(m.recall)}</td>
        <td>${renderMetricCell(m.f1_score)}</td>
        <td>${renderMetricCell(m.roc_auc)}</td>
      </tr>
    `;
  }).join('');
  
  show('comparisonSection');
}

function renderMetricCell(val) {
  const pct = parseFloat(val) || 0;
  return `
    <div class="metric-bar-wrap">
      <span class="metric-val">${pct}%</span>
      <div class="metric-bar">
        <div class="metric-bar-fill" style="width:${pct}%"></div>
      </div>
    </div>
  `;
}

// ── Charts ─────────────────────────────────────────────────────
function renderCharts(data) {
  if (!data.models || !data.models.length) return;
  
  const labels = data.models.map(m => m.name);
  
  // 1. Accuracy Bar Chart
  createBarChart('accuracyChart', 'Accuracy (%)', labels, 
    data.models.map(m => m.accuracy));
  
  // 2. F1 Score Bar Chart
  createBarChart('f1Chart', 'F1 Score (%)', labels,
    data.models.map(m => m.f1_score));
  
  // 3. Dataset Doughnut
  const distCtx = $('distChart');
  if (distCtx) {
    new Chart(distCtx, {
      type: 'doughnut',
      data: {
        labels: ['Ham (Legitimate)', 'Spam'],
        datasets: [{
          data: [data.ham_count, data.spam_count],
          backgroundColor: ['rgba(34,197,94,0.75)', 'rgba(239,68,68,0.75)'],
          borderColor:     ['rgba(34,197,94,1)',    'rgba(239,68,68,1)'],
          borderWidth: 2,
          hoverOffset: 8,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { padding: 20, usePointStyle: true } },
          tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.raw.toLocaleString()} (${((ctx.raw/data.total_samples)*100).toFixed(1)}%)` } }
        },
        cutout: '65%',
      }
    });
  }
  
  // 4. Radar Chart
  const radarCtx = $('radarChart');
  if (radarCtx) {
    new Chart(radarCtx, {
      type: 'radar',
      data: {
        labels: ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC-AUC'],
        datasets: data.models.map((m, i) => ({
          label: m.name,
          data: [m.accuracy, m.precision, m.recall, m.f1_score, m.roc_auc],
          backgroundColor: MODEL_COLORS[i % MODEL_COLORS.length].bg.replace('0.75)', '0.15)'),
          borderColor:     MODEL_COLORS[i % MODEL_COLORS.length].border,
          borderWidth: 2,
          pointBackgroundColor: MODEL_COLORS[i % MODEL_COLORS.length].border,
          pointRadius: 4,
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            min: 80, max: 100,
            ticks: { backdropColor: 'transparent', stepSize: 5, font: { size: 10 } },
            grid:  { color: 'rgba(255,255,255,0.06)' },
            angleLines: { color: 'rgba(255,255,255,0.06)' },
          }
        },
        plugins: {
          legend: { position: 'bottom', labels: { padding: 16, usePointStyle: true, font: { size: 11 } } }
        }
      }
    });
  }
  
  show('chartsSection');
}

function createBarChart(canvasId, label, labels, values) {
  const ctx = $(canvasId);
  if (!ctx) return;
  
  const max = Math.max(...values);
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label,
        data: values,
        backgroundColor: MODEL_COLORS.map(c => c.bg),
        borderColor:     MODEL_COLORS.map(c => c.border),
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          min: Math.max(0, Math.min(...values) - 5),
          max: Math.min(100, max + 2),
          ticks: { callback: v => v + '%' },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 } }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw}%` }
        }
      }
    }
  });
}

// ── Confusion Matrices ─────────────────────────────────────────
function renderConfusionMatrices(data) {
  const grid = $('cmGrid');
  if (!grid || !data.models) return;
  
  grid.innerHTML = data.models.map(m => {
    const cm = m.confusion_matrix;
    if (!cm || cm.length < 2) return '';
    
    // [[TN, FP], [FN, TP]]
    const TN = cm[0][0], FP = cm[0][1];
    const FN = cm[1][0], TP = cm[1][1];
    
    return `
      <div class="cm-card">
        <h4>${m.name}</h4>
        <table class="cm-table">
          <tr>
            <td class="cm-tn" title="True Negative">${TN}<br/><small style="font-size:0.55rem;font-weight:500;opacity:0.7">TN</small></td>
            <td class="cm-fp" title="False Positive">${FP}<br/><small style="font-size:0.55rem;font-weight:500;opacity:0.7">FP</small></td>
          </tr>
          <tr>
            <td class="cm-fn" title="False Negative">${FN}<br/><small style="font-size:0.55rem;font-weight:500;opacity:0.7">FN</small></td>
            <td class="cm-tp" title="True Positive">${TP}<br/><small style="font-size:0.55rem;font-weight:500;opacity:0.7">TP</small></td>
          </tr>
        </table>
        <div class="cm-legend">
          <div class="cm-leg-item"><div class="cm-leg-dot" style="background:rgba(59,130,246,0.6)"></div>TN: Ham→Ham</div>
          <div class="cm-leg-item"><div class="cm-leg-dot" style="background:rgba(239,68,68,0.6)"></div>FP: Ham→Spam</div>
          <div class="cm-leg-item"><div class="cm-leg-dot" style="background:rgba(249,115,22,0.6)"></div>FN: Spam→Ham</div>
          <div class="cm-leg-item"><div class="cm-leg-dot" style="background:rgba(34,197,94,0.6)"></div>TP: Spam→Spam</div>
        </div>
      </div>
    `;
  }).join('');
  
  show('cmSection');
}

// ── Boot ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', loadAnalytics);
