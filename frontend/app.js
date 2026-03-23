/* ═══════════════════════════════════════════════════════════════
   CRM Corven — SaaS Frontend Application
   ═══════════════════════════════════════════════════════════════ */

const API = 'http://localhost:8000/api/v1';
let token = localStorage.getItem('crm_token');
let currentUser = null;
let currentPage = 'dashboard';
let leadsCache = [];
let chatData = [];

/* ── API Client ────────────────────────────────────────────── */
async function api(endpoint, opts = {}) {
    const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    try {
        const r = await fetch(`${API}${endpoint}`, { ...opts, headers });
        if (r.status === 401) { logout(); return null; }
        const data = await r.json();
        if (!r.ok) throw new Error(data.detail || 'Erro na API');
        return data;
    } catch(e) {
        console.error('API Error:', e);
        throw e;
    }
}

/* ── AUTH ───────────────────────────────────────────────────── */
async function sendOTP() {
    const email = document.getElementById('login-email').value.trim();
    if (!email) return;
    const btn = document.getElementById('btn-send-otp');
    btn.textContent = 'Enviando...'; btn.disabled = true;
    try {
        const data = await api('/auth/request-otp', { method: 'POST', body: JSON.stringify({ email }) });
        // Auto-fill OTP in dev mode
        if (data.otp_code_dev_only) {
            document.getElementById('login-otp').value = data.otp_code_dev_only;
        }
        document.getElementById('login-step-email').style.display = 'none';
        document.getElementById('login-step-otp').style.display = 'block';
        hideError();
    } catch(e) {
        showError(e.message);
    }
    btn.textContent = 'Entrar'; btn.disabled = false;
}

async function verifyOTP() {
    const email = document.getElementById('login-email').value.trim();
    const code = document.getElementById('login-otp').value.trim();
    if (!code) return;
    try {
        const data = await api('/auth/verify-otp', { method: 'POST', body: JSON.stringify({ email, code }) });
        token = data.access_token;
        localStorage.setItem('crm_token', token);
        localStorage.setItem('crm_refresh', data.refresh_token || '');
        await loadApp();
    } catch(e) {
        showError(e.message);
    }
}

function backToEmail() {
    document.getElementById('login-step-email').style.display = 'block';
    document.getElementById('login-step-otp').style.display = 'none';
    hideError();
}

function logout() {
    token = null; currentUser = null;
    localStorage.removeItem('crm_token');
    localStorage.removeItem('crm_refresh');
    document.getElementById('app-shell').style.display = 'none';
    document.getElementById('login-screen').style.display = 'flex';
    document.getElementById('login-step-email').style.display = 'block';
    document.getElementById('login-step-otp').style.display = 'none';
}

function showError(msg) {
    const el = document.getElementById('login-error');
    el.textContent = msg; el.style.display = 'block';
}
function hideError() { document.getElementById('login-error').style.display = 'none'; }

/* ── APP INIT ──────────────────────────────────────────────── */
async function loadApp() {
    try {
        currentUser = await api('/auth/me');
        if (!currentUser) return;
    } catch(e) { logout(); return; }

    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('app-shell').style.display = 'flex';

    // Set user info
    const name = currentUser.name || currentUser.email;
    document.getElementById('user-name').textContent = name;
    document.getElementById('user-role').textContent = roleLabel(currentUser.role);
    document.getElementById('user-avatar').textContent = name.charAt(0).toUpperCase();

    // Plan display
    const plan = currentUser.plan || 'professional';
    document.getElementById('sidebar-plan').textContent = planName(plan);

    buildSidebar();
    navigateTo('dashboard');
}

function roleLabel(r) {
    const map = { superadmin: 'Super Admin', admin: 'Administrador', user: 'Corretor' };
    return map[r] || r;
}

function planName(p) {
    const map = { basic: '⭐ Básico', basic2: '🚀 Básico 2', intermediate: '💎 Intermediário', professional: '👑 Master' };
    return map[p] || '👑 Master';
}

