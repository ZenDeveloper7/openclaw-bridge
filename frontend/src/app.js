/* OpenClaw Control Board — Frontend v2 */

const API = window.location.port === '5173'
  ? 'http://localhost:8787/api'
  : '/api';

let currentPath = '';
let currentEditPath = '';

// ── Dashboard Config ───────────────────────────────────────────────
var dashboardConfig = { boardName: 'Control Board', icon: '🦞', theme: 'default', accentColor: null };

async function loadDashboardConfig() {
  try {
    var res = await fetch(API + '/dashboard/config');
    if (res.ok) {
      dashboardConfig = await res.json();
      applyDashboardConfig();
    }
  } catch (e) {
    console.log('Using default dashboard config');
  }
}

function applyDashboardConfig() {
  // Update page title
  document.title = dashboardConfig.boardName || 'OpenClaw Control Board';
  // Update header
  var boardTitle = document.getElementById('board-title');
  if (boardTitle) boardTitle.textContent = dashboardConfig.boardName || 'Control Board';
  // Update favicon if icon is provided
  if (dashboardConfig.icon) {
    var favicon = document.querySelector('link[rel="icon"]');
    if (favicon) {
      favicon.href = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>" + dashboardConfig.icon + "</text></svg>";
    }
    // Update logo
    var logoIcon = document.querySelector('.logo-icon');
    if (logoIcon) logoIcon.textContent = dashboardConfig.icon;
  }
  // Apply theme
  applyTheme(dashboardConfig.theme);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  // Update theme button states
  document.querySelectorAll('.theme-btn').forEach(function(btn) {
    btn.classList.toggle('active', btn.dataset.theme === theme);
  });
}

// ── Easter Eggs ───────────────────────────────────────────────────────
var easterEggs = (function() {
  var konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
  var konamiIndex = 0;
  var logoClickSequence = [];
  var logoClicks = 0;
  var matrixMode = false;
  var clickTimer = null;
  
  var secretMessages = [
    '🦞 You found a secret!',
    'The lobsters are watching...',
    'Did you know? Atlas holds up the sky!',
    '🚀 Productivity mode: ACTIVATED',
    '🎉 You are now 10% cooler',
    '⚡ Ka-chow!',
    '🔮 The future looks bright',
    '💡 Fun fact: Dolphins are smarter than you think',
    '🎮 Konami code hint: ↑↑↓↓←→←→BA',
    '🌟 You have discovered hidden knowledge',
    '🐙 tentacles? No, just octopus vibes',
  ];
  
  var matrixPhrases = [
    'Wake up, Neo...',
    'The Matrix has you...',
    'Follow the white rabbit.',
    'There is no spoon.',
    'Free your mind.',
    'Welcome to the real world.',
  ];
  
  // Konami code detection
  document.addEventListener('keydown', function(e) {
    if (e.key === konamiCode[konamiIndex]) {
      konamiIndex++;
      if (konamiIndex === konamiCode.length) {
        activateMatrixMode();
        konamiIndex = 0;
      }
    } else {
      konamiIndex = 0;
    }
  });
  
  // Logo click sequence
  var logo = document.querySelector('.logo');
  if (logo) {
    logo.style.cursor = 'pointer';
    logo.title = 'Click me...';
    logo.addEventListener('click', function() {
      logoClicks++;
      clearTimeout(clickTimer);
      logoClickSequence.push(Date.now());
      
      // Keep only last 5 clicks
      if (logoClickSequence.length > 5) logoClickSequence.shift();
      
      // Check for rapid clicks
      if (logoClicks === 7) {
        toast('🎮 7 clicks! You found a hidden feature!', 'success');
        logoClicks = 0;
      }
      
      clickTimer = setTimeout(function() {
        logoClicks = 0;
      }, 2000);
    });
  }
  
  // Random secret messages in console
  console.log('%c🛠️ OpenClaw Control Board', 'font-size: 24px; font-weight: bold; color: #f97316;');
  console.log('%cSecret commands:', 'font-weight: bold; color: #22c55e;');
  console.log('%c↑↑↓↓←→←→BA - Activate Matrix Mode', 'color: #88c0d0;');
  console.log('%cClick the logo 7 times rapidly - ???', 'color: #88c0d0;');
  console.log('%cType "easterEggs.revealAll()" in console', 'color: #88c0d0;');
  
  // Secret console function
  window.easterEggs = {
    revealAll: function() {
      console.log('%c🎉 EASTER EGGS REVEALED!', 'font-size: 20px; color: #f97316;');
      console.log('1. Konami code: ↑↑↓↓←→←→BA → Matrix Mode');
      console.log('2. Click logo 7 times → Secret toast');
      console.log('3. Theme: Matrix → Hacker vibes');
      console.log('4. Hidden in plain sight...');
      toast('🎉 Easter eggs revealed in console!', 'success');
    },
    matrix: function() {
      activateMatrixMode();
    },
    joke: function() {
      var jokes = [
        'Why did the lobster go to therapy? Because it had shell issues! 🦞',
        'What do you call a computer that sings? A-Dell! 🎤',
        'Why do programmers prefer dark mode? Because light attracts bugs! 🐛',
      ];
      toast(jokes[Math.floor(Math.random() * jokes.length)], 'success');
    },
  };
  
  // Random toast on page load (10% chance)
  if (Math.random() < 0.1) {
    setTimeout(function() {
      toast(secretMessages[Math.floor(Math.random() * secretMessages.length)], 'success');
    }, 3000);
  }
  
  // 404 page easter egg
  var originalTitle = document.title;
  document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
      document.title = '😢 Come back...';
    } else {
      document.title = originalTitle;
    }
  });
  
  function activateMatrixMode() {
    if (matrixMode) return;
    matrixMode = true;
    
    toast('🟢 Matrix Mode Activated...', 'success');
    document.body.classList.add('matrix-mode');
    
    // Random Matrix phrases in console
    console.log('%c� Matrix Mode Active 🌟', 'font-size: 16px; color: #00ff41; font-family: monospace;');
    var phraseInterval = setInterval(function() {
      var phrase = matrixPhrases[Math.floor(Math.random() * matrixPhrases.length)];
      console.log('%c' + phrase, 'color: #00ff41; font-family: monospace; font-size: 12px;');
    }, 3000);
    
    // Store in session
    sessionStorage.setItem('matrixMode', 'true');
    
    // Auto-disable after 2 minutes
    setTimeout(function() {
      matrixMode = false;
      document.body.classList.remove('matrix-mode');
      toast('🔴 Matrix Mode ended', 'success');
      clearInterval(phraseInterval);
      sessionStorage.removeItem('matrixMode');
    }, 120000);
  }
  
  // Check for saved matrix mode
  if (sessionStorage.getItem('matrixMode') === 'true') {
    matrixMode = true;
    document.body.classList.add('matrix-mode');
  }
})();

function applyCustomAccent(color) {
  if (color && color !== '#f97316') {
    document.documentElement.style.setProperty('--accent', color);
    document.documentElement.style.setProperty('--accent-hover', adjustBrightness(color, 10));
    document.documentElement.style.setProperty('--accent-dim', hexToRgba(color, 0.15));
  } else {
    // Reset to theme default
    var defaultAccent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#f97316';
    document.documentElement.style.setProperty('--accent', defaultAccent);
    document.documentElement.style.setProperty('--accent-hover', adjustBrightness(defaultAccent, 10));
    document.documentElement.style.setProperty('--accent-dim', hexToRgba(defaultAccent, 0.15));
  }
}

function adjustBrightness(hex, percent) {
  var num = parseInt(hex.replace('#', ''), 16);
  var amt = Math.round(2.55 * percent);
  var R = (num >> 16) + amt;
  var G = (num >> 8 & 0x00FF) + amt;
  var B = (num & 0x0000FF) + amt;
  return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
}

function hexToRgba(hex, alpha) {
  var r = parseInt(hex.slice(1, 3), 16);
  var g = parseInt(hex.slice(3, 5), 16);
  var b = parseInt(hex.slice(5, 7), 16);
  return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')';
}

// Theme button handlers
document.querySelectorAll('.theme-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    var theme = this.dataset.theme;
    applyTheme(theme);
    dashboardConfig.theme = theme;
    dashboardConfig.accentColor = null;
    document.getElementById('settings-accent-color').value = '#f97316';
  });
});

// Custom accent color handler
document.getElementById('settings-accent-color').addEventListener('input', function(e) {
  var color = e.target.value;
  applyCustomAccent(color);
});

// Settings modal handlers
document.getElementById('btn-settings').addEventListener('click', function() {
  document.getElementById('settings-board-name').value = dashboardConfig.boardName || '';
  document.getElementById('settings-board-icon').value = dashboardConfig.icon || '🦞';
  // Set theme buttons
  document.querySelectorAll('.theme-btn').forEach(function(btn) {
    btn.classList.toggle('active', btn.dataset.theme === dashboardConfig.theme);
  });
  document.getElementById('settings-accent-color').value = dashboardConfig.accentColor || '#f97316';
  document.getElementById('settings-modal').classList.remove('hidden');
});

document.getElementById('btn-settings-close').addEventListener('click', closeSettingsModal);
document.getElementById('btn-settings-cancel').addEventListener('click', closeSettingsModal);

function closeSettingsModal() {
  document.getElementById('settings-modal').classList.add('hidden');
}

document.getElementById('btn-settings-save').addEventListener('click', async function() {
  var boardName = document.getElementById('settings-board-name').value.trim() || 'Control Board';
  var icon = document.getElementById('settings-board-icon').value.trim() || '🦞';
  var theme = dashboardConfig.theme;
  var accentColor = document.getElementById('settings-accent-color').value;

  try {
    var res = await fetch(API + '/dashboard/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ boardName: boardName, icon: icon, theme: theme, accentColor: accentColor }),
    });
    if (res.ok) {
      dashboardConfig = await res.json();
      applyDashboardConfig();
      toast('Settings saved!', 'success');
      closeSettingsModal();
    } else {
      toast('Failed to save settings', 'error');
    }
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
});

document.getElementById('settings-modal').addEventListener('click', function(e) {
  if (e.target === this) closeSettingsModal();
});

// ── Dynamic Agent Registry ─────────────────────────────────────────
var agentRegistry = []; // [{id, name, emoji}]

async function loadAgentRegistry() {
  try {
    var res = await fetch(API + '/agents');
    var agents = await res.json();
    agentRegistry = agents.map(function(a) {
      return { id: a.id, name: a.name || a.id, emoji: getAgentEmoji(a.id, a.name) };
    });
  } catch (e) { /* keep existing */ }
  populateAgentDropdowns();
}

var agentColors = { main: '#f97316', atlas: '#3b82f6', jupiter: '#a855f7' };
function getAgentColor(id) { return agentColors[id] || '#6b7280'; }

function getAgentEmoji(id, name) {
  // Known emojis, fallback to first letter
  var known = { main: '🦞', atlas: '🛠️', jupiter: '💰'};
  return known[id] || '🤖';
}

function getAgentLabel(agentId) {
  if (!agentId) return '—';
  for (var i = 0; i < agentRegistry.length; i++) {
    if (agentRegistry[i].id === agentId) return agentRegistry[i].emoji + ' ' + agentRegistry[i].name;
  }
  return agentId;
}

function populateAgentDropdowns() {
  var selectors = ['task-agent', 'activity-agent-filter'];
  for (var s = 0; s < selectors.length; s++) {
    var el = document.getElementById(selectors[s]);
    if (!el) continue;
    var currentVal = el.value;
    var firstOpt = el.options[0]; // "Unassigned" or "All Agents"
    el.innerHTML = '';
    el.appendChild(firstOpt);
    for (var i = 0; i < agentRegistry.length; i++) {
      var opt = document.createElement('option');
      opt.value = agentRegistry[i].id;
      opt.textContent = agentRegistry[i].emoji + ' ' + agentRegistry[i].name;
      el.appendChild(opt);
    }
    el.value = currentVal;
  }
}

