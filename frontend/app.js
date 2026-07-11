const apiUrl = (path) => `/api/tenants/${currentTenant}${path}`;

let currentTenant = "";
let mode = "OVERVIEW";
let expandedClusters = new Set();
let snapshotGraph = null;
let investigationRoot = null;
let baseElementIds = new Set();
let expandedPool = { nodes: new Map(), edges: new Map() };
let edgeSeq = 0;
let pathFindingMode = false;
let pathSource = null;
let pathTarget = null;
let currentSelectedNode = null;
let currentLayout = 'cose';

const cy = cytoscape({
  container: document.getElementById('cy'),
  style: [
    {
      selector: 'node',
      style: {
        'background-color': 'data(color)',
        'label': 'data(label)',
        'color': '#eaeef5',
        'font-family': 'JetBrains Mono, monospace',
        'font-size': 10,
        'text-valign': 'bottom',
        'text-margin-y': 7,
        'width': 'data(size)',
        'height': 'data(size)',
        'border-width': 2,
        'border-color': '#07090d',
        'text-outline-width': 2,
        'text-outline-color': '#07090d',
        'transition-property': 'width, height, border-width, opacity',
        'transition-duration': '0.25s'
      }
    },
    {
      selector: 'node[isCluster="true"]',
      style: {
        'shape': 'round-hexagon',
        'border-width': 3,
        'border-color': 'data(color)',
        'font-weight': 700,
        'font-size': 11,
        'background-opacity': 0.85
      }
    },
    {
      selector: 'node[isCluster="true"][expanded="true"]',
      style: { 'border-style': 'dashed', 'background-opacity': 0.55 }
    },
    {
      selector: 'node:selected',
      style: { 'border-color': '#ffffff', 'border-width': 3 }
    },
    { selector: 'node.dim', style: { 'opacity': 0.18 } },
    {
      selector: 'edge',
      style: {
        'curve-style': 'bezier',
        'width': 1.6,
        'line-color': '#2c3548',
        'target-arrow-color': '#2c3548',
        'target-arrow-shape': 'triangle',
        'arrow-scale': 0.8,
        'label': 'data(label)',
        'font-family': 'JetBrains Mono, monospace',
        'font-size': 8.5,
        'color': '#6b7891',
        'text-rotation': 'autorotate',
        'text-outline-width': 2,
        'text-outline-color': '#07090d',
        'opacity': 0.9
      }
    },
    { selector: 'edge[isMember="true"]', style: { 'line-style': 'dashed', 'opacity': 0.5 } },
    { selector: 'edge.dim', style: { 'opacity': 0.06 } },
    {
      selector: ".path-node",
      style: {
        "border-width": 5,
        "border-color": "#facc15",
        "background-color": "#f97316"
      }
    },
    {
      selector: ".path-edge",
      style: {
        "width": 6,
        "line-color": "#f97316",
        "target-arrow-color": "#f97316",
        "z-index": 999
      }
    }
  ],
  wheelSensitivity: 0.25
});

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => t.classList.remove('show'), 2200);
}

function colorFor(type) {
  const colors = {
    User: "#60a5fa", Host: "#f59e0b", IP: "#4ade80", Domain: "#a78bfa",
    FileHash: "#fb7185", URL: "#22d3ee", Process: "#e879f9", Email: "#facc15",
    CloudResource: "#34d399", CVE: "#f87171", Entity: "#94a3b8"
  };
  return colors[type] || "#94a3b8";
}

async function safeFetchJson(url, options = {}) {
  const token = sessionStorage.getItem("soc_token");
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
        window.location.href = "/login.html";
        return;
    }
  if (!res.ok) throw new Error('HTTP ' + res.status);
  
  const json = await res.json();
  return json.data !== undefined ? json.data : json;
}

function togglePathFinding() {
  pathFindingMode = !pathFindingMode;
  const panel = document.getElementById('pathPanel');
  const btn = document.getElementById('togglePathBtn');
  panel.hidden = !pathFindingMode;
  if (pathFindingMode) {
    if (!currentSelectedNode) {
      showToast("Hãy chọn một node trước.");
      pathFindingMode = false;
      panel.hidden = true;
      return;
    }
    pathSource = currentSelectedNode;
    pathTarget = null;
    document.getElementById("pathSource").textContent = `${pathSource.type}: ${pathSource.id}`;
    document.getElementById("pathTarget").textContent = "Chưa chọn";
    document.getElementById("findPathBtn").disabled = true;
    btn.innerHTML = "✕ Cancel Path";
  } else {
    pathSource = null;
    pathTarget = null;
    document.getElementById("pathSource").textContent = "Chưa chọn";
    document.getElementById("pathTarget").textContent = "Chưa chọn";
    document.getElementById("findPathBtn").disabled = true;
    btn.innerHTML = "⇄ Find Path";
    dehighlightPath();
  }
}

function runLayout(opts = {}) {
  cy.layout({ ...LAYOUTS[currentLayout], ...opts }).run();
  updateStats();
}

function debounce(func, timeout = 500) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => { func.apply(this, args); }, timeout);
  };
}

function normalizeNames(raw) {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw.map(x => (typeof x === 'string' ? x : (x.name || x.type || x.value))).filter(Boolean);
  return [];
}

function shorten(str, max) {
  str = String(str ?? '');
  return str.length > max ? str.slice(0, max - 1) + '…' : str;
}

function syncLayoutSwitch() {
  document.querySelectorAll('#layoutSwitch button').forEach(b =>
    b.classList.toggle('active', b.dataset.l === currentLayout)
  );
}

function updateStats() {
  document.getElementById('nodeCountLbl').textContent = cy.nodes(':visible').length;
  document.getElementById('edgeCountLbl').textContent = cy.edges(':visible').length;
  document.getElementById('canvasEmpty').style.display = cy.nodes(':visible').length === 0 ? 'flex' : 'none';
}

function showGraphPage() {
  showPage('graph');
  cy.resize();
  updateStats();
}

function showListPage() {
  showPage('list');
}

function setMode(next) {
  mode = next;
  const pill = document.getElementById('modePill');
  if (mode === 'OVERVIEW') {
    pill.className = 'pill overview dot';
    pill.textContent = 'Overview';
    document.getElementById('overviewControls').style.display = 'block';
    document.getElementById('investigationControls').style.display = 'none';
  } else {
    pill.className = 'pill investigation dot';
    pill.textContent = 'Investigation';
    document.getElementById('overviewControls').style.display = 'none';
    document.getElementById('investigationControls').style.display = 'block';
  }
}