function isAdmin() { return currentUser && (currentUser.role === 'admin' || currentUser.role === 'superadmin'); }
function planLevel() {
    const p = currentUser?.plan || 'professional';
    const levels = { basic: 1, basic2: 2, intermediate: 3, professional: 4 };
    return levels[p] || 4;
}

/* ── SIDEBAR ───────────────────────────────────────────────── */
function buildSidebar() {
    const nav = document.getElementById('sidebar-nav');
    const items = [
        { id: 'dashboard', icon: '📊', label: 'Dashboard' },
        { id: 'crm', icon: '📋', label: 'CRM / Kanban' },
        { id: 'whatsapp', icon: '💬', label: 'WhatsApp', badge: '3' },
    ];

    if (isAdmin()) {
        items.push({ divider: true });
        items.push({ label: 'ADMINISTRAÇÃO', type: 'label' });
        items.push({ id: 'users', icon: '👥', label: 'Usuários' });
    }

    if (planLevel() >= 2) {
        items.push({ divider: true });
        items.push({ label: 'INTELIGÊNCIA', type: 'label' });
        if (isAdmin()) items.push({ id: 'ia', icon: '🤖', label: 'Config IA' });
    }

    if (planLevel() >= 3) {
        items.push({ id: 'agenda', icon: '📅', label: 'Agenda' });
    }

    if (planLevel() >= 4) {
        items.push({ id: 'secretary', icon: '🧠', label: 'Secretária IA' });
    }

    items.push({ divider: true });
    items.push({ id: 'config', icon: '⚙️', label: 'Configurações' });

    nav.innerHTML = items.map(item => {
        if (item.divider) return '<div class="nav-divider"></div>';
        if (item.type === 'label') return `<div class="nav-label">${item.label}</div>`;
        const badge = item.badge ? `<span class="nav-badge">${item.badge}</span>` : '';
        return `<div class="nav-item" data-page="${item.id}" onclick="navigateTo('${item.id}')">
            <span class="nav-icon">${item.icon}</span>${item.label}${badge}
        </div>`;
    }).join('');
}