// ── Navigation ─────────────────────────────────────────────────────

document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    showView(btn.dataset.view);
  });
});

function showView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  var target = document.getElementById('view-' + name);
  if (target) target.classList.add('active');

  if (name === 'dashboard') loadDashboard();
  if (name === 'kanban') loadKanban();
  if (name === 'agents') loadAgents();
  if (name === 'subagents') loadSubagents();
  if (name === 'calendar') loadCalendar();
  if (name === 'files') loadConfig();
  if (name === 'activity') loadActivity();
  if (name === 'security') loadSecurity();
}


// ── Dashboard ──────────────────────────────────────────────────────

async function loadDashboard() {
  // Load stats
  try {
    var res = await fetch(API + '/stats');
    var stats = await res.json();

    var tasks = stats.tasks || {};

    document.getElementById('dashboard-stats').innerHTML = ''
      + dashCard('🦞', stats.version || '?', 'Version', 'orange')
      + dashCard(stats.gatewayRunning ? '🟢' : '🔴', stats.gatewayRunning ? 'Online' : 'Offline', 'Gateway', 'green')
      + dashCard('🤖', stats.agentCount, 'Agents', 'blue')
      + dashCard('📋', tasks.total || 0, 'Tasks', 'purple')
      + dashCard('🔥', tasks.inProgress || 0, 'In Progress', 'cyan')
      + dashCard('✅', tasks.done || 0, 'Completed', 'green')
      + dashCard('💾', formatSize(stats.workspaceSize || 0), 'Storage', 'blue')
      + dashCard('📝', tasks.backlog || 0, 'Backlog', 'orange');
  } catch (e) {
    document.getElementById('dashboard-stats').innerHTML = '<div class="loading">Error loading stats</div>';
  }

  // Load system health
  try {
    var res = await fetch(API + '/health');
    var health = await res.json();
    renderHealthMetrics(health);
  } catch (e) {
    document.getElementById('health-metrics').innerHTML = '<div class="loading">Unable to load health metrics</div>';
  }

  // Load agents
  try {
    var res = await fetch(API + '/agents');
    var agents = await res.json();
    var html = '';
    for (var i = 0; i < agents.length; i++) {
      html += renderAgentCard(agents[i], true);
    }
    document.getElementById('dash-agents').innerHTML = html || '<div class="loading">No agents</div>';
  } catch (e) {}

  // Load in-progress tasks
  try {
    var res = await fetch(API + '/kanban');
    var board = await res.json();
    var inProgress = (board.tasks || []).filter(function(t) { return t.status === 'in-progress'; });
    var html = '';
    for (var i = 0; i < inProgress.length; i++) {
      html += renderKanbanCard(inProgress[i]);
    }
    document.getElementById('dash-tasks').innerHTML = html || '<div class="loading" style="padding:20px; font-size:12px;">No tasks in progress</div>';
  } catch (e) {}
}

function dashCard(icon, value, label, color) {
  return '<div class="dash-card">'
    + '<div class="dash-icon ' + color + '">' + icon + '</div>'
    + '<div class="dash-info">'
    + '<div class="dash-value">' + esc(String(value)) + '</div>'
    + '<div class="dash-label">' + esc(label) + '</div>'
    + '</div></div>';
}

function renderHealthMetrics(health) {
  // Update uptime
  document.getElementById('health-uptime').textContent = 'Uptime: ' + (health.uptime || '--');
  
  // Build metrics HTML - ONLY RAM and Disk
  var metrics = [];
  
  // Memory
  var memClass = health.memory.percent > 80 ? 'critical' : health.memory.percent > 60 ? 'warning' : 'good';
  metrics.push({
    value: health.memory.percent + '%',
    label: 'RAM',
    icon: '🧠',
    className: memClass,
    detail: health.memory.usedGB + ' / ' + health.memory.totalGB + ' GB'
  });
  
  // Disk
  var diskClass = health.disk.percent > 80 ? 'critical' : health.disk.percent > 60 ? 'warning' : 'good';
  metrics.push({
    value: health.disk.percent + '%',
    label: 'Disk',
    icon: '💾',
    className: diskClass,
    detail: health.disk.usedGB + ' / ' + health.disk.totalGB + ' GB'
  });
  
  var html = '';
  for (var i = 0; i < metrics.length; i++) {
    var m = metrics[i];
    html += '<div class="health-metric ' + m.className + '">'
      + '<div class="health-metric-icon">' + m.icon + '</div>'
      + '<div class="health-metric-content">'
      + '<div class="health-metric-value">' + m.value + '</div>'
      + '<div class="health-metric-label">' + m.label + '</div>'
      + '<div class="health-metric-detail">' + m.detail + '</div>'
      + '</div></div>';
  }
  
  document.getElementById('health-metrics').innerHTML = html;
  
  // Update progress bars
  var memPercent = health.memory.percent || 0;
  var memBar = document.getElementById('mem-bar');
  var memText = document.getElementById('mem-percent');
  memBar.style.width = memPercent + '%';
  memBar.className = 'health-bar-fill ' + (memPercent > 80 ? 'critical' : memPercent > 60 ? 'warning' : 'good');
  memText.textContent = memPercent + '% (' + health.memory.usedGB + ' / ' + health.memory.totalGB + ' GB)';
  
  var diskPercent = health.disk.percent || 0;
  var diskBar = document.getElementById('disk-bar');
  var diskText = document.getElementById('disk-percent');
  diskBar.style.width = diskPercent + '%';
  diskBar.className = 'health-bar-fill ' + (diskPercent > 80 ? 'critical' : diskPercent > 60 ? 'warning' : 'good');
  diskText.textContent = diskPercent + '% (' + health.disk.usedGB + ' / ' + health.disk.totalGB + ' GB)';
  diskBar.style.width = diskPercent + '%';
  diskBar.className = 'health-bar-fill ' + (diskPercent > 80 ? 'critical' : diskPercent > 60 ? 'warning' : 'good');
  diskText.textContent = diskPercent + '% (' + health.disk.usedGB + ' / ' + health.disk.totalGB + ' GB)';
  
  // Load average chart removed — only RAM and Disk shown
}

document.getElementById('btn-refresh-dash').addEventListener('click', loadDashboard);

// ── Kanban Board ───────────────────────────────────────────────────

var COLUMNS = [
  { id: 'backlog', label: 'Backlog', icon: '📝' },
  { id: 'in-progress', label: 'In Progress', icon: '🔥' },
  { id: 'review', label: 'Review', icon: '👀' },
  { id: 'done', label: 'Done', icon: '✅' },
];

var kanbanTasks = [];
var editingTaskId = null;

async function loadKanban() {
  try {
    var res = await fetch(API + '/kanban');
    var board = await res.json();
    kanbanTasks = board.tasks || [];
    renderKanban();
  } catch (e) {
    document.getElementById('kanban-board').innerHTML = '<div class="loading">Error loading tasks</div>';
  }
}

function renderKanban() {
  var board = document.getElementById('kanban-board');
  var html = '';

  for (var c = 0; c < COLUMNS.length; c++) {
    var col = COLUMNS[c];
    var colTasks = kanbanTasks.filter(function(t) { return t.status === col.id; });

    html += '<div class="kanban-column col-' + col.id + '">'
      + '<div class="kanban-col-header">'
      + '<div class="kanban-col-title">' + col.icon + ' ' + col.label
      + ' <span class="kanban-col-count">' + colTasks.length + '</span></div>'
      + '</div>'
      + '<div class="kanban-col-body" data-status="' + col.id + '" '
      + 'ondragover="kanbanDragOver(event)" ondragleave="kanbanDragLeave(event)" ondrop="kanbanDrop(event)">';

    for (var t = 0; t < colTasks.length; t++) {
      html += renderKanbanCard(colTasks[t]);
    }

    html += '</div>'
      + '<div style="padding:0 10px 10px;">'
      + '<button class="kanban-add-btn" onclick="openNewTask(\'' + col.id + '\')">+ Add task</button>'
      + '</div>'
      + '</div>';
  }

  board.innerHTML = html;
}

function renderKanbanCard(task) {
  var agentClass = task.agent === 'main' ? 'agent-poseidon' : task.agent === 'atlas' ? 'agent-atlas' : 'agent-unassigned';
  var agentLabel = getAgentLabel(task.agent);
  var prioClass = 'priority-' + (task.priority || 'normal');

  var tagsHtml = '';
  if (task.tags && task.tags.length) {
    tagsHtml = '<div class="kanban-card-tags">';
    for (var i = 0; i < task.tags.length; i++) {
      if (task.tags[i]) tagsHtml += '<span class="kanban-tag">' + esc(task.tags[i]) + '</span>';
    }
    tagsHtml += '</div>';
  }

  return '<div class="kanban-card ' + prioClass + '" draggable="true" data-task-id="' + esc(task.id) + '" '
    + 'ondragstart="kanbanDragStart(event)" ondragend="kanbanDragEnd(event)">'
    + '<div class="kanban-card-actions">'
    + '<button onclick="editTask(\'' + esc(task.id) + '\')" title="Edit">✏️</button>'
    + '</div>'
    + '<div class="kanban-card-title">' + esc(task.title) + '</div>'
    + (task.description ? '<div class="kanban-card-desc">' + esc(task.description) + '</div>' : '')
    + '<div class="kanban-card-footer">'
    + '<span class="kanban-card-agent ' + agentClass + '">' + agentLabel + '</span>'
    + tagsHtml
    + '</div></div>';
}

// ── Kanban Drag & Drop ─────────────────────────────────────────────

var draggedTaskId = null;

function kanbanDragStart(e) {
  draggedTaskId = e.target.dataset.taskId;
  e.target.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
}

function kanbanDragEnd(e) {
  e.target.classList.remove('dragging');
  document.querySelectorAll('.kanban-col-body').forEach(function(el) {
    el.classList.remove('drag-over');
  });
}

function kanbanDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  e.currentTarget.classList.add('drag-over');
}

function kanbanDragLeave(e) {
  e.currentTarget.classList.remove('drag-over');
}

async function kanbanDrop(e) {
  e.preventDefault();
  e.currentTarget.classList.remove('drag-over');

  var newStatus = e.currentTarget.dataset.status;
  if (!draggedTaskId || !newStatus) return;

  try {
    await fetch(API + '/kanban/task/' + encodeURIComponent(draggedTaskId) + '/move', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });
    await loadKanban();
    toast('Moved to ' + newStatus, 'success');
  } catch (e) {
    toast('Move failed', 'error');
  }

  draggedTaskId = null;
}

// ── Task Modal ─────────────────────────────────────────────────────

function openNewTask(status) {
  editingTaskId = null;
  document.getElementById('task-modal-title').textContent = 'New Task';
  document.getElementById('task-title').value = '';
  document.getElementById('task-desc').value = '';
  document.getElementById('task-agent').value = '';
  document.getElementById('task-priority').value = 'normal';
  document.getElementById('task-status').value = status || 'backlog';
  document.getElementById('task-tags').value = '';
  document.getElementById('btn-task-delete').style.display = 'none';
  document.getElementById('task-modal').classList.remove('hidden');
  document.getElementById('task-title').focus();
}