async function loadOverviewClusterGraph() {
  setMode('OVERVIEW');
  expandedClusters.clear();
  investigationRoot = null;
  document.getElementById('canvasHint').textContent = "Chế độ tổng quan · Click vào một cụm để khám phá";
  document.getElementById('breadcrumbBox').textContent = '—';
  try {
    const data = await safeFetchJson(apiUrl('/graphs/clusters'));
    const nodes = data.nodes || data.clusters || [];
    const edges = data.edges || [];
    cy.elements().remove();
    const elements = [];
    nodes.forEach(c => {
      const type = c.entity_type || c.type;
      elements.push({
        group: 'nodes',
        data: {
          id: `Cluster:${type}`,
          fullLabel: `${type}`,
          label: `${type} (${c.count})`,
          color: colorFor(type),
          size: 58,
          isCluster: "true",
          expanded: "false",
          clusterType: type,
          count: c.count,
          properties: { "Loại": type, "Số lượng": c.count }
        }
      });
    });
    edges.forEach((e, idx) => {
      const srcId = e.source.startsWith('Cluster:') ? e.source : `Cluster:${e.source}`;
      const dstId = e.target.startsWith('Cluster:') ? e.target : `Cluster:${e.target}`;
      elements.push({
        group: 'edges',
        data: {
          id: `clusteredge_${idx}_${edgeSeq++}`,
          source: srcId,
          target: dstId,
          label: e.type ? `${e.type}${e.count ? ' (' + e.count + ')' : ''}` : 'RELATED'
        }
      });
    });
    cy.add(elements);
    runLayout();
    loadGlobalFilterOptions();
  } catch (err) {
    console.error(err);
    showToast('Không thể tải dữ liệu cluster: ' + err.message);
  }
}

async function toggleCluster(clusterId) {
  const clusterNode = cy.getElementById(clusterId);
  if (expandedClusters.has(clusterId)) {
    cy.remove(cy.nodes().filter(n => n.data('belongsTo') === clusterId));
    expandedClusters.delete(clusterId);
    clusterNode.data('expanded', 'false');
    clusterNode.data('size', 58);
    renderActionPanel(clusterNode);
    runLayout();
    return;
  }
  try {
    const type = clusterNode.data('clusterType');
    const entities = await safeFetchJson(apiUrl(`/graphs/clusters/types/${encodeURIComponent(type)}`));
    const list = Array.isArray(entities) ? entities : (entities.entities || []);
    const center = clusterNode.position();
    const total = list.length || 1;
    const radius = Math.min(260, 60 + total * 10);
    const elements = [];
    list.forEach((ent, i) => {
      const id = ent.id || `${type}:${ent.value}`;
      if (cy.getElementById(id).length) return;
      const angle = (i / total) * Math.PI * 2;
      const relCount = ent.relationship_count;
      elements.push({
        group: 'nodes',
        data: {
          id,
          label: type+":"+shorten(ent.id, 16) + (relCount ? ` (${relCount})` : ''),
          fullLabel: ent.value || ent.id,
          color: colorFor(type),
          size: 32,
          isCluster: "false",
          belongsTo: clusterId,
          type: type,
          isNewExpanded: false,
          properties: ent.properties || {}
        },
        position: { x: center.x + radius * Math.cos(angle), y: center.y + radius * Math.sin(angle) }
      });
      elements.push({
        group: 'edges',
        data: { id: `member_${clusterId}_${id}_${edgeSeq++}`, source: clusterId, target: id, label: 'MEMBER', isMember: "true" }
      });
    });
    cy.add(elements);
    clusterNode.data('expanded', 'true');
    clusterNode.data('size', 40);
    expandedClusters.add(clusterId);
    renderActionPanel(clusterNode);
    runLayout({ fit: false });
  } catch (err) {
    console.error(err);
    showToast('Không thể mở rộng cụm: ' + err.message);
  }
}

async function loadGlobalFilterOptions() {
  const typeSel = document.getElementById('globalTypeSelect');
  const relSel  = document.getElementById('globalRelSelect');
  try {
    const types = await safeFetchJson(apiUrl('/graphs/get-types'));
    const list = normalizeNames(types);
    typeSel.innerHTML = '<option value="">— Tất cả loại —</option>' + list.map(t => `<option value="${t}">${t}</option>`).join('');
  } catch { typeSel.innerHTML = '<option value="">— Tất cả loại —</option>'; }
  relSel.innerHTML = '<option value="">— Tất cả quan hệ —</option>';
  loadRelOptionsForType();
  typeSel.onchange = () => loadRelOptionsForType(typeSel.value);
}

async function loadRelOptionsForType(type) {
  const relSel = document.getElementById('globalRelSelect');
  try {
    if (!type) {
      relSel.innerHTML = '<option value="">— Tất cả quan hệ —</option>';
    }
    const typehtml= type? `?type=${encodeURIComponent(type)}` : ``;
    const rels = await safeFetchJson(apiUrl(`/graphs/filter-relationships${typehtml}`));
    const list = normalizeNames(rels);
    relSel.innerHTML = '<option value="">— Tất cả quan hệ —</option>' + list.map(r => `<option value="${r}">${r}</option>`).join('');
  } catch { }
}

async function runGlobalSearch() {
  const params = new URLSearchParams();
  const type = document.getElementById('globalTypeSelect').value;
  const rels = document.getElementById('globalRelSelect').value;
  const start = document.getElementById('globalStartTime').value;
  const end = document.getElementById('globalEndTime').value;
  const keyword = document.getElementById('globalSearchInput').value.trim().toLowerCase();
  const listEl = document.getElementById('entityChipList');
  listEl.innerHTML = '<div class="empty-note">Đang tìm kiếm...</div>';
  try {
    if (type) params.append('type', type);
    if (rels) params.append('relationship', rels);
    if (start) params.append('start', `${start}T00:00:00Z`);
    if (end) params.append('end', `${end}T23:59:59Z`);
    const path = `/entities/lists?${params.toString()}`;
    const data = await safeFetchJson(apiUrl(path));
    let list = Array.isArray(data) ? data : (data.entities || data.nodes || []);
    if (keyword) list = list.filter(e => String(e.value || e.id || '').toLowerCase().includes(keyword));
    document.getElementById('entityResultCount').textContent = list.length;
    renderEntityChips(list);
  } catch (err) {
    listEl.innerHTML = `<div class="empty-note">Lỗi truy vấn: ${err.message}</div>`;
  }
}