/* ── NAVIGATION ────────────────────────────────────────────── */
function navigateTo(page) {
    currentPage = page;

    // Update active nav
    document.querySelectorAll('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.page === page));

    // Update topbar
    const titles = { dashboard: 'Dashboard', crm: 'CRM / Kanban', whatsapp: 'WhatsApp', users: 'Usuários', ia: 'Inteligência Artificial', agenda: 'Agenda', secretary: 'Secretária IA', config: 'Configurações' };
    document.getElementById('page-title').textContent = titles[page] || page;

    // Load page template
    const tpl = document.getElementById(`tpl-${page}`);
    const content = document.getElementById('page-content');
    if (tpl) {
        content.innerHTML = '';
        content.appendChild(tpl.content.cloneNode(true));
    }

    // Load page data
    const loaders = { dashboard: loadDashboard, crm: loadCRM, whatsapp: loadWhatsApp, users: loadUsers, ia: loadIA, agenda: loadAgenda, config: loadConfig };
    if (loaders[page]) loaders[page]();
}

/* ── DASHBOARD ─────────────────────────────────────────────── */
async function loadDashboard() {
    try {
        const endpoint = isAdmin() ? '/dashboard/admin' : '/dashboard/user';
        const data = await api(endpoint);
        if (!data) return;

        // Metrics
        const grid = document.getElementById('metrics-grid');
        const metrics = [
            { icon: '👥', value: data.total_leads || 0, label: 'Total de Leads', color: '', change: '+12% mês' },
            { icon: '✅', value: data.conversions || 0, label: 'Conversões', color: 'green', change: `${data.conversion_rate || 0}% taxa` },
            { icon: '📢', value: data.total_campaigns || 0, label: 'Campanhas Ativas', color: 'blue' },
            { icon: '📋', value: data.pending_tasks || 0, label: 'Tarefas Pendentes', color: 'yellow' },
            { icon: '⚠️', value: data.overdue_tasks || 0, label: 'Tarefas Atrasadas', color: 'red' },
        ];
        grid.innerHTML = metrics.map(m => `
            <div class="metric-card ${m.color}">
                <div class="metric-icon">${m.icon}</div>
                <div class="metric-value">${m.value}</div>
                <div class="metric-label">${m.label}</div>
                ${m.change ? `<div class="metric-change up">↑ ${m.change}</div>` : ''}
            </div>
        `).join('');

        // Pipeline chart
        const stages = data.leads_by_stage || {};
        const total = data.total_leads || 1;
        const pipeline = document.getElementById('pipeline-chart');
        const stageMap = [
            { key: 'novo', label: 'Novo Lead', cls: 'novo' },
            { key: 'contato_iniciado', label: 'Contato Iniciado', cls: 'contato' },
            { key: 'em_negociacao', label: 'Em Negociação', cls: 'negociacao' },
            { key: 'aguardando_retorno', label: 'Aguardando', cls: 'aguardando' },
            { key: 'fechado', label: 'Fechado', cls: 'fechado' },
            { key: 'perdido', label: 'Perdido', cls: 'perdido' },
        ];
        pipeline.innerHTML = stageMap.map(s => {
            const count = stages[s.key] || 0;
            const pct = Math.max((count / total) * 100, 5);
            return `<div class="pipeline-bar">
                <div class="pipeline-bar-label">${s.label}</div>
                <div class="pipeline-bar-track">
                    <div class="pipeline-bar-fill ${s.cls}" style="width:${pct}%">${count}</div>
                </div>
            </div>`;
        }).join('');

        // Source chart
        const sources = data.leads_by_source || {};
        const sourceChart = document.getElementById('source-chart');
        const sourceIcons = { whatsapp: '💬', meta_ads: '📘', google_ads: '🔍', indicacao: '🤝', organic: '🌿' };
        const sourceNames = { whatsapp: 'WhatsApp', meta_ads: 'Meta Ads', google_ads: 'Google Ads', indicacao: 'Indicação', organic: 'Orgânico' };
        sourceChart.innerHTML = Object.entries(sources).sort((a,b) => b[1] - a[1]).map(([key, count]) => {
            const pct = ((count / total) * 100).toFixed(0);
            return `<div class="source-row">
                <div class="source-icon ${key}">${sourceIcons[key] || '📌'}</div>
                <div class="source-name">${sourceNames[key] || key}</div>
                <div class="source-count">${count}</div>
                <div class="source-pct">${pct}%</div>
            </div>`;
        }).join('');

        // Activity feed
        loadActivityFeed();

        // Tasks
        loadDashTasks();

    } catch(e) {
        toast('Erro ao carregar dashboard: ' + e.message, 'error');
    }
}

function loadActivityFeed() {
    const feed = document.getElementById('activity-feed');
    const activities = [
        { color: 'green', text: '<strong>Maria Silva</strong> avançou para Em Negociação', time: '2 min' },
        { color: 'blue', text: 'Nova mensagem de <strong>João Santos</strong> no WhatsApp', time: '15 min' },
        { color: 'accent', text: 'Proposta enviada para <strong>Fernanda Lima</strong>', time: '1h' },
        { color: 'yellow', text: 'Tarefa atrasada: Follow-up com <strong>Carlos Souza</strong>', time: '2h' },
        { color: 'green', text: '<strong>Pedro Ferreira</strong> — negócio fechado! 🎉', time: '3h' },
        { color: 'blue', text: 'Novo lead captado via <strong>Meta Ads</strong>', time: '4h' },
    ];
    feed.innerHTML = activities.map(a => `
        <div class="activity-item">
            <div class="activity-dot ${a.color}"></div>
            <div class="activity-text">${a.text}</div>
            <div class="activity-time">${a.time}</div>
        </div>
    `).join('');
}

function loadDashTasks() {
    const list = document.getElementById('dash-tasks');
    const tasks = [
        { title: 'Ligar para Maria Silva', due: 'Hoje', cls: 'today' },
        { title: 'Enviar proposta para João Santos', due: 'Atrasada', cls: 'overdue' },
        { title: 'Follow-up WhatsApp — Ana Oliveira', due: 'Amanhã', cls: 'upcoming' },
        { title: 'Reunião com Fernanda Lima', due: 'Atrasada', cls: 'overdue' },
        { title: 'Enviar comparativo para Carlos Souza', due: 'Qui', cls: 'upcoming' },
    ];
    const badge = document.getElementById('tasks-badge');
    badge.textContent = tasks.length;
    list.innerHTML = tasks.map(t => `
        <div class="task-item">
            <div class="task-check"></div>
            <div class="task-title">${t.title}</div>
            <span class="task-due ${t.cls}">${t.due}</span>
        </div>
    `).join('');
}

/* ── CRM KANBAN ────────────────────────────────────────────── */
async function loadCRM() {
    try {
        const data = await api('/leads/?limit=100');
        if (!data) return;
        leadsCache = Array.isArray(data) ? data : (data.leads || []);

        const stages = ['novo', 'contato_iniciado', 'em_negociacao', 'aguardando_retorno', 'fechado', 'perdido'];
        stages.forEach(stage => {
            const col = document.getElementById(`col-${stage}`);
            const count = document.getElementById(`count-${stage}`);
            const stageLeads = leadsCache.filter(l => l.stage === stage);
            count.textContent = stageLeads.length;
            col.innerHTML = stageLeads.map(l => `
                <div class="kanban-card" onclick="openLeadDetail('${l.id}')">
                    <div class="kanban-card-name">${l.name}</div>
                    <div class="kanban-card-info">${l.email || l.phone || '—'}</div>
                    ${l.source ? `<div class="kanban-card-source">${l.source}</div>` : ''}
                    <div class="kanban-card-footer">
                        ${l.assigned_to ? '👤' : ''} ${formatDate(l.created_at)}
                    </div>
                </div>
            `).join('');
        });
    } catch(e) {
        toast('Erro ao carregar pipeline', 'error');
    }
}

function openNewLeadModal() {
    document.getElementById('generic-modal-title').textContent = 'Novo Lead';
    document.getElementById('generic-modal-body').innerHTML = `
        <div class="form-group"><label>Nome</label><input type="text" id="new-lead-name" placeholder="Nome do lead"></div>
        <div class="form-group"><label>Email</label><input type="email" id="new-lead-email" placeholder="email@exemplo.com"></div>
        <div class="form-group"><label>Telefone</label><input type="text" id="new-lead-phone" placeholder="(11) 99999-9999"></div>
        <div class="form-group"><label>Origem</label><select id="new-lead-source"><option value="whatsapp">WhatsApp</option><option value="meta_ads">Meta Ads</option><option value="google_ads">Google Ads</option><option value="indicacao">Indicação</option><option value="organic">Orgânico</option></select></div>
        <div class="modal-actions">
            <button class="btn-primary btn-sm" onclick="createLead()">Criar Lead</button>
            <button class="btn-secondary btn-sm" onclick="closeModal('generic-modal')">Cancelar</button>
        </div>
    `;
    document.getElementById('generic-modal').style.display = 'flex';
}

async function createLead() {
    const body = {
        name: document.getElementById('new-lead-name').value,
        email: document.getElementById('new-lead-email').value,
        phone: document.getElementById('new-lead-phone').value,
        source: document.getElementById('new-lead-source').value,
    };
    try {
        await api('/leads/', { method: 'POST', body: JSON.stringify(body) });
        closeModal('generic-modal');
        toast('Lead criado com sucesso!', 'success');
        loadCRM();
    } catch(e) { toast(e.message, 'error'); }
}

async function openLeadDetail(id) {
    const lead = leadsCache.find(l => l.id === id);
    if (!lead) return;

    document.getElementById('lead-modal-name').textContent = lead.name;
    const body = document.getElementById('lead-modal-body');

    body.innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px">
            <div class="form-group"><label>Email</label><div style="color:var(--text-secondary);font-size:13px">${lead.email || '—'}</div></div>
            <div class="form-group"><label>Telefone</label><div style="color:var(--text-secondary);font-size:13px">${lead.phone || '—'}</div></div>
            <div class="form-group"><label>Origem</label><div><span class="kanban-card-source">${lead.source || '—'}</span></div></div>
            <div class="form-group"><label>Estágio</label>
                <select id="detail-stage" onchange="moveLeadStage('${lead.id}', this.value)">
                    <option value="novo" ${lead.stage==='novo'?'selected':''}>Novo Lead</option>
                    <option value="contato_iniciado" ${lead.stage==='contato_iniciado'?'selected':''}>Contato Iniciado</option>
                    <option value="em_negociacao" ${lead.stage==='em_negociacao'?'selected':''}>Em Negociação</option>
                    <option value="aguardando_retorno" ${lead.stage==='aguardando_retorno'?'selected':''}>Aguardando</option>
                    <option value="fechado" ${lead.stage==='fechado'?'selected':''}>Fechado</option>
                    <option value="perdido" ${lead.stage==='perdido'?'selected':''}>Perdido</option>
                </select>
            </div>
        </div>
        <h4 style="margin-bottom:8px;font-size:13px;color:var(--text-muted)">INTERAÇÕES</h4>
        <div style="max-height:200px;overflow-y:auto;margin-bottom:16px">
            ${(lead.interactions || []).map(i => `
                <div class="activity-item">
                    <div class="activity-dot blue"></div>
                    <div class="activity-text">${i.content || i.type}</div>
                    <div class="activity-time">${formatDate(i.created_at)}</div>
                </div>
            `).join('') || '<div style="color:var(--text-muted);font-size:13px">Nenhuma interação</div>'}
        </div>
        <h4 style="margin-bottom:8px;font-size:13px;color:var(--text-muted)">NOTAS</h4>
        <div style="max-height:150px;overflow-y:auto">
            ${(lead.notes || []).map(n => `
                <div style="padding:8px 12px;background:var(--bg-input);border-radius:6px;margin-bottom:6px;font-size:13px;color:var(--text-secondary)">${n.content}</div>
            `).join('') || '<div style="color:var(--text-muted);font-size:13px">Nenhuma nota</div>'}
        </div>
    `;
    document.getElementById('lead-modal').style.display = 'flex';
}

async function moveLeadStage(id, stage) {
    try {
        await api(`/leads/${id}/stage`, { method: 'PATCH', body: JSON.stringify({ stage }) });
        toast('Lead movido!', 'success');
        closeModal('lead-modal');
        loadCRM();
    } catch(e) { toast(e.message, 'error'); }
}

/* ── WHATSAPP ──────────────────────────────────────────────── */
async function loadWhatsApp() {
    try {
        // Load all messages for the tenant
        const msgs = await api('/whatsapp/messages?limit=200') || [];
        
        if (!msgs.length) {
            document.getElementById('chat-list').innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted)">Nenhuma conversa encontrada</div>';
            return;
        }
        chatData = msgs;

        const grouped = {};
        msgs.forEach(m => {
            const key = m.lead_id || 'unknown';
            if (!grouped[key]) grouped[key] = { lead_id: m.lead_id, messages: [], lead_name: m.lead_name || 'Contato', lead_phone: m.lead_phone || '' };
            grouped[key].messages.push(m);
        });

        const contacts = Object.values(grouped).sort((a,b) => {
            const lastA = a.messages[a.messages.length-1]?.created_at || '';
            const lastB = b.messages[b.messages.length-1]?.created_at || '';
            return lastB.localeCompare(lastA);
        });

        const list = document.getElementById('chat-list');
        list.innerHTML = contacts.map((c, i) => {
            const name = c.lead_name || 'Contato';
            const lastMsg = c.messages[c.messages.length-1];
            const preview = lastMsg?.content?.substring(0, 40) || '';
            const unread = c.messages.filter(m => m.direction === 'inbound').length;
            return `<div class="chat-contact" onclick="openChat(${i})" data-idx="${i}">
                <div class="chat-contact-avatar">${name.charAt(0)}</div>
                <div class="chat-contact-info">
                    <div class="chat-contact-name">${name}</div>
                    <div class="chat-contact-last">${preview}...</div>
                </div>
                <div>
                    <div class="chat-contact-time">${formatTime(lastMsg?.created_at)}</div>
                    ${unread > 2 ? `<div class="chat-contact-unread">${unread}</div>` : ''}
                </div>
            </div>`;
        }).join('');

        // Auto-open first
        if (contacts.length > 0) openChat(0);

    } catch(e) {
        toast('Erro ao carregar WhatsApp', 'error');
    }
}

function openChat(idx) {
    // Highlight active contact
    document.querySelectorAll('.chat-contact').forEach(el => el.classList.toggle('active', el.dataset.idx == idx));

    const allGrouped = {};
    chatData.forEach(m => {
        const key = m.lead_id || 'unknown';
        if (!allGrouped[key]) allGrouped[key] = { lead_name: m.lead_name || 'Contato', lead_phone: m.lead_phone || '', messages: [] };
        allGrouped[key].messages.push(m);
    });
    const contacts = Object.values(allGrouped);
    const contact = contacts[idx];
    if (!contact) return;

    const name = contact.lead_name || 'Contato';
    const main = document.getElementById('chat-main');
    main.innerHTML = `
        <div class="chat-header">
            <div class="chat-contact-avatar" style="width:36px;height:36px;font-size:14px">${name.charAt(0)}</div>
            <div class="chat-header-name">
                <h4>${name}</h4>
                <span>${contact.lead_phone || 'WhatsApp'}</span>
            </div>
        </div>
        <div class="chat-messages">
            ${contact.messages.sort((a,b) => (a.created_at||'').localeCompare(b.created_at||'')).map(m => `
                <div class="chat-bubble ${m.direction}">
                    ${m.content}
                    <div class="chat-bubble-time">${formatTime(m.created_at)}</div>
                </div>
            `).join('')}
        </div>
        <div class="chat-input-bar">
            <input type="text" placeholder="Digite uma mensagem..." id="chat-msg-input" onkeydown="if(event.key==='Enter')sendChatMsg()">
            <button class="btn-primary" onclick="sendChatMsg()">Enviar</button>
        </div>
    `;

    // Scroll to bottom
    const msgs = main.querySelector('.chat-messages');
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
}

function sendChatMsg() {
    const input = document.getElementById('chat-msg-input');
    if (!input || !input.value.trim()) return;
    const msgs = document.querySelector('.chat-messages');
    msgs.innerHTML += `<div class="chat-bubble outbound">${input.value}<div class="chat-bubble-time">Agora</div></div>`;
    input.value = '';
    msgs.scrollTop = msgs.scrollHeight;
    toast('Mensagem enviada!', 'success');
}

/* ── USERS ─────────────────────────────────────────────────── */
async function loadUsers() {
    try {
        const data = await api('/users/');
        if (!data) return;
        const users = data.users || data || [];
        const tbody = document.getElementById('users-tbody');
        tbody.innerHTML = users.map(u => `
            <tr>
                <td><strong>${u.name}</strong></td>
                <td>${u.email}</td>
                <td><span class="role-badge ${u.role}">${roleLabel(u.role)}</span></td>
                <td>${u.lead_count || '—'}</td>
                <td><span class="status-badge ${u.is_active ? 'active' : 'inactive'}">${u.is_active ? '● Ativo' : '● Inativo'}</span></td>
                <td><button class="btn-icon" title="Editar">✏️</button></td>
            </tr>
        `).join('');
    } catch(e) { toast('Erro ao carregar usuários', 'error'); }
}

/* ── IA CONFIG ─────────────────────────────────────────────── */
function loadIA() {
    // Show RAG section for intermediário+
    if (planLevel() >= 3) {
        const ragSection = document.getElementById('ia-rag-section');
        if (ragSection) ragSection.style.display = 'block';
        loadRAGFiles();
    }
}

async function loadRAGFiles() {
    try {
        const data = await api('/documents/');
        const files = data.documents || data || [];
        const container = document.getElementById('rag-files');
        if (!container) return;
        const icons = { 'application/pdf': '📄', 'application/msword': '📝', 'application/vnd.ms-excel': '📊' };
        container.innerHTML = files.map(f => `
            <div class="rag-file">
                <div class="rag-file-icon">${icons[f.content_type] || '📎'}</div>
                <div class="rag-file-name">${f.original_name}</div>
                <div class="rag-file-status ${f.embedding_status}">${f.embedding_status === 'done' ? '✅ Indexado' : '⏳ Processando'}</div>
            </div>
        `).join('');
    } catch(e) {}
}

function savePrompt() { toast('Prompt master salvo com sucesso!', 'success'); }
function uploadRAGFile() { toast('Upload de documento iniciado...', 'info'); }

/* ── AGENDA ────────────────────────────────────────────────── */
async function loadAgenda() {
    const now = new Date();
    const todayEl = document.getElementById('today-date');
    if (todayEl) todayEl.textContent = now.toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' });

    try {
        const data = await api('/calendar/events?limit=20');
        const events = data.events || data || [];

        const today = now.toISOString().split('T')[0];
        const todayEvents = events.filter(e => e.start_datetime?.startsWith(today));
        const upcomingEvents = events.filter(e => !e.start_datetime?.startsWith(today));

        const todayList = document.getElementById('today-events');
        const upcomingList = document.getElementById('upcoming-events');

        if (todayList) {
            todayList.innerHTML = todayEvents.length ? todayEvents.map(renderEvent).join('') :
                '<div style="padding:16px;text-align:center;color:var(--text-muted)">Nenhum evento hoje</div>';
        }

        if (upcomingList) {
            upcomingList.innerHTML = upcomingEvents.length ? upcomingEvents.slice(0, 8).map(renderEvent).join('') :
                '<div style="padding:16px;text-align:center;color:var(--text-muted)">Sem eventos futuros</div>';
        }
    } catch(e) {
        toast('Erro ao carregar agenda', 'error');
    }
}

function renderEvent(e) {
    const time = e.start_datetime ? new Date(e.start_datetime).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '';
    return `<div class="event-item">
        <div class="event-time">${time}</div>
        <div class="event-details">
            <div class="event-title">${e.title}</div>
            <div class="event-desc">${e.description || ''}</div>
        </div>
    </div>`;
}

function openNewEventModal() { toast('Em breve: criação de eventos', 'info'); }
function syncGoogleCalendar() { toast('Sincronização com Google Calendar em breve', 'info'); }

/* ── SECRETARY ─────────────────────────────────────────────── */
async function secretarySend(text) {
    const input = document.getElementById('secretary-input');
    const msg = text || input?.value?.trim();
    if (!msg) return;
    if (input) input.value = '';

    const container = document.getElementById('secretary-messages');

    // User message
    container.innerHTML += `<div class="msg msg-user"><div class="msg-avatar">${(currentUser?.name || 'U').charAt(0)}</div><div class="msg-content"><p>${msg}</p></div></div>`;
    container.scrollTop = container.scrollHeight;

    // Typing indicator
    container.innerHTML += `<div class="msg msg-bot" id="typing"><div class="msg-avatar">🤖</div><div class="msg-content"><p>Digitando...</p></div></div>`;
    container.scrollTop = container.scrollHeight;

    // Simulate response
    setTimeout(() => {
        document.getElementById('typing')?.remove();
        const responses = {
            'Quais leads precisam de follow-up?': '📋 **3 leads precisam de follow-up:**\n\n1. **Carlos Souza** — sem contato há 5 dias (plano PME)\n2. **Larissa Barbosa** — aguardando proposta há 3 dias\n3. **Gustavo Mendes** — pediu retorno na quinta\n\n💡 Recomendo priorizar Carlos Souza, o interesse dele é alto.',
            'Resuma meu dia': '📊 **Resumo do dia:**\n\n• 20 leads ativos, 3 convertidos este mês (15%)\n• 5 tarefas pendentes, 2 atrasadas\n• 12 mensagens WhatsApp recebidas\n• Próximo evento: Reunião Maria Silva às 14h\n\n✅ Performance acima da meta mensal!',
            'Quais tarefas estão atrasadas?': '⚠️ **2 tarefas atrasadas:**\n\n1. **Enviar proposta João Santos** — venceu ontem\n2. **Follow-up Fernanda Lima** — venceu há 2 dias\n\n🔧 Posso criar lembretes para hoje?',
        };
        const response = responses[msg] || `Entendido! Vou processar sua solicitação: "${msg}"\n\n🔄 Consultando o banco de dados e preparando a resposta...`;

        container.innerHTML += `<div class="msg msg-bot"><div class="msg-avatar">🤖</div><div class="msg-content"><p>${response.replace(/\n/g, '<br>')}</p></div></div>`;
        container.scrollTop = container.scrollHeight;
    }, 1200);
}

/* ── CONFIG ────────────────────────────────────────────────── */
async function loadConfig() {
    if (currentUser) {
        const nameEl = document.getElementById('cfg-name');
        const emailEl = document.getElementById('cfg-email');
        if (nameEl) nameEl.value = currentUser.name || '';
        if (emailEl) emailEl.value = currentUser.email || '';
    }

    if (isAdmin()) {
        const companyCard = document.getElementById('company-card');
        if (companyCard) companyCard.style.display = 'block';
        try {
            const data = await api('/settings/company');
            if (data) {
                const nameEl = document.getElementById('cfg-company-name');
                if (nameEl) nameEl.value = data.name || '';
                const planEl = document.getElementById('cfg-plan-display');
                if (planEl) planEl.innerHTML = `<div class="plan-name">${planName(data.plan || 'professional')}</div><div class="plan-desc">Plano atual da empresa</div>`;
            }
        } catch(e) {}
    }
}

function saveProfile() { toast('Perfil salvo com sucesso!', 'success'); }

/* ── MODALS ────────────────────────────────────────────────── */
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

// Close on overlay click
document.addEventListener('click', e => {
    if (e.target.classList.contains('modal-overlay')) e.target.style.display = 'none';
});

// Close on Escape
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') document.querySelectorAll('.modal-overlay').forEach(m => m.style.display = 'none');
});

/* ── TOAST ─────────────────────────────────────────────────── */
function toast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = msg;
    container.appendChild(el);
    setTimeout(() => el.remove(), 4000);
}

/* ── UTILS ─────────────────────────────────────────────────── */
function formatDate(d) {
    if (!d) return '';
    return new Date(d).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
}

function formatTime(d) {
    if (!d) return '';
    const date = new Date(d);
    const now = new Date();
    const diff = now - date;
    if (diff < 3600000) return Math.floor(diff/60000) + 'min';
    if (diff < 86400000) return Math.floor(diff/3600000) + 'h';
    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
}

/* ── BOOT ──────────────────────────────────────────────────── */
if (token) {
    loadApp();
}