function editTask(taskId) {
  var task = null;
  for (var i = 0; i < kanbanTasks.length; i++) {
    if (kanbanTasks[i].id === taskId) { task = kanbanTasks[i]; break; }
  }
  if (!task) return;

  editingTaskId = taskId;
  document.getElementById('task-modal-title').textContent = 'Edit Task';
  document.getElementById('task-title').value = task.title || '';
  document.getElementById('task-desc').value = task.description || '';
  document.getElementById('task-agent').value = task.agent || '';
  document.getElementById('task-priority').value = task.priority || 'normal';
  document.getElementById('task-status').value = task.status || 'backlog';
  document.getElementById('task-tags').value = (task.tags || []).join(', ');
  document.getElementById('btn-task-delete').style.display = 'inline-flex';
  document.getElementById('task-modal').classList.remove('hidden');
  document.getElementById('task-title').focus();
}

document.getElementById('btn-add-task').addEventListener('click', function() {
  openNewTask('backlog');
});

document.getElementById('btn-task-close').addEventListener('click', closeTaskModal);
document.getElementById('btn-task-cancel').addEventListener('click', closeTaskModal);

function closeTaskModal() {
  document.getElementById('task-modal').classList.add('hidden');
  editingTaskId = null;
}

document.getElementById('btn-task-save').addEventListener('click', async function() {
  var title = document.getElementById('task-title').value.trim();
  if (!title) { toast('Title is required', 'error'); return; }

  var tagsRaw = document.getElementById('task-tags').value;
  var tags = tagsRaw ? tagsRaw.split(',').map(function(s) { return s.trim(); }).filter(Boolean) : [];

  var taskData = {
    title: title,
    description: document.getElementById('task-desc').value.trim(),
    agent: document.getElementById('task-agent').value,
    priority: document.getElementById('task-priority').value,
    status: document.getElementById('task-status').value,
    tags: tags,
  };

  try {
    if (editingTaskId) {
      await fetch(API + '/kanban/task/' + encodeURIComponent(editingTaskId), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData),
      });
      toast('Task updated!', 'success');
    } else {
      taskData.id = '';
      await fetch(API + '/kanban/task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData),
      });
      toast('Task created!', 'success');
    }

    closeTaskModal();
    await loadKanban();
    // Also refresh dashboard if visible
    if (document.getElementById('view-dashboard').classList.contains('active')) {
      loadDashboard();
    }
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
});

document.getElementById('btn-task-delete').addEventListener('click', async function() {
  if (!editingTaskId) return;
  if (!confirm('Delete this task?')) return;

  try {
    await fetch(API + '/kanban/task/' + encodeURIComponent(editingTaskId), {
      method: 'DELETE',
    });
    toast('Task deleted', 'success');
    closeTaskModal();
    await loadKanban();
  } catch (e) {
    toast('Delete failed', 'error');
  }
});

document.getElementById('task-modal').addEventListener('click', function(e) {
  if (e.target === this) closeTaskModal();
});

// ── Configuration View ──────────────────────────────────────────────

async function loadConfig() {
  var container = document.getElementById('config-view');
  if (!container) {
    // Fallback to files if element doesn't exist
    loadFiles('');
    return;
  }
  
  container.innerHTML = '<div class="loading">Loading configuration...</div>';
  
  try {
    // Load openclaw.json via dedicated endpoint
    var res = await fetch(API + '/openclaw/config');
    if (!res.ok) {
      container.innerHTML = '<div class="error">Could not load configuration</div>';
      return;
    }
    
    var config = await res.json();
    var pretty = JSON.stringify(config, null, 2);
    var html = '<div class="config-card">';
    html += '<div class="config-header" style="display:flex;align-items:center;justify-content:space-between;">';
    html += '<div style="display:flex;align-items:center;gap:8px;"><span class="config-icon">⚙️</span><span class="config-title">openclaw.json</span></div>';
    html += '<button id="btn-save-config" class="btn btn-primary" style="font-size:12px;">💾 Save</button>';
    html += '</div>';
    html += '<div class="config-content">';
    html += '<textarea id="config-editor" spellcheck="false"></textarea>';
    html += '</div>';
    html += '</div>';
    
    container.innerHTML = html;
    
    // Initialize CodeMirror for JSON editing
    var editorEl = document.getElementById('config-editor');
    if (editorEl) {
      codeMirrorInstance = CodeMirror.fromTextArea(editorEl, {
        mode: "application/json",
        theme: "material-darker",
        lineNumbers: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        indentUnit: 2,
        tabSize: 2
      });
      codeMirrorInstance.setValue(pretty);
    }
    
    document.getElementById('btn-save-config').addEventListener('click', async function() {
      var content = codeMirrorInstance ? codeMirrorInstance.getValue() : document.getElementById('config-editor').value;
      try {
        var parsed = JSON.parse(content); // validate
        var res = await fetch(API + '/openclaw/config', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(parsed),
        });
        if (res.ok) toast('Config saved!', 'success');
        else toast('Save failed', 'error');
      } catch (e) {
        toast('Invalid JSON: ' + e.message, 'error');
      }
    });
  } catch (e) {
    container.innerHTML = '<div class="error">Error: ' + esc(e.message) + '</div>';
  }
}

// Keep loadFiles for backward compatibility but it just redirects to config
async function loadFiles(path) {
  loadConfig();
}

function updateBreadcrumbs(path) {
  var bc = document.getElementById('breadcrumbs');
  var html = '<span class="crumb" onclick="loadFiles(\'\')">~/.openclaw</span>';

  if (path) {
    var parts = path.split('/');
    var cumulative = '';
    for (var i = 0; i < parts.length; i++) {
      cumulative = cumulative ? cumulative + '/' + parts[i] : parts[i];
      html += '<span class="crumb" onclick="loadFiles(\'' + escAttr(cumulative) + '\')">' + esc(parts[i]) + '</span>';
    }
  }

  bc.innerHTML = html;
}

// ── File Editor ────────────────────────────────────────────────────

function isImageFile(path) {
  return /\.(jpg|jpeg|png|gif|webp|svg|bmp|ico)$/i.test(path);
}

function openImageViewer(path) {
  var modal = document.getElementById('image-viewer-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'image-viewer-modal';
    modal.className = 'img-viewer-modal';
    modal.innerHTML = '<div class="img-viewer-backdrop"></div>'
      + '<div class="img-viewer-container">'
      + '<div class="img-viewer-header">'
      + '<span class="img-viewer-title"></span>'
      + '<button class="img-viewer-close" onclick="closeImageViewer()">✕</button>'
      + '</div>'
      + '<div class="img-viewer-body"><img class="img-viewer-img" /></div>'
      + '<div class="img-viewer-footer"></div>'
      + '</div>';
    document.body.appendChild(modal);
    modal.querySelector('.img-viewer-backdrop').addEventListener('click', closeImageViewer);
  }
  var imgUrl = API + '/files/image?path=' + encodeURIComponent(path);
  var fileName = path.split('/').pop();
  modal.querySelector('.img-viewer-title').textContent = fileName;
  modal.querySelector('.img-viewer-footer').textContent = path;
  var img = modal.querySelector('.img-viewer-img');
  img.src = imgUrl;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeImageViewer() {
  var modal = document.getElementById('image-viewer-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// Close on Escape
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeImageViewer();
});

async function openFile(path) {
  if (path.endsWith('.jsonl')) return openJsonl(path);
  if (isImageFile(path)) return openImageViewer(path);

  try {
    var res = await fetch(API + '/files/read?path=' + encodeURIComponent(path));
    if (!res.ok) { toast((await res.json()).detail || 'Cannot open', 'error'); return; }

    var data = await res.json();
    currentEditPath = path;

    document.getElementById('editor-title').textContent = data.name;
    document.getElementById('editor-status').textContent = data.type + ' · ' + path;

    // Determine CodeMirror mode based on file extension
    var mode = "text/plain";
    if (path.endsWith('.js') || path.endsWith('.jsx') || path.endsWith('.ts') || path.endsWith('.tsx')) {
      mode = "javascript";
    } else if (path.endsWith('.py')) {
      mode = "python";
    } else if (path.endsWith('.json') || path.endsWith('.jsonl')) {
      mode = "application/json";
    } else if (path.endsWith('.md') || path.endsWith('.markdown')) {
      mode = "markdown";
    } else if (path.endsWith('.html') || path.endsWith('.htm')) {
      mode = "htmlmixed";
    } else if (path.endsWith('.css')) {
      mode = "css";
    } else if (path.endsWith('.sql')) {
      mode = "sql";
    } else if (path.endsWith('.xml') || path.endsWith('.yaml') || path.endsWith('.yml')) {
      mode = "application/xml";
    }

    // Markdown preview support
    var isMarkdown = data.type === 'markdown' || path.endsWith('.md');
    editorIsMarkdown = isMarkdown;
    var toggleBtn = document.getElementById('btn-toggle-preview');
    var editorContainer = document.getElementById('editor-container');
    var preview = document.getElementById('markdown-preview');

    toggleBtn.style.display = isMarkdown ? 'inline-flex' : 'none';

    if (isMarkdown) {
      // Default to preview mode for markdown
      editorPreviewMode = true;
      editorContainer.style.display = 'none';
      preview.style.display = 'block';
      preview.innerHTML = parseMarkdown(data.content);
      toggleBtn.textContent = '✏️ Edit';
    } else {
      editorPreviewMode = false;
      editorContainer.style.display = '';
      preview.style.display = 'none';
      toggleBtn.textContent = '👁️ Preview';
      
      // Initialize or update CodeMirror for code files
      var editorEl = document.getElementById('editor');
      if (editorEl) {
        if (codeMirrorInstance) {
          codeMirrorInstance.setValue(data.content);
          codeMirrorInstance.setOption("mode", mode);
        } else {
          codeMirrorInstance = CodeMirror.fromTextArea(editorEl, {
            mode: mode,
            theme: "material-darker",
            lineNumbers: true,
            matchBrackets: true,
            autoCloseBrackets: true,
            indentUnit: 2,
            tabSize: 2
          });
        }
      }
    }

    document.querySelectorAll('.view').forEach(function(v) { v.classList.remove('active'); });
    document.getElementById('view-editor').classList.add('active');
  } catch (e) {
    toast('Error: ' + e.message, 'error');
  }
}

// ── Markdown Preview ───────────────────────────────────────────────

var editorIsMarkdown = false;
var editorPreviewMode = false;
var codeMirrorInstance = null;

function parseMarkdown(md) {
  var html = md;

  // Escape HTML
  html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  // Code blocks (``` ... ```)
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, function(m, lang, code) {
    return '<pre><code class="lang-' + lang + '">' + code.trim() + '</code></pre>';
  });

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Tables
  html = html.replace(/^(\|.+\|)\n(\|[\s\-:|]+\|)\n((?:\|.+\|\n?)+)/gm, function(m, header, sep, body) {
    var ths = header.split('|').filter(Boolean).map(function(c) { return '<th>' + c.trim() + '</th>'; }).join('');
    var rows = body.trim().split('\n').map(function(row) {
      var tds = row.split('|').filter(Boolean).map(function(c) { return '<td>' + c.trim() + '</td>'; }).join('');
      return '<tr>' + tds + '</tr>';
    }).join('');
    return '<table><thead><tr>' + ths + '</tr></thead><tbody>' + rows + '</tbody></table>';
  });

  // Headings
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Horizontal rule
  html = html.replace(/^---+$/gm, '<hr>');

  // Blockquotes
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');

  // Bold + italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Strikethrough
  html = html.replace(/~~(.+?)~~/g, '<del>$1</del>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

  // Images
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');

  // Task lists
  html = html.replace(/^(\s*)- \[x\] (.+)$/gm, '$1<li><input type="checkbox" checked disabled> <span class="task-done">$2</span></li>');
  html = html.replace(/^(\s*)- \[ \] (.+)$/gm, '$1<li><input type="checkbox" disabled> $2</li>');

  // Unordered lists
  html = html.replace(/^(\s*)- (.+)$/gm, function(m, indent, content) {
    return '<li>' + content + '</li>';
  });

  // Wrap consecutive <li> in <ul>
  html = html.replace(/((?:<li>[\s\S]*?<\/li>\n?)+)/g, '<ul>$1</ul>');

  // Ordered lists
  html = html.replace(/^(\d+)\. (.+)$/gm, '<oli>$2</oli>');
  html = html.replace(/((?:<oli>[\s\S]*?<\/oli>\n?)+)/g, function(m) {
    return '<ol>' + m.replace(/<\/?oli>/g, function(t) { return t.replace('oli', 'li'); }) + '</ol>';
  });

  // Paragraphs — wrap loose lines
  html = html.replace(/^(?!<[a-z/])((?!<).+)$/gm, '<p>$1</p>');

  // Clean up empty paragraphs
  html = html.replace(/<p>\s*<\/p>/g, '');

  return html;
}

document.getElementById('btn-toggle-preview').addEventListener('click', function() {
  editorPreviewMode = !editorPreviewMode;

  var editorContainer = document.getElementById('editor-container');
  var preview = document.getElementById('markdown-preview');

  if (editorPreviewMode) {
    editorContainer.style.display = 'none';
    preview.style.display = 'block';
    preview.innerHTML = parseMarkdown(document.getElementById('editor').value);
    this.textContent = '✏️ Edit';
  } else {
    editorContainer.style.display = '';
    preview.style.display = 'none';
    this.textContent = '👁️ Preview';
  }
});

document.getElementById('btn-save').addEventListener('click', async function() {
  if (!currentEditPath) return;
  try {
    var res = await fetch(API + '/files/write?path=' + encodeURIComponent(currentEditPath), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: document.getElementById('editor').value }),
    });
    if (!res.ok) { toast((await res.json()).detail || 'Save failed', 'error'); return; }
    toast('Saved!', 'success');
  } catch (e) { toast('Error: ' + e.message, 'error'); }
});

