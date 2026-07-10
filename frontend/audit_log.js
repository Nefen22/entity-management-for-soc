let logCurrentPage = 1;
const logPageSize = 15;
const urlParams = new URLSearchParams(window.location.search);
const receivedData = urlParams.get('data');

if (receivedData) {
  sessionStorage.setItem('soc_token', receivedData);
}

const entityColors = {
  User: "#60a5fa", Host: "#f59e0b", IP: "#3d413e", Domain: "#a78bfa",
  FileHash: "#fb7185", URL: "#22d3ee", Process: "#e879f9", Email: "#facc15",
  CloudResource: "#34d399", CVE: "#f87171", Entity: "#94a3b8"
};

// --- BỎ gọi loadTenants() trực tiếp ở đây để đưa vào luồng khởi tạo chuẩn ---

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

async function loadTenants() {
  const select = document.getElementById('tenantSelect');
  try {
    const tenants = await safeFetchJson('/api/tenants');
    const list = Array.isArray(tenants) ? tenants : [];
    select.innerHTML = list.map(t => `<option value="${t}">${t}</option>`).join('');
  } catch {
    select.innerHTML = '<option value="default">default</option>';
  }
  // Gán giá trị tenant đầu tiên tìm được
  currentTenant = select.value;
}

document.getElementById('tenantSelect').addEventListener('change', function () {
  console.log(this.value)
  currentTenant = this.value;
  fetchLogs(1);
});


async function fetchLogs(page) {
  try {
    logCurrentPage = page;
    const searchKeyword = document.getElementById('searchId').value.trim();
    const typeKeyword = document.getElementById('filterType').value;
    const actionKeyword = document.getElementById('filterAction').value;
    const startTimeVal = document.getElementById('startTime').value;
    const endTimeVal = document.getElementById('endTime').value;
    
    // Đảm bảo lấy giá trị mới nhất từ thuộc tính hoặc biến toàn cục
    const tenant = currentTenant || document.getElementById('tenantSelect').value;
    if (!tenant) return; // Phòng trường hợp danh sách tenant trống

    const params = new URLSearchParams();
    params.set('page', page);
    params.set('limit', logPageSize);
    if (searchKeyword) params.set('entity_id', searchKeyword);
    if (typeKeyword && typeKeyword !== 'ALL') params.set('entity_type', typeKeyword);
    if (actionKeyword && actionKeyword !== 'ALL') params.set('action', actionKeyword);
    if (startTimeVal) params.set('start_time', new Date(startTimeVal).toISOString());
    if (endTimeVal) params.set('end_time', new Date(endTimeVal).toISOString());
    
    const url = `/api/tenants/${encodeURIComponent(tenant)}/logs/audit-logs?${params.toString()}`;
    const res = await safeFetchJson(url);
    document.getElementById('logCount').innerText = res.metadata.total_records;
    document.getElementById('pageInfo').innerText = `Trang ${res.metadata.current_page} / ${res.metadata.total_pages}`;
    document.getElementById('btnPrevPage').disabled = !res.metadata.has_previous;
    document.getElementById('btnNextPage').disabled = !res.metadata.has_next;
    renderLogTable(res.data, searchKeyword, typeKeyword);
  } catch (err) {
    console.error("Lỗi fetch logs:", err);
    document.getElementById('logTableBody').innerHTML = `
      <tr>
        <td colspan="4" class="p-6 text-center text-rose-400 font-mono">[!] Không thể kết nối tới tệp tin logs hoặc lỗi API 500.</td>
      </tr>
    `;
  }
}

// ... Các hàm navigatePage, executeFilter, renderLogTable giữ nguyên cấu trúc cũ của bạn ...

function navigatePage(step) {
  fetchLogs(logCurrentPage + step);
}

function executeFilter() {
  fetchLogs(1);
}

