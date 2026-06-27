# ADR-003: Chọn Cytoscape.js cho Graph Visualization

## Context

Hệ thống Entity Management for SOC cần:
- Hiển thị graph quan hệ giữa các entity (User, Host, IP, Domain, FileHash...)
- Hỗ trợ nhiều layout (force-directed, hierarchical, tree...)
- Cho phép người dùng tương tác: click node xem chi tiết, filter theo loại entity/quan hệ
- Tích hợp vào frontend đơn giản (HTML + JavaScript, không dùng framework)

Đề bài liệt kê 3 lựa chọn: `cytoscape.js`, `vis.js`, `d3.js`

## Decision

Sử dụng **Cytoscape.js**

## So sánh các lựa chọn

### Cytoscape.js

Ưu điểm:
- Thiết kế chuyên biệt cho graph/network visualization
- Hỗ trợ sẵn nhiều layout: force-directed (cose), breadth-first, dagre (hierarchical), concentric — không cần cài thêm thư viện
- API thao tác graph trực quan: filter node/edge, highlight, expand subgraph dễ dàng
- Hỗ trợ event handler (click, hover, select) tốt cho investigation workflow
- Tích hợp đơn giản qua CDN, không cần build step
- Tài liệu đầy đủ, cộng đồng lớn

Nhược điểm:
- Hiệu năng giảm khi graph có hàng chục nghìn node (nhưng vượt quá nhu cầu hiện tại)

Đánh giá: **Phù hợp nhất** với yêu cầu graph investigation của SOC platform

---

### vis.js

Ưu điểm:
- Dễ dùng, ít config
- Visualization đẹp theo mặc định

Nhược điểm:
- Layout ít tùy chỉnh hơn Cytoscape.js
- Khả năng filter/manipulation graph phức tạp hạn chế hơn
- Phát triển chậm lại trong những năm gần đây

Đánh giá: Phù hợp cho use case đơn giản, không đủ linh hoạt cho investigation workflow

---

### d3.js

Ưu điểm:
- Cực kỳ linh hoạt, có thể tùy chỉnh mọi thứ
- Hiệu năng cao
- Hệ sinh thái rộng

Nhược điểm:
- Low-level — không có built-in graph layout, phải tự implement force simulation
- Learning curve cao, tốn nhiều thời gian để ra được kết quả graph cơ bản
- Không phù hợp với timeline ngắn của dự án

Đánh giá: Mạnh nhưng quá low-level cho bài toán graph investigation, không phù hợp với thời gian triển khai ngắn

---

## Reason

Cytoscape.js được chọn vì:
- Là thư viện graph chuyên biệt, không phải thư viện visualization tổng quát như d3
- Built-in layout đa dạng (cose, breadth-first, dagre, concentric) đáp ứng trực tiếp yêu cầu FR-16
- API manipulation graph (filter, expand, highlight) phù hợp với investigation workflow của SOC analyst
- Tích hợp dễ dàng vào single HTML file không cần build step, phù hợp với kiến trúc frontend hiện tại

## Consequences

### Ưu:
- Triển khai nhanh, có graph cơ bản chạy được trong thời gian ngắn
- Hỗ trợ nhiều layout giúp analyst lựa chọn view phù hợp với từng loại điều tra
- Dễ mở rộng thêm tính năng: expand-on-click, path highlighting, time-based filtering

### Nhược:
- Hiệu năng có thể giảm nếu graph vượt quá vài nghìn node trong cùng 1 view (cần phân trang hoặc giới hạn hop)
- Không có built-in export PNG/JSON (cần xử lý thêm nếu muốn implement FR-19)