document.getElementById('btn-close-editor').addEventListener('click', function() {
  currentEditPath = '';
  showView('files');
  document.querySelectorAll('.nav-btn').forEach(function(b) {
    b.classList.toggle('active', b.dataset.view === 'files');
  });
});

// ── Agents ─────────────────────────────────────────────────────────

// Agent roles mapping (matches backend AGENT_ROLES)
var AGENT_ROLES = {
  "main": "Executive Assistant",
  "atlas": "Coding Specialist",
  "jupiter": "Finance Analyst",
  "jarvis": "General Agent"
};

async function loadAgents() {
  var list = document.getElementById('agent-list');
  list.innerHTML = '<div class="loading">Loading agents...</div>';

  try {
    var res = await fetch(API + '/agents');
    var agents = await res.json();
    var html = '';
    for (var i = 0; i < agents.length; i++) {
      html += renderAgentCard(agents[i], false, AGENT_ROLES);
    }
    list.innerHTML = html || '<div class="loading">No agents configured</div>';
  } catch (e) {
    list.innerHTML = '<div class="loading">Error: ' + esc(e.message) + '</div>';
  }
}

function renderAgentCard(agent, compact, agentRoles) {
  var emoji = getAgentEmoji(agent.id, agent.name);
  var modelStr = typeof agent.model === 'object' ? JSON.stringify(agent.model) : String(agent.model || '');
  
  // Get agent role from roles object (default to "Agent" if not found)
  var role = agentRoles && agentRoles[agent.id] || "Agent";

  var isActive = agent.status === 'active';
  var statusDot = '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:' + (isActive ? '#22c55e' : '#6b7280') + ';margin-right:6px;"></span>';
  var statusText = isActive ? 'Active' : 'Inactive';

  // Format last active from ageMs
  var lastActive = '';
  if (agent.ageMs != null) {
    var mins = Math.floor(agent.ageMs / 60000);
    if (mins < 1) lastActive = 'just now';
    else if (mins < 60) lastActive = mins + 'm ago';
    else if (mins < 1440) lastActive = Math.floor(mins / 60) + 'h ago';
    else lastActive = Math.floor(mins / 1440) + 'd ago';
  }

  var html = '<div class="agent-card clickable" onclick="openAgentDialog(\'' + escAttr(agent.id) + '\', \'' + escAttr(agent.name) + '\')">'
    + '<div class="agent-card-header">'
    + '<div class="agent-avatar-large">' + emoji + '</div>'
    + '<div class="agent-info">'
    + '<div class="agent-name">' + esc(agent.name) + '</div>'
    + '<div class="agent-role">' + statusDot + statusText + '</div>'
    + '</div>'
    + '</div>'
    + '<div class="agent-card-body">';

  if (!compact) {
    html += '<div class="agent-meta">';
    html += '<div class="meta-item"><span class="meta-label">Model</span><span class="meta-value">' + esc(modelStr.length > 30 ? modelStr.substring(0, 30) + '…' : modelStr) + '</span></div>';
    html += '<div class="meta-item"><span class="meta-label">Role</span><span class="meta-value" style="font-size:12px;opacity:0.7;">' + esc(role) + '</span></div>';
    html += '<div class="meta-item"><span class="meta-label">Messages</span><span class="meta-value">' + (agent.messageCount || 0) + '</span></div>';
    if (lastActive) html += '<div class="meta-item"><span class="meta-label">Last Active</span><span class="meta-value">' + esc(lastActive) + '</span></div>';
    html += '</div>';
    if (agent.sessionKey) {
      html += '<div style="font-size:10px;color:var(--text-muted);margin-top:6px;font-family:monospace;opacity:0.6;">' + esc(agent.sessionKey) + '</div>';
    }
  } else {
    if (lastActive) html += '<div style="font-size:11px;color:var(--text-dim);">' + esc(lastActive) + '</div>';
  }

  html += '</div></div>';
  return html;
}

// ── Subagents ──────────────────────────────────────────────────────

function formatTimeAgo(timestampMs) {
  if (!timestampMs) return 'Never';
  var now = Date.now();
  var diff = now - timestampMs;
  var mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  else if (mins < 60) return mins + 'm ago';
  else if (mins < 1440) return Math.floor(mins / 60) + 'h ago';
  else return Math.floor(mins / 1440) + 'd ago';
}

async function loadSubagents() {
  var list = document.getElementById('subagent-list');
  list.innerHTML = '<div class="loading">Loading subagents...</div>';

  try {
    var res = await fetch(API + '/sessions');
    var sessions = await res.json();
    var subagents = sessions.filter(function(s) {
      return s.isSubagent;
    });
    
    var html = '';
    if (subagents.length > 0) {
      for (var i = 0; i < subagents.length; i++) {
        html += renderSubagentCard(subagents[i]);
      }
    } else {
      html = '<div class="loading" style="text-align:center;padding:40px;">No active subagents</div>';
    }
    list.innerHTML = html;
  } catch (e) {
    list.innerHTML = '<div class="loading">Error: ' + esc(e.message) + '</div>';
  }
}

function renderSubagentCard(session) {
  var sessionId = session.id;
  var shortId = sessionId.length > 20 ? sessionId.substring(0, 17) + '...' : sessionId;
  var agentId = session.agentId || 'unknown';
  var model = session.model || 'unknown';
  var channel = session.channel || 'unknown';
  var contextTokens = session.contextTokens || 0;
  var totalTokens = session.totalTokens || 0;
  var updatedAt = session.updatedAt || 0;
  var runCount = session.runCount || null;
  
  var timeAgo = formatTimeAgo(updatedAt);
  
  var tokenInfo = '';
  if (totalTokens > 0) {
    tokenInfo = '<div class="meta-item"><span class="meta-label">Tokens</span><span class="meta-value">' + contextTokens + ' → ' + totalTokens + '</span></div>';
  }
  
  var runInfo = '';
  if (runCount !== null && runCount > 1) {
    runInfo = '<div class="meta-item"><span class="meta-label">Runs</span><span class="meta-value">' + runCount + '</span></div>';
  }

  var html = '<div class="agent-card clickable" style="opacity:0.9;">'
    + '<div class="agent-card-header">'
    + '<div class="agent-avatar-large">🤖</div>'
    + '<div class="agent-info">'
    + '<div class="agent-name">' + esc(agentId) + '</div>'
    + '<div class="agent-role"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#3b82f6;margin-right:6px;"></span>Subagent</div>'
    + '</div>'
    + '</div>'
    + '<div class="agent-card-body">'
    + '<div class="agent-meta">';
  html += '<div class="meta-item"><span class="meta-label">Model</span><span class="meta-value">' + esc(model.length > 30 ? model.substring(0, 30) + '…' : model) + '</span></div>';
  html += '<div class="meta-item"><span class="meta-label">Channel</span><span class="meta-value">' + esc(channel) + '</span></div>';
  html += tokenInfo;
  html += runInfo;
  html += '<div class="meta-item"><span class="meta-label">Updated</span><span class="meta-value">' + esc(timeAgo) + '</span></div>';
  html += '</div>';
  html += '<div style="font-size:9px;color:var(--text-muted);margin-top:6px;font-family:monospace;opacity:0.5;">' + esc(shortId) + '</div>';
  html += '</div></div>';
  
  return html;
}

// ── Agent Dialog ───────────────────────────────────────────────────

var currentAgentDialogId = '';

function openAgentDialog(agentId, agentName) {
  currentAgentDialogId = agentId;
  var emoji = getAgentEmoji(agentId, agentName);
  document.getElementById('agent-dialog-title').textContent = emoji + ' ' + agentName;
  document.getElementById('agent-dialog').classList.remove('hidden');
}

function closeAgentDialog() {
  document.getElementById('agent-dialog').classList.add('hidden');
  currentAgentDialogId = '';
}

document.getElementById('btn-agent-dialog-close').addEventListener('click', closeAgentDialog);

document.getElementById('agent-dialog').addEventListener('click', function(e) {
  if (e.target === this) closeAgentDialog();
});