function renderEntityChips(list) {
  const listEl = document.getElementById('entityChipList');
  if (!list.length) {
    listEl.innerHTML = '<div class="empty-note">Không tìm thấy thực thể phù hợp.</div>';
    return;
  }
  listEl.innerHTML = list.slice(0, 200).map(e => {
    const type = e.type || document.getElementById('globalTypeSelect').value || 'Entity';
    const value = e.value || e.id;
    return `
      <div class="entity-row" data-type="${type}" data-value="${value}">
        <div class="entity-main">
          <span class="entity-type">${type}</span>
          <span class="entity-val">${value}</span>
        </div>
        <button class="entity-action" type="button" title="Double click để xem đồ thị">⤴</button>
      </div>`;
  }).join('');

  listEl.querySelectorAll('.entity-row').forEach((row, idx) => {
    const entity = list[idx];
    row.addEventListener('click', () => {
      document.querySelectorAll('.entity-row').forEach(r => r.classList.remove('selected'));
      row.classList.add('selected');
      showDetail(entity.id, entity.type, 'listDetailPanel');
    });
    row.addEventListener('dblclick', () => {
      const type = entity.type || document.getElementById('globalTypeSelect').value || 'Entity';
      const value = entity.fullLabel || entity.id;
      openEntityGraph(type, value);
    });
  });
}

async function openEntityGraph(type, value) {
  showGraphPage();
  await startInvestigation(type, value);
}

document.getElementById('globalSearchBtn').addEventListener('click', runGlobalSearch);
document.getElementById('globalSearchInput').addEventListener('keydown', e => { if (e.key === 'Enter') runGlobalSearch(); });

document.getElementById('layoutSelect').addEventListener('change', e => {
  currentLayout = e.target.value;
  syncLayoutSwitch();
  runLayout();
});

document.getElementById('layoutSwitch').addEventListener('click', e => {
  const btn = e.target.closest('button[data-l]');
  if (!btn) return;
  currentLayout = btn.dataset.l;
  document.getElementById('layoutSelect').value = currentLayout;
  syncLayoutSwitch();
  runLayout();
});

document.getElementById('tenantSelect').addEventListener('change', function () {
  currentTenant = this.value;
  loadOverviewClusterGraph();
  runGlobalSearch();
});

document.getElementById('globalResetBtn').addEventListener('click', function () {
  document.getElementById('globalTypeSelect').value = "";
  document.getElementById('globalRelSelect').value = "";
  loadGlobalFilterOptions();
});

cy.on('add remove', () => updateStats());
cy.on('dbltap', 'node[isCluster="true"]', (evt) => toggleCluster(evt.target.id()));
cy.on('dbltap', 'node[isCluster="false"]', (evt) => {
  let node = evt.target;
  const pill = document.getElementById('modePill');
  if (pill.textContent != 'Investigation')
    startInvestigation(node.data("type"), node.id());
  else hopExpand(node.data('type'), node.id(), 1);
});

cy.on("tap", "node", (e) => {
  const node = e.target;
  const pill = document.getElementById('modePill');
  const nodeData = node.data();
  cy.nodes().unselect();
  node.select();
  renderActionPanel(node);
  if (node.isCluster)
    return;
  showDetail(nodeData.id, nodeData.type, 'detailPanel');
  if (pill.textContent === 'Overview') {
    return;
  }
  currentSelectedNode = nodeData;
  if (pathFindingMode) {
    pathTarget = currentSelectedNode;
    document.getElementById("pathTarget").textContent = pathTarget.id;
    document.getElementById("findPathBtn").disabled = false;
  } else {
    pathSource = currentSelectedNode;
    document.getElementById("pathSource").textContent = pathSource.id;
    document.getElementById("togglePathBtn").disabled = false;
  }
});

cy.on('tap', (evt) => { if (evt.target === cy) cy.nodes().unselect(); });

async function initApp() {
  await loadTenants();
  await loadGlobalFilterOptions();
  await runGlobalSearch();
  await loadOverviewClusterGraph();
}

window.addEventListener('resize', () => cy.resize());

initApp();

const LAYOUTS = {
  cose:         { name: 'cose', animate: true, animationDuration: 450, nodeRepulsion: 52000, idealEdgeLength: 85, componentSpacing: 60, fit: true, padding: 60 },
  dagre:        { name: 'dagre', rankDir: 'TB', animate: true, animationDuration: 400, fit: true, padding: 60 },
  breadthfirst: { name: 'breadthfirst', animate: true, animationDuration: 400, fit: true, padding: 60, spacingFactor: 1.3 },
  concentric:   { name: 'concentric', animate: true, animationDuration: 400, fit: true, padding: 60, minNodeSpacing: 40 }
};

async function loadTenants() {
  const select = document.getElementById('tenantSelect');
  try {
    const tenants = await safeFetchJson('/api/tenants');
    const list = Array.isArray(tenants) ? tenants : [];
    select.innerHTML = list.map(t => `<option value="${t}">${t}</option>`).join('');
  } catch {
    select.innerHTML = '<option value="default">default</option>';
  }
  currentTenant = select.value;
}

async function startInvestigation(type, value) {
  snapshotGraph = cy.elements().clone();
  setMode('INVESTIGATION');
  investigationRoot = { type, value };
  baseElementIds = new Set();
  expandedPool = { nodes: new Map(), edges: new Map() };
  document.getElementById('canvasHint').textContent = `Đang điều tra: ${value}`;
  document.getElementById('breadcrumbBox').innerHTML = `Gốc điều tra: <b>${value}</b> <span style="color:var(--muted-2)">(${type})</span>`;
  try {
    const data = await safeFetchJson(apiUrl(`/graphs/entities/types/${encodeURIComponent(type)}/values/${encodeURIComponent(value)}?hop=1`));
    cy.elements().remove();
    const nodes = data.nodes || [];
    const edges = data.edges || [];
    nodes.forEach(n => {
      baseElementIds.add(n.id);
      const isRoot = (n.properties?.value === value) || n.id === `${type}:${value}`;
      cy.add({
        group: 'nodes',
        data: {
          id: n.id,
          label: n.type+":"+shorten(n.id, 16),
          fullLabel: n.id,
          color: colorFor(n.type),
          size: isRoot ? 46 : 34,
          isCluster: "false",
          type: n.type,
          isNewExpanded: false,
          properties: n.properties || {}
        },
        classes: isRoot ? 'root' : ''
      });
    });
    edges.forEach((e, idx) => {
      const id = `base_${idx}_${edgeSeq++}`;
      baseElementIds.add(id);
      cy.add({ group: 'edges', data: { id, source: e.source || e.start, target: e.target || e.end, label: e.type, isNewExpanded: false } });
    });
    runLayout();
    refreshHopNodeSelect();
    syncLayoutSwitch();
    renderInvestigationFilters();
    const rootNode = cy.nodes('.root').length ? cy.nodes('.root') : cy.nodes().first();
    if (rootNode.length) { rootNode.select(); showDetail(rootNode.data("id"), rootNode.data("type"), 'detailPanel'); renderActionPanel(rootNode); }
  } catch (err) {
    console.error(err);
    showToast('Không thể bắt đầu điều tra: ' + err.message);
  }
}