function renderLogTable(logs, filterId = "", filterType = "ALL") {
  const tbody = document.getElementById('logTableBody');
  tbody.innerHTML = '';
  const filteredLogs = logs.filter(log => {
    if (filterType !== "ALL" && log.entity_type !== filterType) return false;
    if (filterId && !log.entity_id.toLowerCase().includes(filterId.toLowerCase())) return false;
    return true;
  });
  if (filteredLogs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="p-8 text-center text-slate-600 italic">Không tìm thấy bản ghi log nào phù hợp với bộ lọc hiện tại.</td></tr>`;
    return;
  }
  filteredLogs.forEach(log => {
    const actionBadge = log.action === 'CREATE'
      ? `<span class="bg-emerald-950/60 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[10px] font-bold">CREATE</span>`
      : `<span class="bg-blue-950/60 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded text-[10px] font-bold">UPDATE</span>`;
    const color = entityColors[log.entity_type] || "#94a3b8";
    let propertiesString = "";
    try {
      const IGNORE_FIELDS = new Set(["first_seen", "last_seen", "count"]);

      const before = typeof log.change.before === "string"
        ? (log.change.before ? JSON.parse(log.change.before) : {})
        : (log.change.before || {});

      const after = typeof log.change.after === "string"
        ? (log.change.after ? JSON.parse(log.change.after) : {})
        : (log.change.after || {});

      const beforeProps = before.properties || before.entity || before;
      const afterProps = after.properties || after.entity || after;

      for (const k of IGNORE_FIELDS) {
        delete beforeProps[k];
        delete afterProps[k];
      }
      if (log.action === "CREATE") {
        propertiesString = `
          <div class="space-y-1">
            ${Object.entries(afterProps)
              .filter(([k]) => !IGNORE_FIELDS.has(k))
              .map(([k,v]) => `
                <div>
                  <span class="text-slate-500">${k}</span>
                  :
                  <span class="text-emerald-400">${JSON.stringify(v)}</span>
                </div>
              `).join("")}
          </div>
        `;
      } else {
        const keys = [...new Set([...Object.keys(beforeProps), ...Object.keys(afterProps)])];
        const changedKeys = keys.filter(k => JSON.stringify(beforeProps[k]) !== JSON.stringify(afterProps[k]));

        propertiesString = `
          <div class="space-y-1">
            ${changedKeys.map(k => `
              <div>
                <span class="text-slate-500">${k}</span>
                <span class="text-red-400 line-through">${beforeProps[k] !== undefined ? JSON.stringify(beforeProps[k]) : "null"}</span>
                <span class="text-slate-500 mx-1">→</span>
                <span class="text-emerald-400">${afterProps[k] !== undefined ? JSON.stringify(afterProps[k]) : "null"}</span>
              </div>
            `).join("")}
          </div>
        `;
      }
    } catch (e) {
      propertiesString = `<pre class="text-xs text-slate-400 whitespace-pre-wrap">${JSON.stringify(log.change, null, 2)}</pre>`;
    }
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-[#121824]/60 transition border-b border-slate-900/60';
    tr.innerHTML = `
      <td class="p-3 text-slate-500 font-mono text-[11px]">${log.timestamp || 'N/A'}</td>
      <td class="p-3">${actionBadge}</td>
      <td class="p-3">
        <span style="color: ${color}; border-color: ${color}40; background-color: ${color}10" class="border px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider mr-2">
          ${log.entity_type}
        </span>
        <span class="text-slate-200 font-bold">${log.entity_id}</span>
      </td>
      <td class="p-3 text-slate-400 align-top" title='${JSON.stringify(log.change)}'>${propertiesString}</td>
    `;
    tbody.appendChild(tr);
  });
}

// --- KHU VỰC THAY ĐỔI CHÍNH Ở ĐÂY ---
document.addEventListener("DOMContentLoaded", async () => {
  // 1. Chờ load xong danh sách tenant và khởi tạo currentTenant trước
  await loadTenants();

  // 2. Điền dữ liệu bộ lọc từ URL params (giữ nguyên logic của bạn)
  const urlParams = new URLSearchParams(window.location.search);
  const searchIdFromUrl = urlParams.get('searchId');
  const entityTypeFromUrl = urlParams.get('entityType');
  const actionFromUrl = urlParams.get('action');
  const startTimeFromUrl = urlParams.get('start_time');
  const endTimeFromUrl = urlParams.get('end_time');

  if (searchIdFromUrl) document.getElementById('searchId').value = searchIdFromUrl;
  if (entityTypeFromUrl && entityColors[entityTypeFromUrl]) document.getElementById('filterType').value = entityTypeFromUrl;
  if (actionFromUrl && ['CREATE', 'UPDATE'].includes(actionFromUrl)) document.getElementById('filterAction').value = actionFromUrl;
  if (startTimeFromUrl) document.getElementById('startTime').value = startTimeFromUrl;
  if (endTimeFromUrl) document.getElementById('endTime').value = endTimeFromUrl;

  // 3. Sau khi đã có tenant mặc định và các bộ lọc, tiến hành fetch dữ liệu log lần đầu tiên
  fetchLogs(1);
});