document.getElementById('btn-agent-state').addEventListener('click', function() {
  var id = currentAgentDialogId;
  closeAgentDialog();
  // Navigate to agents/<agent-id> in file explorer
  loadFiles('agents/' + id);
  document.querySelectorAll('.nav-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.view === 'files'); });
  document.querySelectorAll('.view').forEach(function(v) { v.classList.remove('active'); });
  document.getElementById('view-files').classList.add('active');
});

document.getElementById('btn-agent-workspace').addEventListener('click', function() {
  var id = currentAgentDialogId;
  closeAgentDialog();
  // Navigate to workspace-<agent-id> in file explorer (or workspace for main)
  var wsPath = id === 'main' ? 'workspace' : 'workspace-' + id;
  loadFiles(wsPath);
  document.querySelectorAll('.nav-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.view === 'files'); });
  document.querySelectorAll('.view').forEach(function(v) { v.classList.remove('active'); });
  document.getElementById('view-files').classList.add('active');
});

document.getElementById('btn-refresh-agents').addEventListener('click', loadAgents);
document.getElementById('btn-refresh-subagents').addEventListener('click', loadSubagents);

// ── JSONL Viewer ───────────────────────────────────────────────────

var jsonlPath = '';
var jsonlOffset = 0;
var JSONL_PAGE_SIZE = 20;
var jsonlData = [];
var jsonlTotal = 0;
var jsonlPollTimer = null;
var jsonlLastTotal = 0;
var jsonlAutoScroll = true;

async function openJsonl(path) {
  jsonlPath = path;
  jsonlLastTotal = 0;
  jsonlAutoScroll = true;
  document.getElementById('jsonl-title').textContent = path.split('/').pop();
  document.getElementById('jsonl-search').value = '';
  document.getElementById('jsonl-role-filter').value = '';

  document.querySelectorAll('.view').forEach(function(v) { v.classList.remove('active'); });
  document.getElementById('view-jsonl').classList.add('active');

  try {
    var res = await fetch(API + '/files/jsonl?path=' + encodeURIComponent(path) + '&offset=0&limit=1');
    var data = await res.json();
    jsonlTotal = data.total;
    jsonlOffset = Math.max(0, jsonlTotal - JSONL_PAGE_SIZE);
  } catch (e) { jsonlOffset = 0; }

  await loadJsonlPage();
  startJsonlPolling();
}

async function loadJsonlPage() {
  var container = document.getElementById('jsonl-lines');
  if (!jsonlData.length) container.innerHTML = '<div class="loading">Loading...</div>';

  try {
    var res = await fetch(API + '/files/jsonl?path=' + encodeURIComponent(jsonlPath) + '&offset=' + jsonlOffset + '&limit=' + JSONL_PAGE_SIZE);
    var data = await res.json();
    jsonlData = data.lines;
    jsonlTotal = data.total;
    updateJsonlPagination();
    renderJsonlLines();
  } catch (e) { container.innerHTML = '<div class="loading">Error: ' + esc(e.message) + '</div>'; }
}

function startJsonlPolling() {
  stopJsonlPolling();
  jsonlLastTotal = jsonlTotal;
  jsonlPollTimer = setInterval(async function() {
    if (!document.getElementById('view-jsonl').classList.contains('active')) { stopJsonlPolling(); return; }
    try {
      var res = await fetch(API + '/files/jsonl?path=' + encodeURIComponent(jsonlPath) + '&offset=' + jsonlOffset + '&limit=' + JSONL_PAGE_SIZE);
      var data = await res.json();
      if (data.total !== jsonlLastTotal || data.lines.length !== jsonlData.length) {
        jsonlData = data.lines; jsonlTotal = data.total; jsonlLastTotal = jsonlTotal;
        updateJsonlPagination(); renderJsonlLines();
        if (jsonlAutoScroll && jsonlOffset + JSONL_PAGE_SIZE >= jsonlTotal) {
          document.getElementById('jsonl-lines').scrollTop = 999999;
        }
      }
    } catch (e) {}
  }, 2000);
}

function stopJsonlPolling() { if (jsonlPollTimer) { clearInterval(jsonlPollTimer); jsonlPollTimer = null; } }

function updateJsonlPagination() {
  var end = Math.min(jsonlOffset + JSONL_PAGE_SIZE, jsonlTotal);
  var start = jsonlTotal > 0 ? jsonlOffset + 1 : 0;
  document.getElementById('jsonl-pagination').textContent = start + '–' + end + ' of ' + jsonlTotal;
  document.getElementById('btn-jsonl-prev').disabled = jsonlOffset === 0;
  document.getElementById('btn-jsonl-next').disabled = jsonlOffset + JSONL_PAGE_SIZE >= jsonlTotal;
}

function getPreview(d, raw) {
  if (!d && raw) return String(raw).substring(0, 150);
  if (!d) return '(empty)';
  if (d.content) {
    if (typeof d.content === 'string') return d.content.substring(0, 150);
    if (Array.isArray(d.content)) {
      for (var i = 0; i < d.content.length; i++) {
        if (d.content[i].text) return d.content[i].text.substring(0, 150);
      }
      return JSON.stringify(d.content).substring(0, 150);
    }
    return JSON.stringify(d.content).substring(0, 150);
  }
  if (d.text) return String(d.text).substring(0, 150);
  if (d.message) return String(d.message).substring(0, 150);
  if (d.type) {
    var parts = [d.type];
    if (d.provider) parts.push(d.provider);
    if (d.modelId) parts.push(d.modelId);
    return parts.join(' · ');
  }
  var keys = Object.keys(d);
  var preview = '';
  for (var i = 0; i < Math.min(keys.length, 4); i++) {
    var v = d[keys[i]];
    var vs = typeof v === 'string' ? v.substring(0, 40) : JSON.stringify(v);
    if (vs && vs.length > 40) vs = vs.substring(0, 40) + '…';
    preview += (i > 0 ? ' · ' : '') + keys[i] + ': ' + vs;
  }
  return preview || '(empty)';
}

function getRole(d) { return d ? (d.role || d.type || 'unknown') : 'unknown'; }

function getRoleClass(role) {
  var r = String(role).toLowerCase();
  if (r === 'user') return 'role-user';
  if (r === 'assistant') return 'role-assistant';
  if (r === 'system' || r === 'session') return 'role-system';
  if (r === 'tool' || r === 'tool_result' || r === 'tool_use') return 'role-tool';
  return 'role-unknown';
}

function renderJsonlLines() {
  var container = document.getElementById('jsonl-lines');
  var search = document.getElementById('jsonl-search').value.toLowerCase();
  var roleFilter = document.getElementById('jsonl-role-filter').value;

  var filtered = [];
  for (var i = 0; i < jsonlData.length; i++) {
    var line = jsonlData[i];
    var d = line.data || {};
    if (roleFilter && getRole(d).toLowerCase() !== roleFilter) continue;
    if (search && JSON.stringify(d).toLowerCase().indexOf(search) === -1) continue;
    filtered.push(line);
  }

  if (!filtered.length) { container.innerHTML = '<div class="loading">No matching lines</div>'; return; }

  var html = '';
  for (var i = 0; i < filtered.length; i++) {
    var line = filtered[i];
    var d = line.data || {};
    var role = getRole(d);
    var roleClass = getRoleClass(role);
    var preview = getPreview(d, line.raw);
    var jsonStr = JSON.stringify(line.data || line.raw || '', null, 2);
    var highlighted = syntaxHighlight(jsonStr);

    html += '<div class="jsonl-line" data-index="' + line.index + '">'
      + '<div class="jsonl-line-header" onclick="toggleJsonlLine(this)">'
      + '<span class="jsonl-line-index">#' + line.index + '</span>'
      + '<span class="jsonl-line-role ' + roleClass + '">' + esc(role) + '</span>'
      + '<span class="jsonl-line-preview">' + esc(preview) + '</span>'
      + '<div class="jsonl-line-actions">'
      + '<button onclick="event.stopPropagation(); editJsonlLine(' + line.index + ')" title="Edit">✏️</button>'
      + '<button onclick="event.stopPropagation(); copyJsonlLine(' + line.index + ')" title="Copy">📋</button>'
      + '</div></div>'
      + '<div class="jsonl-line-body"><pre>' + highlighted + '</pre></div></div>';
  }

  container.innerHTML = html;
}

function toggleJsonlLine(header) { header.nextElementSibling.classList.toggle('open'); }

function editJsonlLine(index) {
  var line = jsonlData.find(function(l) { return l.index === index; });
  if (!line) return;
  document.getElementById('jsonl-edit-title').textContent = 'Edit Line #' + index;
  document.getElementById('jsonl-edit-area').value = JSON.stringify(line.data || line.raw, null, 2);
  document.getElementById('jsonl-edit-modal').classList.remove('hidden');
  document.getElementById('jsonl-edit-modal').dataset.index = index;
}

function copyJsonlLine(index) {
  var line = jsonlData.find(function(l) { return l.index === index; });
  if (!line) return;
  navigator.clipboard.writeText(JSON.stringify(line.data || line.raw, null, 2));
  toast('Copied!', 'success');
}

document.getElementById('btn-jsonl-edit-close').addEventListener('click', function() {
  document.getElementById('jsonl-edit-modal').classList.add('hidden');
});

document.getElementById('btn-jsonl-edit-format').addEventListener('click', function() {
  var area = document.getElementById('jsonl-edit-area');
  try { area.value = JSON.stringify(JSON.parse(area.value), null, 2); toast('Formatted!', 'success'); }
  catch (e) { toast('Invalid JSON', 'error'); }
});

document.getElementById('btn-jsonl-edit-save').addEventListener('click', async function() {
  var modal = document.getElementById('jsonl-edit-modal');
  var index = parseInt(modal.dataset.index);
  var content = document.getElementById('jsonl-edit-area').value;
  try { JSON.parse(content); } catch (e) { toast('Invalid JSON', 'error'); return; }
  var compact = JSON.stringify(JSON.parse(content));
  try {
    var res = await fetch(API + '/files/jsonl/line?path=' + encodeURIComponent(jsonlPath) + '&index=' + index, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: compact }),
    });
    if (!res.ok) { toast((await res.json()).detail || 'Save failed', 'error'); return; }
    toast('Saved!', 'success');
    modal.classList.add('hidden');
    await loadJsonlPage();
  } catch (e) { toast('Error: ' + e.message, 'error'); }
});

document.getElementById('btn-jsonl-prev').addEventListener('click', function() {
  jsonlAutoScroll = false;
  jsonlOffset = Math.max(0, jsonlOffset - JSONL_PAGE_SIZE);
  loadJsonlPage();
});

document.getElementById('btn-jsonl-next').addEventListener('click', function() {
  if (jsonlOffset + JSONL_PAGE_SIZE < jsonlTotal) {
    jsonlOffset += JSONL_PAGE_SIZE;
    jsonlAutoScroll = (jsonlOffset + JSONL_PAGE_SIZE >= jsonlTotal);
    loadJsonlPage();
  }
});

document.getElementById('btn-jsonl-last').addEventListener('click', function() {
  jsonlOffset = jsonlTotal > JSONL_PAGE_SIZE ? Math.floor((jsonlTotal - 1) / JSONL_PAGE_SIZE) * JSONL_PAGE_SIZE : 0;
  jsonlAutoScroll = true;
  loadJsonlPage();
});

document.getElementById('btn-jsonl-raw').addEventListener('click', function() {
  stopJsonlPolling();
  currentEditPath = jsonlPath;
  fetch(API + '/files/read?path=' + encodeURIComponent(jsonlPath))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      document.getElementById('editor-title').textContent = data.name;
      document.getElementById('editor').value = data.content;
      document.getElementById('editor-status').textContent = 'jsonl · ' + jsonlPath;
      document.querySelectorAll('.view').forEach(function(v) { v.classList.remove('active'); });
      document.getElementById('view-editor').classList.add('active');
    });
});