async function hopExpand(type, value, hop) {
  const targetNode = cy.getElementById(`${value}`).length
    ? cy.getElementById(`${value}`)
    : cy.nodes().filter(n => n.data('fullLabel') === value);
  const origin = targetNode.length ? targetNode.position() : { x: 0, y: 0 };
  try {
    const data = await safeFetchJson(apiUrl(`/graphs/entities/types/${encodeURIComponent(type)}/values/${encodeURIComponent(value)}?hop=${hop}`));
    const nodes = data.nodes || [];
    const edges = data.edges || [];
    cy.nodes().forEach(n => n.lock());
    let addedAny = false;
    nodes.forEach(n => {
      if (cy.getElementById(n.id).length) return;
      addedAny = true;
      expandedPool.nodes.set(n.id, n.type);
      cy.add({
        group: 'nodes',
        data: {
          id: n.id,
          label: n.type+":"+shorten(n.properties?.value || n.properties?.name || n.id, 16),
          fullLabel: n.properties?.value || n.id,
          color: colorFor(n.type),
          size: 30,
          isCluster: "false",
          type: n.type,
          isNewExpanded: true,
          properties: n.properties || {}
        },
        position: { x: origin.x + (Math.random() - 0.5) * 120, y: origin.y + (Math.random() - 0.5) * 120 }
      });
      cy.getElementById(n.id).unlock();
    });
    edges.forEach((e, idx) => {
      const src = e.source || e.start, dst = e.target || e.end, label = e.type;
      const exists = cy.edges().some(ex => ex.data('source') === src && ex.data('target') === dst && ex.data('label') === label);
      if (exists) return;
      const id = `hop_${Date.now()}_${idx}_${edgeSeq++}`;
      expandedPool.edges.set(id, label);
      cy.add({ group: 'edges', data: { id, source: src, target: dst, label, isNewExpanded: true } });
    });
    cy.layout({ name: 'cose', animate: true, animationDuration: 350, fit: false, nodeRepulsion: 28000, idealEdgeLength: 70 }).run();
    setTimeout(() => cy.nodes().unlock(), 400);
    refreshHopNodeSelect();
    renderInvestigationFilters();
    updateStats();
    showToast(addedAny ? 'Đã mở rộng thêm thực thể mới' : 'Không có thực thể mới ngoài graph hiện tại');
  } catch (err) {
    console.error(err);
    showToast('Lỗi mở rộng hop: ' + err.message);
    cy.nodes().unlock();
  }
}

function refreshHopNodeSelect() {
  const sel = document.getElementById('hopNodeSelect');
  const current = sel.value;
  const items = [];
  cy.nodes(':visible').forEach(n => {
    if (n.data('isCluster') === 'true') return;
    const label = n.data('fullLabel') || n.data('id');
    items.push({ type: n.data('type'), value: label });
  });
  sel.innerHTML = items.map(i => `<option value="${i.type}::${i.value}">${shorten(i.value, 26)} (${i.type})</option>`).join('');
  if ([...sel.options].some(o => o.value === current)) sel.value = current;
}

document.getElementById('hopExpandBtn').addEventListener('click', () => {
  const sel = document.getElementById('hopNodeSelect');
  if (!sel.value) { showToast('Chưa có node nào để mở rộng'); return; }
  const [type, value] = sel.value.split('::');
  const hop = parseInt(document.getElementById('hopDepthInput').value || '1', 10);
  hopExpand(type, value, hop);
});

function renderInvestigationFilters() {
  const nodeBox = document.getElementById('nodeFilterChecklist');
  const edgeBox = document.getElementById('edgeFilterChecklist');
  const types = [...new Set(expandedPool.nodes.values())];
  const rels  = [...new Set(expandedPool.edges.values())];
  nodeBox.innerHTML = types.length ? types.map(t => `
    <label class="check-item"><input type="checkbox" class="node-filter-chk" value="${t}" checked> ${t}</label>`).join('')
    : '<div class="empty-note">Chưa có node mở rộng.</div>';
  edgeBox.innerHTML = rels.length ? rels.map(r => `
    <label class="check-item"><input type="checkbox" class="edge-filter-chk" value="${r}" checked> ${r}</label>`).join('')
    : '<div class="empty-note">Chưa có quan hệ mới.</div>';
}

document.getElementById('applyInvFilterBtn').addEventListener('click', () => {
  const checkedTypes = [...document.querySelectorAll('.node-filter-chk:checked')].map(c => c.value);
  const checkedRels  = [...document.querySelectorAll('.edge-filter-chk:checked')].map(c => c.value);
  cy.batch(() => {
    cy.nodes().forEach(n => {
      if (!n.data('isNewExpanded')) return;
      n.style('display', checkedTypes.includes(n.data('type')) ? 'element' : 'none');
    });
    cy.edges().forEach(e => {
      if (!e.data('isNewExpanded')) return;
      const visible = checkedRels.includes(e.data('label')) && e.source().style('display') === 'element' && e.target().style('display') === 'element';
      e.style('display', visible ? 'element' : 'none');
    });
  });
  updateStats();
});

function exitInvestigation() {
  if (snapshotGraph) {
    cy.elements().remove();
    cy.add(snapshotGraph);
    snapshotGraph = null;
    setMode('OVERVIEW');
    document.getElementById('canvasHint').textContent = "Chế độ tổng quan · Click vào một cụm để khám phá";
    runLayout({ fit: false });
  } else {
    loadOverviewClusterGraph();
  }
  document.getElementById('actionPanel').innerHTML = '<div class="detail-empty">Chọn một cụm hoặc một thực thể trên đồ thị để bắt đầu.</div>';
  document.getElementById('detailPanel').innerHTML = '<div class="detail-empty">Chưa có đối tượng nào được chọn.</div>';
}

document.getElementById('exitInvestigationBtn').addEventListener('click', exitInvestigation);

