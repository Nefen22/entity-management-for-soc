let logCurrentPage = 1;
const logPageSize = 15;

// Đồng bộ bảng màu mã Hex chính xác từ hàm colorFor của index.html
const entityColors = {
  User: "#60a5fa", Host: "#f59e0b", IP: "#4ade80", Domain: "#a78bfa",
  FileHash: "#fb7185", URL: "#22d3ee", Process: "#e879f9", Email: "#facc15",
  CloudResource: "#34d399", CVE: "#f87171", Entity: "#94a3b8"
};

async function fetchLogs(page) {
  try {
    logCurrentPage = page;
    const searchKeyword = document.getElementById('searchId').value.trim();
    const typeKeyword = document.getElementById('filterType').value;
    let url = `/api/logs?page=${page}&limit=${logPageSize}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error("Mất kết nối hệ thống log API");
    const res = await response.json();
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
      const before = typeof log.change.before === "string"
        ? (log.change.before ? JSON.parse(log.change.before) : {})
        : (log.change.before || {});
      const after = typeof log.change.after === "string"
        ? (log.change.after ? JSON.parse(log.change.after) : {})
        : (log.change.after || {});
      const beforeProps = before.properties || before.entity || before;
      const afterProps = after.properties || after.entity || after;
      if (log.action === "CREATE") {
        propertiesString = `
          <div class="space-y-1">
            ${Object.entries(afterProps).map(([k,v]) => `
              <div>
                <span class="text-slate-500">${k}</span>
                :
                <span class="text-emerald-400">${JSON.stringify(v)}</span>
              </div>
            `).join("")}
          </div>
        `;
      } else {
        const keys = [...new Set([ ...Object.keys(beforeProps), ...Object.keys(afterProps) ])];
        propertiesString = `
          <div class="space-y-1">
            ${keys.map(k => `
              <div>
                <span class="text-slate-500">${k}</span>
                <span class="text-red-400 line-through">${JSON.stringify(beforeProps[k])}</span>
                <span class="text-slate-500 mx-1">→</span>
                <span class="text-emerald-400">${JSON.stringify(afterProps[k])}</span>
              </div>
            `).join("")}
          </div>
        `;
      }
    } catch (e) {
      propertiesString = `
        <pre class="text-xs text-slate-400 whitespace-pre-wrap">
${JSON.stringify(log.change, null, 2)}
        </pre>
      `;
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

document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const searchIdFromUrl = urlParams.get('searchId');
  const entityTypeFromUrl = urlParams.get('entityType');
  if (searchIdFromUrl) {
    document.getElementById('searchId').value = searchIdFromUrl;
  }
  if (entityTypeFromUrl && entityColors[entityTypeFromUrl]) {
    document.getElementById('filterType').value = entityTypeFromUrl;
  }
  fetchLogs(1);
});