document.getElementById('btn-close-jsonl').addEventListener('click', function() {
  stopJsonlPolling();
  showView('files');
  document.querySelectorAll('.nav-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.view === 'files'); });
});

document.getElementById('jsonl-search').addEventListener('input', renderJsonlLines);
document.getElementById('jsonl-role-filter').addEventListener('change', renderJsonlLines);

function syntaxHighlight(json) {
  var escaped = esc(json);
  escaped = escaped.replace(/&quot;([^&]+?)&quot;\s*:/g, '<span class="json-key">&quot;$1&quot;</span>:');
  escaped = escaped.replace(/:\s*&quot;((?:[^&]|&(?!quot;))*)&quot;/g, ': <span class="json-string">&quot;$1&quot;</span>');
  escaped = escaped.replace(/:\s*(-?\d+\.?\d*)/g, ': <span class="json-number">$1</span>');
  escaped = escaped.replace(/:\s*(true|false)/g, ': <span class="json-bool">$1</span>');
  escaped = escaped.replace(/:\s*(null)/g, ': <span class="json-null">$1</span>');
  return escaped;
}

// ── Security Panel ─────────────────────────────────────────────────

var securityPollTimer = null;

async function loadSecurity() {
  stopSecurityPolling();

  try {
    var res = await fetch(API + '/security');
    var data = await res.json();
    renderSecurityThreats(data.threats);
    renderTailscale(data.tailscale);
    renderSSH(data.ssh);
    renderAuthEvents(data.authEvents);
  } catch (e) {
    document.getElementById('security-threats').innerHTML = '<div class="loading">Error loading security data</div>';
  }

  startSecurityPolling();
}

function startSecurityPolling() {
  stopSecurityPolling();
  securityPollTimer = setInterval(function() {
    if (!document.getElementById('view-security').classList.contains('active')) { stopSecurityPolling(); return; }
    loadSecurity();
  }, 30000);
}

function stopSecurityPolling() { if (securityPollTimer) { clearInterval(securityPollTimer); securityPollTimer = null; } }

function renderSecurityThreats(threats) {
  var levelColors = { low: 'green', medium: 'yellow', high: 'red' };
  var levelEmoji = { low: '🟢', medium: '🟡', high: '🔴' };
  var color = levelColors[threats.level] || 'green';
  var emoji = levelEmoji[threats.level] || '🟢';

  var html = '<div class="threat-summary">'
    + '<div class="threat-level-card threat-' + color + '">'
    + '<span class="threat-emoji">' + emoji + '</span>'
    + '<span class="threat-label">Threat Level</span>'
    + '<span class="threat-value">' + threats.level.toUpperCase() + '</span>'
    + '</div>'
    + '<div class="threat-stat-card">'
    + '<span class="threat-stat-icon">🔑</span>'
    + '<span class="threat-stat-value">' + threats.failedSSH + '</span>'
    + '<span class="threat-stat-label">Failed SSH (24h)</span>'
    + '</div>'
    + '<div class="threat-stat-card">'
    + '<span class="threat-stat-icon">🚫</span>'
    + '<span class="threat-stat-value">' + threats.blockedMessages + '</span>'
    + '<span class="threat-stat-label">Blocked Messages</span>'
    + '</div>'
    + '</div>';

  document.getElementById('security-threats').innerHTML = html;
}

function renderTailscale(ts) {
  var container = document.getElementById('security-tailscale');
  if (ts.status === 'off') {
    container.innerHTML = '<div class="sec-detail"><span class="sec-label">Status</span><span class="sec-value" style="color:var(--text-muted)">Off / Not installed</span></div>';
    return;
  }

  var statusColor = ts.status === 'active' ? 'var(--green)' : 'var(--yellow)';
  container.innerHTML = ''
    + '<div class="sec-detail"><span class="sec-label">Status</span><span class="sec-value" style="color:' + statusColor + '">● ' + esc(ts.status) + '</span></div>'
    + '<div class="sec-detail"><span class="sec-label">Hostname</span><span class="sec-value">' + esc(ts.hostname) + '</span></div>'
    + '<div class="sec-detail"><span class="sec-label">IP</span><span class="sec-value" style="font-family:monospace">' + esc(ts.ip) + '</span></div>'
    + '<div class="sec-detail"><span class="sec-label">Peers</span><span class="sec-value">' + ts.peers + ' online / ' + (ts.totalPeers || 0) + ' total</span></div>';
}

function renderSSH(ssh) {
  var container = document.getElementById('security-ssh');
  if (!ssh.recent || !ssh.recent.length) {
    container.innerHTML = '<div class="loading" style="padding:14px; font-size:12px;">No SSH events found</div>';
    return;
  }

  var html = '<div class="ssh-list">';
  for (var i = ssh.recent.length - 1; i >= 0; i--) {
    var ev = ssh.recent[i];
    var statusClass = ev.success ? 'ssh-ok' : 'ssh-fail';
    var statusIcon = ev.success ? '✅' : '❌';
    html += '<div class="ssh-entry ' + statusClass + '">'
      + '<span class="ssh-time">' + esc(ev.timestamp) + '</span>'
      + '<span class="ssh-icon">' + statusIcon + '</span>'
      + '<span class="ssh-user">' + esc(ev.user || '—') + '</span>'
      + '<span class="ssh-ip">' + esc(ev.ip || '—') + '</span>'
      + '<span class="ssh-msg">' + esc(ev.message || '') + '</span>'
      + '</div>';
  }
  html += '</div>';
  container.innerHTML = html;
}

function renderAuthEvents(events) {
  var container = document.getElementById('security-auth');
  if (!events || !events.length) {
    container.innerHTML = '<div class="loading" style="padding:14px; font-size:12px;">No auth events found</div>';
    return;
  }

  var html = '<div class="auth-event-list">';
  for (var i = events.length - 1; i >= 0; i--) {
    var ev = events[i];
    var typeClass = ev.type === 'blocked' ? 'auth-blocked' : ev.type === 'pairing' ? 'auth-pairing' : 'auth-info';
    var typeIcon = ev.type === 'blocked' ? '🚫' : ev.type === 'pairing' ? '🔗' : 'ℹ️';
    html += '<div class="auth-event ' + typeClass + '">'
      + '<span class="auth-time">' + esc(ev.timestamp) + '</span>'
      + '<span class="auth-icon">' + typeIcon + '</span>'
      + '<span class="auth-type">' + esc(ev.type) + '</span>'
      + '<span class="auth-msg">' + esc(ev.message) + '</span>'
      + '</div>';
  }
  html += '</div>';
  container.innerHTML = html;
}

document.getElementById('btn-refresh-security').addEventListener('click', loadSecurity);

// ── Calendar View ──────────────────────────────────────────────────

var calWeekOffset = 0;
var calJobs = [];
var calViewMode = 'week'; // 'week' or 'timeline'
var calAgentFilter = '';

function parseCronDays(expr) {
  // Parse day-of-week field from cron expression (5th field, 0=Sun..6=Sat)
  var parts = (expr || '').split(/\s+/);
  if (parts.length < 5) return [];
  var dow = parts[4];
  if (dow === '*') return [0,1,2,3,4,5,6];
  var days = [];
  var segments = dow.split(',');
  for (var s = 0; s < segments.length; s++) {
    var seg = segments[s];
    if (seg.indexOf('-') !== -1) {
      var range = seg.split('-');
      for (var d = parseInt(range[0]); d <= parseInt(range[1]); d++) days.push(d);
    } else if (seg.match(/^\d+$/)) {
      days.push(parseInt(seg));
    }
  }
  return days;
}

async function loadCalendar() {
  try {
    var res = await fetch(API + '/calendar/jobs');
    var data = await res.json();
    calJobs = Array.isArray(data) ? data : (data.jobs || []);
    // Compute daysOfWeek from cron expression if not present
    for (var j = 0; j < calJobs.length; j++) {
      var cj = calJobs[j];
      if (!cj.daysOfWeek && cj.schedule && cj.schedule.expr) {
        cj.daysOfWeek = parseCronDays(cj.schedule.expr);
      }
      if (!cj.jobId) cj.jobId = cj.id || ('job-' + j);
    }
  } catch (e) {
    calJobs = [];
  }
  populateCalFilter();
  renderCalendarView();
}

function populateCalFilter() {
  var select = document.getElementById('cal-filter-agent');
  if (!select) return;
  
  // Get unique agents from jobs
  var agents = {};
  for (var i = 0; i < calJobs.length; i++) {
    var agent = calJobs[i].agent || 'system';
    agents[agent] = true;
  }
  
  var currentVal = select.value;
  select.innerHTML = '<option value="">All Agents</option>';
  Object.keys(agents).sort().forEach(function(agent) {
    var opt = document.createElement('option');
    opt.value = agent;
    opt.textContent = agent;
    select.appendChild(opt);
  });
  select.value = currentVal;
}

document.getElementById('cal-filter-agent').addEventListener('change', function(e) {
  calAgentFilter = e.target.value;
  renderCalendarView();
});

function renderCalendarView() {
  if (calViewMode === 'timeline') {
    renderTimeline();
  } else {
    renderCalendar();
  }
  renderJobList();
}

function getWeekDates(offset) {
  var now = new Date();
  var day = now.getDay(); // 0=Sun
  var mondayOffset = day === 0 ? -6 : 1 - day;
  var monday = new Date(now);
  monday.setDate(now.getDate() + mondayOffset + (offset * 7));
  monday.setHours(0, 0, 0, 0);

  var dates = [];
  for (var i = 0; i < 7; i++) {
    var d = new Date(monday);
    d.setDate(monday.getDate() + i);
    dates.push(d);
  }
  return dates;
}

function renderCalendar() {
  var dates = getWeekDates(calWeekOffset);
  var dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  var today = new Date();
  today.setHours(0, 0, 0, 0);

  // Week label (IST format: dd/mm/yyyy – dd/mm/yyyy)
  var startStr = formatDateOnly(dates[0]);
  var endStr = formatDateOnly(dates[6]);
  document.getElementById('cal-week-label').textContent = startStr + ' – ' + endStr;

  var html = '<div class="cal-header-row">';
  for (var i = 0; i < 7; i++) {
    var isToday = dates[i].getTime() === today.getTime();
    html += '<div class="cal-header-cell' + (isToday ? ' cal-today' : '') + '">'
      + '<span class="cal-day-name">' + dayNames[i] + '</span>'
      + '<span class="cal-day-num">' + dates[i].getDate() + '</span>'
      + '</div>';
  }
  html += '</div><div class="cal-body-row">';

  for (var i = 0; i < 7; i++) {
    var isToday = dates[i].getTime() === today.getTime();
    var dayJobs = getJobsForDay(i, dates[i]);
    html += '<div class="cal-body-cell' + (isToday ? ' cal-today' : '') + '">';
    for (var j = 0; j < dayJobs.length; j++) {
      var job = dayJobs[j];
      var enabledClass = job.enabled !== false ? 'cal-job-enabled' : 'cal-job-disabled';
      var chipAgent = job.agent ? (' · ' + esc(job.agent)) : '';
      html += '<div class="cal-job-chip ' + enabledClass + '" title="' + escAttr(job.scheduleDesc || '') + '">'
        + esc(job.name || job.jobId || 'Job') + chipAgent + '</div>';
    }
    if (!dayJobs.length) {
      html += '<div class="cal-empty">—</div>';
    }
    html += '</div>';
  }
  html += '</div>';

  document.getElementById('calendar-grid').innerHTML = html;
}

function getJobsForDay(dayIndex, date) {
  // dayIndex: 0=Mon..6=Sun
  // Map to cron day-of-week: 0=Sun..6=Sat
  var cronDow = dayIndex === 6 ? 0 : dayIndex + 1;
  var matched = [];
  for (var i = 0; i < calJobs.length; i++) {
    var job = calJobs[i];
    
    // Apply agent filter
    if (calAgentFilter && job.agent !== calAgentFilter) continue;
    
    var days = job.daysOfWeek || [];
    if (days.length === 0 || days.indexOf(cronDow) !== -1) {
      // For "at" jobs, check if the date matches
      var schedule = job.schedule || {};
      if (schedule.kind === 'at') {
        try {
          var atDate = new Date(schedule.at);
          if (atDate.toDateString() === date.toDateString()) {
            matched.push(job);
          }
        } catch (e) {}
      } else {
        matched.push(job);
      }
    }
  }
  return matched;
}

function renderJobList() {
  // Filter jobs by agent
  var filteredJobs = calJobs;
  if (calAgentFilter) {
    filteredJobs = calJobs.filter(function(j) { return j.agent === calAgentFilter; });
  }
  
  var html = '';
  if (!filteredJobs.length) {
    html = '<div class="cal-no-jobs">'
      + '<div style="font-size:40px; margin-bottom:12px;">📅</div>'
      + '<div style="font-size:14px; color:var(--text-dim)">No scheduled jobs</div>'
      + '<div style="font-size:12px; color:var(--text-muted); margin-top:6px;">' + (calAgentFilter ? 'No jobs for ' + calAgentFilter : 'Create cron jobs via OpenClaw') + '</div>'
      + '</div>';
  } else {
    html = '<h3 class="cal-list-title">All Jobs (' + filteredJobs.length + ')' + (calAgentFilter ? ' for ' + calAgentFilter : '') + '</h3>';
    for (var i = 0; i < filteredJobs.length; i++) {
      var job = filteredJobs[i];
      var statusBadge = job.enabled !== false
        ? '<span class="cal-badge cal-badge-active">Active</span>'
        : '<span class="cal-badge cal-badge-disabled">Disabled</span>';
      var targetBadge = '<span class="cal-badge cal-badge-target">' + esc(job.sessionTarget || '?') + '</span>';
      var agentBadge = job.agent ? '<span class="cal-badge" style="background:' + (getAgentColor(job.agent) || '#6b7280') + ';color:#fff;">' + esc(job.agent) + '</span>' : '';
      var payloadKind = (job.payload || {}).kind || '?';

      html += '<div class="cal-job-row">'
        + '<div class="cal-job-info">'
        + '<div class="cal-job-name">' + esc(job.name || job.jobId || 'Untitled') + '</div>'
        + '<div class="cal-job-meta">' + esc(job.scheduleDesc || '') + ' · ' + esc(payloadKind) + '</div>'
        + '</div>'
        + '<div class="cal-job-badges">' + agentBadge + statusBadge + targetBadge + '</div>'
        + '</div>';
    }
  }
  document.getElementById('cal-job-list').innerHTML = html;
}

function getJobHour(job) {
  var schedule = job.schedule || {};
  if (schedule.kind === 'at') {
    try { return new Date(schedule.at).getHours(); } catch (e) { return -1; }
  }
  if (schedule.kind === 'cron') {
    var parts = (schedule.expr || '').split(' ');
    if (parts.length >= 5) {
      var hour = parts[1];
      if (hour.match(/^\d+$/)) return parseInt(hour);
      if (hour.startsWith('*/')) {
        var interval = parseInt(hour.substring(2));
        if (interval > 0) return -2; // recurring hourly
      }
    }
  }
  return -1;
}

function renderTimeline() {
  var now = new Date();
  var currentHour = now.getHours();
  var currentMin = now.getMinutes();

  // Build hour slots 0-23
  var hourJobs = {};
  for (var i = 0; i < calJobs.length; i++) {
    var job = calJobs[i];
    if (job.enabled === false) continue;
    var h = getJobHour(job);
    if (h === -2) {
      var parts = (job.schedule.expr || '').split(' ');
      var interval = parseInt(parts[1].substring(2));
      for (var hr = 0; hr < 24; hr += interval) {
        if (!hourJobs[hr]) hourJobs[hr] = [];
        hourJobs[hr].push(job);
      }
    } else if (h >= 0 && h <= 23) {
      if (!hourJobs[h]) hourJobs[h] = [];
      hourJobs[h].push(job);
    }
  }

  // Agent colors (use global)

  var html = '<div class="cal-timeline">';
  html += '<div class="cal-tl-header">';
  html += '<div class="cal-tl-header-title">Today\'s Schedule</div>';
  html += '<div class="cal-tl-header-date">' + now.toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }) + '</div>';
  html += '</div>';

  // Summary bar at top
  var totalJobs = 0;
  var nextJob = null;
  var nextHour = -1;
  for (var h = 0; h < 24; h++) {
    if (hourJobs[h]) {
      totalJobs += hourJobs[h].length;
      if (h >= currentHour && !nextJob) {
        nextJob = hourJobs[h][0];
        nextHour = h;
      }
    }
  }
  html += '<div class="cal-tl-summary">';
  html += '<div class="cal-tl-stat"><span class="cal-tl-stat-num">' + totalJobs + '</span> scheduled today</div>';
  if (nextJob && nextHour > currentHour) {
    var ampm = nextHour < 12 ? 'AM' : 'PM';
    var h12 = nextHour % 12 || 12;
    html += '<div class="cal-tl-stat">Next: <strong>' + esc(nextJob.name || 'Job') + '</strong> at ' + h12 + ':00 ' + ampm + '</div>';
  }
  html += '</div>';

  // Timeline
  html += '<div class="cal-tl-track">';

  for (var h = 0; h < 24; h++) {
    var isPast = h < currentHour;
    var isCurrent = h === currentHour;
    var isNext = h === nextHour && h > currentHour;
    var ampm = h < 12 ? 'AM' : 'PM';
    var h12 = h % 12 || 12;
    var timeLabel = h12 + ':00 ' + ampm;
    var jobs = hourJobs[h] || [];
    var hasJobs = jobs.length > 0;

    // Collapse empty past hours (show every 3rd)
    if (!hasJobs && !isCurrent && isPast && h % 3 !== 0) continue;
    // Collapse empty future hours (show every 2nd or if adjacent to job)
    if (!hasJobs && !isCurrent && !isPast) {
      var adjacentToJob = (hourJobs[h-1] && hourJobs[h-1].length) || (hourJobs[h+1] && hourJobs[h+1].length);
      if (!adjacentToJob && h % 3 !== 0) continue;
    }

    var rowClass = 'cal-tl-row';
    if (isCurrent) rowClass += ' cal-tl-current';
    else if (isPast) rowClass += ' cal-tl-past';
    if (hasJobs) rowClass += ' cal-tl-has-jobs';

    html += '<div class="' + rowClass + '">';

    // Time label
    html += '<div class="cal-tl-time">' + timeLabel + '</div>';

    // Vertical line + dot
    html += '<div class="cal-tl-line">';
    if (isCurrent) {
      html += '<div class="cal-tl-now-dot"></div>';
    } else if (hasJobs) {
      html += '<div class="cal-tl-dot-filled"></div>';
    } else {
      html += '<div class="cal-tl-dot-empty"></div>';
    }
    html += '</div>';

    // Content
    html += '<div class="cal-tl-content">';
    if (isCurrent && !hasJobs) {
      html += '<div class="cal-tl-now-label">Now</div>';
    }
    for (var j = 0; j < jobs.length; j++) {
      var job = jobs[j];
      var color = getAgentColor(job.agent);
      var payload = (job.payload || {}).kind || '';
      var icon = payload === 'agentTurn' ? '🤖' : '⚡';
      html += '<div class="cal-tl-card" style="border-left-color:' + color + '">'
        + '<div class="cal-tl-card-header">'
        + '<span class="cal-tl-card-icon">' + icon + '</span>'
        + '<span class="cal-tl-card-name">' + esc(job.name || 'Untitled') + '</span>'
        + '</div>'
        + '<div class="cal-tl-card-meta">'
        + '<span class="cal-tl-card-agent" style="color:' + color + '">' + esc(job.agent || '?') + '</span>'
        + '<span class="cal-tl-card-type">' + esc(payload) + '</span>'
        + (job.sessionTarget ? '<span class="cal-tl-card-target">' + esc(job.sessionTarget) + '</span>' : '')
        + '</div>'
        + '</div>';
    }
    html += '</div></div>';
  }

  html += '</div></div>';
  document.getElementById('calendar-grid').innerHTML = html;
}