function renderActionPanel(node) {
  const panel = document.getElementById('actionPanel');
  const data = node.data();
  currentSelectedNode = data;
  if (data.isCluster === "true") {
    const isExp = expandedClusters.has(data.id);
    panel.innerHTML = `
      <div style="font-weight:600; font-size:12.5px; color:var(--accent);">Cụm: ${data.clusterType}</div>
      <div style="font-size:11px; color:var(--muted);">${data.count} thực thể trong cụm này</div>
      <button id="clusterToggleBtn" class="${isExp ? 'danger' : ''}" style="margin-top:6px;">
        ${isExp ? '⊟ Thu gọn cụm' : '⊞ Mở rộng cụm'}
      </button>
    `;
    document.getElementById('clusterToggleBtn').addEventListener('click', () => { toggleCluster(data.id)});
    return;
  }
  if (mode === 'OVERVIEW') {
    panel.innerHTML = `
      <div class="investigate-cta">
        <p>Bắt đầu điều tra sâu thực thể
          <b style="color:var(--text)">${data.fullLabel || data.id}</b>
        </p>
        <button id="startInvBtn" class="block">
          ▶ Bắt đầu điều tra
        </button>
    `;
    document.getElementById('startInvBtn')
      .addEventListener('click', () => startInvestigation(data.type, data.fullLabel || data.id));

  } else {
    panel.innerHTML = `
      <div style="font-weight:600;font-size:12.5px;color:var(--amber);">
        ${data.fullLabel || data.id}
      </div>
      <div style="font-size:11px;color:var(--muted);margin-bottom:6px;">
        ${data.type}
      </div>
      <div class="row">
        <button id="quickHop1Btn" class="secondary sm">1-Hop</button>
        <button id="quickHop2Btn" class="secondary sm">2-Hop</button>
      </div>
    `;
    document.getElementById('quickHop1Btn').addEventListener('click', () => hopExpand(data.type, data.id, 1));
    document.getElementById('quickHop2Btn').addEventListener('click', () => hopExpand(data.type, data.id, 2));
    document.getElementById('togglePathBtn').addEventListener('click', togglePathFinding);
    document.getElementById('exportGraphBtn').addEventListener('click', exportGraphImage);
  }
}

function exportGraphImage() {
  const png = cy.png({ full: true, scale: 3, bg: "#0f172a" });
  const a = document.createElement("a");
  a.href = png;
  a.download = `graph-${new Date().toISOString().slice(0,19)}.png`;
  a.click();
  showToast("Đã xuất ảnh đồ thị.");
}