document.getElementById('btn-cal-prev').addEventListener('click', function() { calWeekOffset--; renderCalendarView(); });
document.getElementById('btn-cal-next').addEventListener('click', function() { calWeekOffset++; renderCalendarView(); });
document.getElementById('btn-cal-today').addEventListener('click', function() { calWeekOffset = 0; renderCalendarView(); });

document.getElementById('btn-cal-week').addEventListener('click', function() {
  calViewMode = 'week';
  document.getElementById('btn-cal-week').className = 'btn btn-primary cal-toggle-btn active';
  document.getElementById('btn-cal-timeline').className = 'btn btn-secondary cal-toggle-btn';
  document.getElementById('btn-cal-prev').style.display = '';
  document.getElementById('btn-cal-next').style.display = '';
  document.getElementById('cal-week-label').style.display = '';
  renderCalendarView();
});
document.getElementById('btn-cal-timeline').addEventListener('click', function() {
  calViewMode = 'timeline';
  document.getElementById('btn-cal-timeline').className = 'btn btn-primary cal-toggle-btn active';
  document.getElementById('btn-cal-week').className = 'btn btn-secondary cal-toggle-btn';
  document.getElementById('btn-cal-prev').style.display = 'none';
  document.getElementById('btn-cal-next').style.display = 'none';
  document.getElementById('cal-week-label').style.display = 'none';
  renderCalendarView();
});

// ── Activity Feed ──────────────────────────────────────────────────

async function loadActivity() {
  var agentEl = document.getElementById('activity-agent-filter');
  var actionEl = document.getElementById('activity-action-filter');
  var container = document.getElementById('activity-timeline');
  if (!container) return;
  container.innerHTML = '<div class="loading">Loading activity...</div>';

  var agent = agentEl ? agentEl.value : '';
  var action = actionEl ? actionEl.value : '';

  try {
    var params = '?limit=100';
    if (agent) params += '&agent=' + encodeURIComponent(agent);
    if (action) params += '&action=' + encodeURIComponent(action);
    var res = await fetch(API + '/activity' + params);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    var data = await res.json();
    // Backend returns flat array
    var entries = Array.isArray(data) ? data : (data.entries || []);
    renderActivity(entries, entries.length);
  } catch (e) {
    container.innerHTML = '<div class="loading" style="color:var(--red)">Error loading activity: ' + esc(e.message) + '</div>';
  }
}

function renderActivity(entries, total) {
  var container = document.getElementById('activity-timeline');
  if (!entries.length) {
    container.innerHTML = '<div class="activity-empty">'
      + '<div style="font-size:40px; margin-bottom:12px;">📊</div>'
      + '<div style="font-size:14px; color:var(--text-dim)">No activity recorded yet</div>'
      + '<div style="font-size:12px; color:var(--text-muted); margin-top:6px;">Activity is logged automatically when agents perform actions</div>'
      + '</div>';
    return;
  }

  var typeIcons = { session: '💬', cron: '⏰', spawn: '🚀' };
  var html = '<div class="activity-count">' + total + ' total entries</div>';
  for (var i = 0; i < entries.length; i++) {
    var e = entries[i];
    var icon = typeIcons[e.type] || '📌';
    var agentLabel = getAgentLabel(e.agent);
    var timeStr = e.timestamp ? formatIST(e.timestamp) : '';
    var modelStr = e.model ? esc(e.model) : '';

    html += '<div class="activity-entry activity-info">'
      + '<div class="activity-icon">' + icon + '</div>'
      + '<div class="activity-body">'
      + '<div class="activity-main">'
      + '<span class="activity-agent" style="font-weight:600;">' + agentLabel + '</span>'
      + '<span class="activity-action" style="margin-left:6px;opacity:0.7;">' + esc(e.type || 'session') + '</span>'
      + '</div>'
      + '<div class="activity-meta">'
      + '<span class="activity-time">' + esc(timeStr) + '</span>'
      + (modelStr ? '<span class="activity-duration" style="font-size:11px;opacity:0.6;">' + modelStr + '</span>' : '')
      + '</div>'
      + (e.content ? '<div class="activity-details">' + esc(e.content) + '</div>' : '')
      + '</div>'
      + '</div>';
  }
  container.innerHTML = html;
}

function getActionIcon(action) {
  var icons = {
    file_write: '📝', file_read: '📖', task_create: '➕', task_move: '📋',
    task_update: '✏️', task_delete: '🗑️', search: '🔍', command: '⚡',
    build: '🔨', deploy: '🚀', error: '❌', login: '🔑',
    agent_run_start: '🚀', agent_run_end: '✅', tool_start: '🔧', tool_end: '🔧',
    message: '💬',
  };
  return icons[action] || '📌';
}

document.getElementById('btn-refresh-activity').addEventListener('click', loadActivity);
document.getElementById('activity-agent-filter').addEventListener('change', loadActivity);
document.getElementById('activity-action-filter').addEventListener('change', loadActivity);

// ── Command Palette ────────────────────────────────────────────────

var PALETTE_COMMANDS = [
  { icon: '📊', label: 'Dashboard', hint: 'Control board overview', action: function() { switchView('dashboard'); } },
  { icon: '📋', label: 'Kanban', hint: 'Task board', action: function() { switchView('kanban'); } },
  { icon: '🤖', label: 'Agents', hint: 'Agent sessions', action: function() { switchView('agents'); } },
  { icon: '📅', label: 'Calendar', hint: 'Scheduled cron jobs', action: function() { switchView('calendar'); } },
  { icon: '📁', label: 'Files', hint: 'File explorer', action: function() { switchView('files'); } },
  { icon: '📊', label: 'Activity', hint: 'Activity feed', action: function() { switchView('activity'); } },
  { icon: '🛡️', label: 'Security', hint: 'Security panel', action: function() { switchView('security'); } },
  { icon: '➕', label: 'New Task', hint: 'Create a task', action: function() { closePalette(); openNewTask('backlog'); } },
  { icon: '🔄', label: 'Refresh', hint: 'Reload current view', action: function() { refreshCurrentView(); } },
];

var paletteSelectedIdx = 0;
var paletteFileResults = [];
var paletteMode = 'commands'; // 'commands' or 'files'
var paletteSearchTimer = null;

function switchView(name) {
  closePalette();
  document.querySelectorAll('.nav-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.view === name); });
  showView(name);
}

function refreshCurrentView() {
  closePalette();
  var active = document.querySelector('.nav-btn.active');
  if (active) showView(active.dataset.view);
}

function openPalette() {
  document.getElementById('command-palette').classList.remove('hidden');
  var input = document.getElementById('palette-input');
  input.value = ''; input.focus();
  input.placeholder = 'Search commands or files...';
  paletteSelectedIdx = 0;
  paletteMode = 'commands';
  paletteFileResults = [];
  renderPaletteResults('');
}

function closePalette() {
  document.getElementById('command-palette').classList.add('hidden');
  if (paletteSearchTimer) { clearTimeout(paletteSearchTimer); paletteSearchTimer = null; }
}

function getFileSearchIcon(name) {
  var ext = name.split('.').pop().toLowerCase();
  return { json: '📋', jsonl: '📊', md: '📝', py: '🐍', js: '🟨', ts: '🟦', sh: '💻', yaml: '📄', yml: '📄', toml: '📄', txt: '📄', log: '📜', css: '🎨', html: '🌐' }[ext] || '📄';
}

async function searchFiles(query) {
  if (query.length < 2) { paletteFileResults = []; return; }
  try {
    var res = await fetch(API + '/files/search?q=' + encodeURIComponent(query) + '&limit=10');
    paletteFileResults = await res.json();
  } catch (e) { paletteFileResults = []; }
}

function renderPaletteResults(query) {
  var results = document.getElementById('palette-results');
  var q = query.toLowerCase();

  // Command matches
  var cmdFiltered = PALETTE_COMMANDS.filter(function(c) {
    return c.label.toLowerCase().indexOf(q) !== -1 || c.hint.toLowerCase().indexOf(q) !== -1;
  });

  // Build combined list: commands first, then file results
  var allItems = [];

  if (cmdFiltered.length > 0 && q.length < 3) {
    // Short query: show commands
    for (var i = 0; i < cmdFiltered.length; i++) {
      allItems.push({ type: 'cmd', icon: cmdFiltered[i].icon, label: cmdFiltered[i].label, hint: cmdFiltered[i].hint, action: cmdFiltered[i].action });
    }
  } else if (cmdFiltered.length > 0) {
    // Longer query: show top 3 commands, then files
    for (var i = 0; i < Math.min(cmdFiltered.length, 3); i++) {
      allItems.push({ type: 'cmd', icon: cmdFiltered[i].icon, label: cmdFiltered[i].label, hint: cmdFiltered[i].hint, action: cmdFiltered[i].action });
    }
  }

  // File results
  if (paletteFileResults.length > 0) {
    allItems.push({ type: 'separator', label: 'FILES' });
    for (var i = 0; i < paletteFileResults.length; i++) {
      var f = paletteFileResults[i];
      (function(file) {
        allItems.push({
          type: 'file',
          icon: getFileSearchIcon(file.name),
          label: file.name,
          hint: file.path,
          action: function() { closePalette(); openFile(file.path); }
        });
      })(f);
    }
  }

  if (paletteSelectedIdx >= allItems.length) paletteSelectedIdx = 0;
  // Skip separator for selection
  while (paletteSelectedIdx < allItems.length && allItems[paletteSelectedIdx].type === 'separator') paletteSelectedIdx++;

  var html = '';
  var actionIdx = 0;
  for (var i = 0; i < allItems.length; i++) {
    var item = allItems[i];
    if (item.type === 'separator') {
      html += '<div class="palette-separator">' + esc(item.label) + '</div>';
      continue;
    }
    var selected = i === paletteSelectedIdx ? ' selected' : '';
    html += '<div class="palette-item' + selected + '" data-idx="' + i + '">'
      + '<span class="palette-item-icon">' + item.icon + '</span>'
      + '<span class="palette-item-label">' + esc(item.label) + '</span>'
      + '<span class="palette-item-hint">' + esc(item.hint) + '</span></div>';
  }

  if (!allItems.length) {
    html = q.length >= 2
      ? '<div class="palette-item"><span class="palette-item-label" style="color:var(--text-dim)">Searching...</span></div>'
      : '<div class="palette-item"><span class="palette-item-label" style="color:var(--text-dim)">Type to search files...</span></div>';
  }

  results.innerHTML = html;

  // Store for keyboard nav
  results._allItems = allItems;

  results.querySelectorAll('.palette-item[data-idx]').forEach(function(el) {
    el.addEventListener('click', function() {
      var idx = parseInt(this.dataset.idx);
      if (allItems[idx] && allItems[idx].action) allItems[idx].action();
    });
  });
}

document.getElementById('palette-input').addEventListener('input', function() {
  var query = this.value;
  paletteSelectedIdx = 0;

  // Render commands immediately
  renderPaletteResults(query);

  // Debounce file search
  if (paletteSearchTimer) clearTimeout(paletteSearchTimer);
  if (query.length >= 2) {
    paletteSearchTimer = setTimeout(async function() {
      await searchFiles(query);
      renderPaletteResults(query);
    }, 200);
  } else {
    paletteFileResults = [];
  }
});

document.getElementById('palette-input').addEventListener('keydown', function(e) {
  var results = document.getElementById('palette-results');
  var allItems = results._allItems || [];
  var maxIdx = allItems.length - 1;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    paletteSelectedIdx++;
    // Skip separators
    while (paletteSelectedIdx <= maxIdx && allItems[paletteSelectedIdx] && allItems[paletteSelectedIdx].type === 'separator') paletteSelectedIdx++;
    if (paletteSelectedIdx > maxIdx) paletteSelectedIdx = maxIdx;
    renderPaletteResults(this.value);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    paletteSelectedIdx--;
    while (paletteSelectedIdx >= 0 && allItems[paletteSelectedIdx] && allItems[paletteSelectedIdx].type === 'separator') paletteSelectedIdx--;
    if (paletteSelectedIdx < 0) paletteSelectedIdx = 0;
    renderPaletteResults(this.value);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (allItems[paletteSelectedIdx] && allItems[paletteSelectedIdx].action) allItems[paletteSelectedIdx].action();
  } else if (e.key === 'Escape') { closePalette(); }
});

document.getElementById('command-palette').addEventListener('click', function(e) { if (e.target === this) closePalette(); });

// ── Keyboard Shortcuts ─────────────────────────────────────────────

document.addEventListener('keydown', function(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault();
    if (document.getElementById('view-editor').classList.contains('active')) document.getElementById('btn-save').click();
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); var p = document.getElementById('command-palette'); p.classList.contains('hidden') ? openPalette() : closePalette(); }
  if (e.key === 'Escape') closePalette();
});

// ── Sidebar Collapse ───────────────────────────────────────────────

var sidebarCollapsed = false;
var navLabels = {};

document.getElementById('btn-collapse').addEventListener('click', function() {
  sidebarCollapsed = !sidebarCollapsed;
  document.getElementById('sidebar').classList.toggle('collapsed', sidebarCollapsed);
  document.querySelectorAll('.nav-btn').forEach(function(btn) {
    var view = btn.dataset.view;
    if (!navLabels[view]) navLabels[view] = btn.textContent;
    if (sidebarCollapsed) {
      var emoji = navLabels[view].match(/[\u{1F300}-\u{1FAD6}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u);
      btn.textContent = emoji ? emoji[0] : navLabels[view].charAt(0);
      btn.title = navLabels[view];
    } else { btn.textContent = navLabels[view]; btn.title = ''; }
  });
});

// ── Helpers ────────────────────────────────────────────────────────

function getFileIcon(name) {
  var ext = name.split('.').pop().toLowerCase();
  return { json: '📋', jsonl: '📊', md: '📝', py: '🐍', js: '🟨', ts: '🟦', sh: '💻', yaml: '📄', yml: '📄', toml: '📄', txt: '📄', log: '📜' }[ext] || '📄';
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
  return (bytes / 1073741824).toFixed(1) + ' GB';
}

function esc(str) {
  if (str == null) return '';
  var el = document.createElement('span');
  el.textContent = String(str);
  return el.innerHTML;
}

function escAttr(str) { return String(str).replace(/\\/g, '\\\\').replace(/'/g, "\\'"); }

// ── Date Formatting (IST) ─────────────────────────────────────────────
function formatIST(ts) {
  // ts can be ISO string, date string, or timestamp (ms)
  var d = new Date(ts);
  // Use Intl to format in Asia/Calcutta timezone
  var options = {
    timeZone: 'Asia/Calcutta',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    timeZone: 'Asia/Calcutta'
  };
  // en-GB gives dd/mm/yyyy, hour12 gives am/pm
  return d.toLocaleString('en-GB', options);
}

function formatDateOnly(ts) {
  var d = new Date(ts);
  var options = {
    timeZone: 'Asia/Calcutta',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  };
  return d.toLocaleString('en-GB', options);
}

function toast(msg, type) {
  var el = document.createElement('div');
  el.className = 'toast ' + (type || 'success');
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(function() { el.remove(); }, 3000);
}

// ── Mobile Navigation ─────────────────────────────────────────────────

(function() {
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebar-overlay');
  var toggle = document.getElementById('mobile-nav-toggle');
  
  if (!sidebar || !overlay || !toggle) return;
  
  function openMobileMenu() {
    sidebar.classList.add('mobile-open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
  
  function closeMobileMenu() {
    sidebar.classList.remove('mobile-open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }
  
  toggle.addEventListener('click', function(e) {
    e.stopPropagation();
    if (sidebar.classList.contains('mobile-open')) {
      closeMobileMenu();
    } else {
      openMobileMenu();
    }
  });
  
  overlay.addEventListener('click', closeMobileMenu);
  
  // Close menu when clicking nav buttons
  var navBtns = sidebar.querySelectorAll('.nav-btn');
  navBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      closeMobileMenu();
    });
  });
  
  // Close menu on escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
      closeMobileMenu();
    }
  });
  
  // Hide toggle on desktop
  function checkWidth() {
    if (window.innerWidth > 700) {
      closeMobileMenu();
      toggle.style.display = 'none';
    } else {
      toggle.style.display = 'flex';
    }
  }
  
  window.addEventListener('resize', checkWidth);
  checkWidth();
})();

// ── Init ───────────────────────────────────────────────────────────

async function init() {
  await loadDashboardConfig();
  await loadAgentRegistry();
  loadDashboard();
  try {
    var res = await fetch(API + '/stats');
    var stats = await res.json();
    document.getElementById('version-badge').textContent = stats.version;
  } catch (e) {}
}

init();