async function showDetail(data_id, data_type, panelId = 'detailPanel') {
  const area = document.getElementById(panelId);
  const data = !data_type
  ? cy.getElementById(data_id).data()
  : await safeFetchJson(apiUrl(`/entities/types/${encodeURIComponent(data_type)}/values/${encodeURIComponent(data_id)}`));
  const id = data.id || data["root"].id;
  const props = data.properties || data["root"].properties;
  const type = data.isCluster === "true" ? "CLUSTER" : data["root"].type;
  const baseIdentities = [
    "value", "username", "hostname", "name", "hash_value",
    "url", "process_name", "resource_id", "address", "cve_id"
  ];

  const metaKeys = new Set(["first_seen", "last_seen", "count"]);
  const identityKeys = new Set(baseIdentities);

  const identityProps = {};
  const metaProps = {};
  const enrichmentProps = {};

  Object.entries(props).forEach(([k, v]) => {
    if (identityKeys.has(k)) {
      identityProps[k] = v;
    } else if (metaKeys.has(k)) {
      metaProps[k] = v;
    } else {
      enrichmentProps[k] = v;
    }
  });

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = String(str ?? "");
    return div.innerHTML;
  }

  const renderPropsHtml = (propsObj, emptyMessage) => {
    const propsHtml = Object.entries(propsObj)
      .map(([k, v]) => `
        <div class="prop-row">
          <span class="k">${escapeHtml(k)}</span>
          <span class="v">${escapeHtml(v)}</span>
        </div>
      `).join('') || `<div class="empty-note">${emptyMessage}</div>`;
    return propsHtml;
  };
  const identityHtml = renderPropsHtml(identityProps, "Không có định danh.");
  const baseProfileHtml = renderPropsHtml(metaProps, "Không có thông tin cơ bản.");
  const enrichmentProfileHtml = renderPropsHtml(enrichmentProps, "Không có thông tin bổ sung.");
  let relationships = [];
  let relsHtml;
  if (data.isCluster !== "true") {
    try {
      const result = data
      relationships = result.edges || [];
    } catch (err) {
      console.error(err);
    }
    relsHtml = relationships.length
      ? relationships.map((rel, index) => {
          const isSource = rel.source === data.id;
          const otherNode = isSource ? rel.target : rel.source;
          const arrow = isSource ? "→" : "←";
          return `
              <div class="relationship">
                <div class="prop-row rel-header" data-index="${index}">
                  <span class="k">${rel.type}</span>
                  <span class="v">${arrow} ${otherNode}</span>
                  <button class="rel-toggle" type="button">▶</button>
                </div>
                <div class="rel-details" id="rel-${index}" hidden>
                  ${Object.entries(rel.rel_properties || {}).map(([k, v]) => {
                    // Xử lý riêng cho evidence: render button thay vì giá trị thô
                    if (k === "evidence" && v) {
                      return `
                        <div class="prop-row">
                          <span class="k">${k}</span>
                          <span class="v">
                            <button class="evidence-btn" data-event-id="${v}">🔗 Xem event gốc</button>
                          </span>
                        </div>
                      `;
                    }
                    // Các property khác giữ nguyên logic cũ
                    return `
                      <div class="prop-row">
                        <span class="k">${k}</span>
                        <span class="v">${Array.isArray(v) ? v.map(x => `<div>• ${x}</div>`).join("") : v}</span>
                      </div>
                    `;
                  }).join("")}
                </div>
                </div>
              </div>
            `;
        }).join("")
      : '<div class="empty-note">Không có mối quan hệ.</div>';
  } else {
  try {
      const result = await safeFetchJson(apiUrl(`/graphs/clusters/types/${encodeURIComponent(data.clusterType)}`));
      relationships = result || [];
    } catch (err) {
      console.error(err);
    }
    relsHtml = relationships.length
      ? relationships.map(rel => `
        <div class="prop-row">
          <span class="k">${shorten(rel.id, 16)}</span>
          <span class="v">(${rel.relationship_count}) relationships</span>
        </div>
      `).join("")
      : '<div class="empty-note">Cluster chưa được mở hoặc không có entity.</div>';
  }
  let enrichHtml = "";
  if (type === "IP" || type === "FileHash") {
    enrichHtml = `
      <div class="enrich-bar">
        <button id="enrichBtn" class="secondary sm">
          ⚡ Enrich ${type}
        </button>
      </div>
    `;
  }
  const relsTitle = data.isCluster !== "true"
    ? `<div class="eyebrow" style="margin-top:12px;">Relationships (${relationships.length})</div>`
    : `<div class="eyebrow" style="margin-top:12px;">Entities (${relationships.length})</div>`;
  area.innerHTML = `
    <span class="type-badge" style="border-color:${colorFor(type)}; color:${colorFor(type)};">
      ${type}
    </span>
    <div class="id-box">
      ${type}:${data.fullLabel || data.id || id}
    </div>
    ${enrichHtml}
    <div class="eyebrow" style="margin-top:12px;">Định danh (Identity)</div>
      ${identityHtml}
    <div class="eyebrow" style="margin-top:12px;">Thông tin cơ bản (Base Profile)</div>
      ${baseProfileHtml}
    <div class="eyebrow" style="margin-top:12px;">Thông tin làm giàu (Enrichment Profile)</div>
      ${enrichmentProfileHtml}
    ${relsTitle}
    <div>
    <div>
      ${relsHtml}
    </div>
  `;
  document.querySelectorAll(".rel-toggle").forEach(btn => {
    btn.onclick = () => {
      const details = btn.closest(".relationship").querySelector(".rel-details");
      details.hidden = !details.hidden;
      btn.textContent = details.hidden ? "▶" : "▼";
    };
  });
  area.querySelectorAll(".evidence-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation(); // tránh trigger click lan ra prop-row cha nếu có
        const eventId = btn.dataset.eventId;
        if (!eventId) return;
        await showEventPopup(eventId, btn);
      });
    });
  const enrichBtn = area.querySelector("#enrichBtn"); 

  if (enrichBtn) {
    enrichBtn.addEventListener("click", async () => {
      enrichBtn.disabled = true;
      enrichBtn.innerHTML = '<span class="spin"></span> Đang enrich...';
      try {
        const path = `/enrichments/types/${type}/values/${encodeURIComponent(id)}`;
        const result = await safeFetchJson(apiUrl(path), { method: "POST" });        
        
        // Truyền panelId vào để khi re-render nó vẫn vẽ đúng vào panel đó
        showDetail(id, type, panelId); 
      } catch (err) {
        showToast("Enrichment thất bại: " + err.message);
        enrichBtn.disabled = false;
        enrichBtn.innerHTML = "⚡ Thử lại";
      }
    });
  }
}
async function showEventPopup(eventId, triggerBtn) {
  // Đóng popup cũ nếu đang mở (tránh chồng nhiều popup)
  document.querySelectorAll(".event-popover").forEach(el => el.remove());

  const originalLabel = triggerBtn.innerHTML;
  triggerBtn.disabled = true;
  triggerBtn.innerHTML = '<span class="spin"></span>';

  // Tạo popover, định vị theo vị trí button
  const rect = triggerBtn.getBoundingClientRect();
  const popover = document.createElement("div");
  popover.className = "event-popover";
  popover.innerHTML = `
    <div class="event-popover-header">
      <span>Chi tiết Event</span>
      <button class="event-popover-close">✕</button>
    </div>
    <div class="event-popover-body">
      <div class="event-popover-loading"><span class="spin"></span> Đang tải...</div>
    </div>
  `;
  document.body.appendChild(popover);

  // Định vị: ưu tiên hiện bên dưới button, lệch trái nếu tràn màn hình
  positionPopover(popover, rect);

  const closePopover = () => popover.remove();
  popover.querySelector(".event-popover-close").addEventListener("click", closePopover);

  // Click ra ngoài để đóng
  const outsideClickHandler = (e) => {
    if (!popover.contains(e.target) && e.target !== triggerBtn) {
      closePopover();
      document.removeEventListener("click", outsideClickHandler);
    }
  };
  setTimeout(() => document.addEventListener("click", outsideClickHandler), 0);

  try {
    const result = await safeFetchJson(apiUrl(`/logs/events/${encodeURIComponent(eventId)}`));
    const raw = result;

    if (!raw) {
      popover.querySelector(".event-popover-body").innerHTML =
        '<div class="empty-note">Không tìm thấy dữ liệu event.</div>';
      return;
    }

    // Các field cố định hiển thị riêng, phần còn lại render động
    const fixedFields = ["event_id", "tenant", "source_type", "timestamp"];
    const restEntries = Object.entries(raw).filter(([k]) => !fixedFields.includes(k));

    popover.querySelector(".event-popover-body").innerHTML = `
      <div class="prop-row">
        <span class="k">Event ID</span>
        <span class="v">${raw.event_id ?? "-"}</span>
      </div>
      <div class="prop-row">
        <span class="k">Tenant</span>
        <span class="v">${raw.tenant ?? "-"}</span>
      </div>
      <div class="prop-row">
        <span class="k">Source Type</span>
        <span class="v">${raw.source_type ?? "-"}</span>
      </div>
      <div class="prop-row">
        <span class="k">Timestamp</span>
        <span class="v">${raw.timestamp ? new Date(raw.timestamp).toLocaleString() : "-"}</span>
      </div>
      ${restEntries.map(([k, v]) => `
        <div class="prop-row">
          <span class="k">${formatKey(k)}</span>
          <span class="v">${formatValue(v)}</span>
        </div>
      `).join("")}
    `;

    positionPopover(popover, rect);
  } catch (err) {
    popover.querySelector(".event-popover-body").innerHTML =
      `<div class="empty-note">Lỗi tải event: ${err.message}</div>`;
  } finally {
    triggerBtn.disabled = false;
    triggerBtn.innerHTML = originalLabel;
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function positionPopover(popover, rect) {
  const popW = popover.offsetWidth || 320;
  const popH = popover.offsetHeight || 200;
  const margin = 8;

  let top = rect.bottom + margin;
  let left = rect.left;

  // Nếu tràn phải màn hình, căn theo mép phải button
  if (left + popW > window.innerWidth - margin) {
    left = rect.right - popW;
  }
  // Nếu tràn dưới màn hình, hiện lên trên button thay vì dưới
  if (top + popH > window.innerHeight - margin) {
    top = rect.top - popH - margin;
  }

  popover.style.top = `${Math.max(margin, top)}px`;
  popover.style.left = `${Math.max(margin, left)}px`;
}

// Đổi snake_case -> Title Case cho đẹp: "destination_host" -> "Destination Host"
function formatKey(key) {
  return key
    .split("_")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

// Xử lý mọi kiểu giá trị: object, array, null, string dài...
function formatValue(v) {
  if (v === null || v === undefined) return "-";
  if (Array.isArray(v)) {
    return v.map(x => `<div>• ${escapeHtml(String(x))}</div>`).join("");
  }
  if (typeof v === "object") {
    // Nested object -> render dạng JSON thu gọn, tránh [object Object]
    return `<pre class="nested-json">${escapeHtml(JSON.stringify(v, null, 2))}</pre>`;
  }
  return escapeHtml(String(v));
}

function highlightPath(nodes, edges) {

    cy.elements().removeClass("path-node path-edge");

    nodes.forEach(n => {
        cy.$id(n.id).addClass("path-node");
    });

    edges.forEach(e => {

        cy.edges().forEach(edge => {

            if (
                edge.data("source") === e.source &&
                edge.data("target") === e.target &&
                edge.data("label") === e.type
            ) {
                edge.addClass("path-edge");
            }

        });

    });

    cy.fit(cy.$(".path-node"), 60);
}

function dehighlightPath() {
    cy.elements().removeClass("path-node path-edge");

    cy.fit(60); 
}


document.getElementById("findPathBtn").onclick = async () => {

    if (!pathSource || !pathTarget) return;
    const result = await safeFetchJson(
        apiUrl(
            `/graphs/path/types/${encodeURIComponent(pathSource.type)}` +
            `/values/${encodeURIComponent(pathSource.id)}` +
            `/dest-types/${encodeURIComponent(pathTarget.type)}` +
            `/dest-values/${encodeURIComponent(pathTarget.id)}`
        )
    );

    highlightPath(result.nodes, result.edges);
};
// ============================
// Ingest
// ============================

let ingestMode = "single";

// ============================
// Color
// ============================

const TYPE_COLORS = {
  User: "#60a5fa",
  Host: "#94a3b8",
  IP: "#4ade80",
  Domain: "#a78bfa",
  FileHash: "#fb7185",
  URL: "#22d3ee",
  Process: "#e879f9",
  Email: "#facc15",
  CloudResource: "#34d399",
  CVE: "#f87171"
};

function colorFor(type) {
  return TYPE_COLORS[type] || "#94a3b8";
}

// ============================
// Init
// ============================

document.addEventListener("DOMContentLoaded", async () => {
  await loadUser();
  setIngestMode("single");

  document
    .querySelectorAll("#ingestModeToggle .mode-btn")
    .forEach(btn => {
      btn.addEventListener("click", () => {
        setIngestMode(btn.dataset.mode);
      });
    });

  document
    .getElementById("ingestBtn")
    ?.addEventListener("click", runIngest);

  document
    .getElementById("loadSampleBtn")
    ?.addEventListener("click", loadSample);

  document
    .getElementById("clearIngestBtn")
    ?.addEventListener("click", clearIngest);

  document
    .getElementById("clearResultBtn")
    ?.addEventListener("click", clearResult);
});

// ============================
// Mode
// ============================

function setIngestMode(mode) {

  ingestMode = mode;

  document
    .querySelectorAll("#ingestModeToggle .mode-btn")
    .forEach(btn => {
      btn.classList.toggle("active", btn.dataset.mode === mode);
    });

  document.getElementById("ingestInput").placeholder =
    mode === "batch"
      ? `[
  {
    "event_id":"evt-001",
    "source_type":"siem"
  },
  {
    "event_id":"evt-002",
    "source_type":"edr"
  }
]`
      : `{
  "event_id":"evt-001",
  "source_type":"siem"
}`;
}

// ============================
// Input
// ============================

function clearIngest() {

  document.getElementById("ingestInput").value = "";

  const status = document.getElementById("ingestStatus");

  status.style.display = "none";
  status.className = "ingest-status";
}

function clearResult() {

  document.getElementById("ingestResultArea").innerHTML = `
    <div class="ingest-empty">
      <div style="font-size:28px;opacity:.3;margin-bottom:8px;">◈</div>
      <div>Kết quả bóc tách entity và relationship sẽ hiển thị ở đây.</div>
    </div>
  `;

  document.getElementById("ingestEventCount").style.display = "none";
  document.getElementById("clearResultBtn").style.display = "none";
}

function loadSample() {

  const single = {
    event_id: "evt-sample-001",
    source_type: "edr",
    timestamp: "2026-06-03T10:00:00Z",
    user: "john.doe",
    destination_host: "DESKTOP-001",
    destination_ip: "185.220.101.45",
    destination_domain: "malicious.ru",
    file_hash: "44d88612fea8a8f36de82e1278abb02f",
    process_name: "powershell.exe",
    parent_process: "explorer.exe"
  };

  const batch = [
    {
      event_id: "batch-001",
      source_type: "siem",
      timestamp: "2026-06-03T09:00:00Z",
      user: "alice",
      source_ip: "10.0.0.1",
      destination_host: "FILE-SERVER-01"
    },
    {
      event_id: "batch-002",
      source_type: "edr",
      timestamp: "2026-06-03T09:05:00Z",
      user: "bob",
      destination_host: "DESKTOP-002",
      destination_ip: "45.33.32.156",
      process_name: "cmd.exe",
      parent_process: "services.exe"
    }
  ];

  document.getElementById("ingestInput").value =
    JSON.stringify(
      ingestMode === "batch"
        ? batch
        : single,
      null,
      2
    );
}

// ============================
// Helpers
// ============================

function shorten(str, max) {

  str = String(str || "");

  return str.length > max
    ? str.slice(0, max - 1) + "…"
    : str;
}

function showStatus(type, msg) {

  const el = document.getElementById("ingestStatus");

  el.className = "ingest-status " + type;
  el.textContent = msg;
  el.style.display = "block";
}

// ============================
// Parse API
// ============================

function parseIngestData(dataArr) {

  const events = [];

  let current = null;

  for (const [key, value] of dataArr) {

    if (key === "nodes") {

      if (current)
        events.push(current);

      current = {
        nodes: value
      };

      continue;
    }

    if (!current)
      current = {};

    switch (key) {

      case "edges":
        current.edges = value;
        break;

      case "source_type":
        current.source_type = value;
        break;

      case "evidence":
        current.evidence = value;
        events.push(current);
        current = null;
        break;
    }
  }

  if (current)
    events.push(current);

  return events;
}

// ============================
// Render
// ============================

function renderEventCard(event, index) {

  const nodes = event.nodes || [];
  const edges = event.edges || [];

  const src = event.source_type || "—";
  const evidence = event.evidence || "—";

  const srcColors = {
    siem: "#5eead4",
    edr: "#fbbf24",
    cloud: "#818cf8",
    alert: "#fb7185"
  };

  const srcColor = srcColors[src] || "#94a3b8";

  const nodeHtml = nodes.map(node => {

    const c = colorFor(node.type);

    return `
      <span class="node-chip"
        style="color:${c};border-color:${c}33;background:${c}12;">
        <span class="chip-type">${node.type}</span>
        ${shorten(node.value,28)}
      </span>
    `;

  }).join("");

  const edgeHtml = edges.map(edge => {
    const sc = colorFor(edge.src.type);
    const tc = colorFor(edge.dest.type);

    const time = edge.time
      ? edge.time.replace("T"," ").substring(0,16)
      : "";

    return `
      <div class="edge-row">

        <span class="e-node"
          style="color:${sc};border-color:${sc}33;background:${sc}12;">
          ${shorten(edge.src.value,20)}
        </span>

        <span class="e-arrow">→</span>

        <span class="e-type">${edge.connect_type}</span>

        <span class="e-arrow">→</span>

        <span class="e-node"
          style="color:${tc};border-color:${tc}33;background:${tc}12;">
          ${shorten(edge.dest.value,20)}
        </span>

        ${
          time
            ? `<span class="e-time">${time}</span>`
            : ""
        }

      </div>
    `;

  }).join("");

  return `
    <div class="event-card">

      <div class="event-card-header">

        <span
          class="ev-badge"
          style="color:${srcColor};border-color:${srcColor}44;"
        >
          ${src.toUpperCase()}
        </span>

        <span class="ev-source">
          Event ${index + 1}
        </span>

        <span class="ev-evidence">
          ${evidence}
        </span>

      </div>

      <div class="event-card-body">

        ${
          nodes.length
            ? `
            <div>
              <div class="entity-group-label">
                Thực thể (${nodes.length})
              </div>

              <div class="node-chips">
                ${nodeHtml}
              </div>
            </div>
          `
            : ""
        }

        ${
          edges.length
            ? `
            <div>
              <div class="entity-group-label">
                Mối quan hệ (${edges.length})
              </div>

              <div class="edge-list">
                ${edgeHtml}
              </div>
            </div>
          `
            : ""
        }

      </div>

    </div>
  `;
}

function renderResults(events) {

  const area = document.getElementById("ingestResultArea");

  if (!events.length) {

    area.innerHTML =
      `<div class="ingest-empty">
        Không có entity nào được bóc tách.
      </div>`;

    return;
  }

  area.innerHTML =
    events.map(renderEventCard).join("");

  const badge =
    document.getElementById("ingestEventCount");

  badge.textContent =
    `${events.length} event${events.length > 1 ? "s" : ""}`;

  badge.style.display = "inline-flex";

  document.getElementById("clearResultBtn")
    .style.display = "inline-flex";
}

// ============================
// API
// ============================
async function runIngest() {
  const btn = document.getElementById("ingestBtn");
  const input = document.getElementById("ingestInput");
  const status = document.getElementById("ingestStatus");
  const autoEnrich = document.getElementById("autoEnrichCheckbox");

  const raw = input.value.trim();

  if (!raw) {
    showStatus("err", "Vui lòng nhập nội dung cần Ingest.");
    return;
  }

  // 1. Tự động xử lý Payload (Ưu tiên thử Parse JSON, nếu thất bại thì lấy làm String/Text thô)
  let payload;
  try {
    payload = JSON.parse(raw);
  } catch {
    // Nếu không phải JSON hợp lệ, coi như chuỗi văn bản thô
    payload = { text: raw }; 
  }

  const isBatch = typeof ingestMode !== "undefined" && ingestMode === "batch";

  // 2. Kiểm tra điều kiện chế độ Batch/Single
  if (isBatch) {
    // Nếu ở chế độ Batch mà payload không phải Array, chuyển nó thành Array 1 phần tử
    if (!Array.isArray(payload)) {
      payload = [payload];
    }
  } else {
    // Nếu ở chế độ Single mà người dùng lỡ dán một JSON Array
    if (Array.isArray(payload)) {
      showStatus("err", "Chế độ Single chỉ nhận dữ liệu đơn (Text hoặc JSON Object).");
      return;
    }
  }

  const tenant = document.getElementById("tenantSelect")?.value || "default";
  console.log(autoEnrich.checked)
  const enrich = autoEnrich.checked ? `?auto_ingest=${true}`: ``;
  const url = isBatch
    ? `/api/tenants/${tenant}/graphs/ingest/batch${enrich}`
    : `/api/tenants/${tenant}/graphs/ingest${enrich}`;

  btn.disabled = true;
  btn.innerHTML = '<span class="spin"></span> Đang xử lý...';
  status.style.display = "none";

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + sessionStorage.getItem("soc_token")
      },
      body: JSON.stringify(payload)
    });

    const json = await response.json();

    if (!response.ok) {
      showStatus(
        "err",
        json.detail || json.message || "Ingest thất bại."
      );
      return;
    }

    showStatus("ok", json.message || "Ingest thành công.");

    if (Array.isArray(json.data)) {
      renderResults(parseIngestData(json.data));
    }

  } catch (err) {
    showStatus(
      "err",
      "Không thể kết nối máy chủ: " + err.message
    );
  } finally {
    btn.disabled = false;
    btn.innerHTML = "⊕ Ingest";
  }
  runGlobalSearch();
}

document.getElementById("loadFileBtn").addEventListener("click", () => {
  document.getElementById("ingestFileInput").click();
});

document.getElementById("ingestFileInput").addEventListener("change", async (e) => {
  const files = Array.from(e.target.files || []);
  if (files.length === 0) return;

  const status = document.getElementById("ingestStatus");
  const input = document.getElementById("ingestInput");
  const isBatch = typeof ingestMode !== "undefined" && ingestMode === "batch";

  try {
    const contents = await Promise.all(files.map(readFileAsText));

    if (files.length === 1) {
      // 1 file: đổ nguyên nội dung vào textarea, để runIngest tự parse JSON/text
      input.value = contents[0];
    } else {
      // Nhiều file: chỉ hợp lệ khi ở chế độ Batch
      if (!isBatch) {
        showStatus("err", "Chọn nhiều file chỉ dùng được ở chế độ Batch. Hãy chuyển mode hoặc chọn 1 file.");
        e.target.value = "";
        return;
      }

      // Mỗi file parse JSON riêng (nếu là JSON), nếu không parse được thì coi là text thô
      const items = contents.map((raw) => {
        const trimmed = raw.trim();
        try {
          return JSON.parse(trimmed);
        } catch {
          return { text: trimmed };
        }
      });

      // Nếu 1 file nào đó tự nó đã là array, "trải phẳng" ra để đúng format batch
      const flattened = items.flatMap((item) => (Array.isArray(item) ? item : [item]));

      input.value = JSON.stringify(flattened, null, 2);
    }

    showStatus("ok", `Đã tải ${files.length} file (${files.map(f => f.name).join(", ")}).`);
  } catch (err) {
    showStatus("err", "Không đọc được file: " + err.message);
  } finally {
    e.target.value = ""; // reset để chọn lại cùng file vẫn trigger change
  }
});

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error(`Không đọc được file "${file.name}"`));
    reader.readAsText(file);
  });
}