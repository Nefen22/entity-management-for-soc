# ADR-004: Config-driven JSON Parser thay thế các Parser riêng biệt

## Context

Hệ thống cần hỗ trợ ingest log từ nhiều nguồn khác nhau (FR-11):

* SIEM events
* EDR events
* Cloud Audit logs
* Custom log sources trong tương lai

### Thiết kế ban đầu

Mỗi nguồn log có một parser riêng:

* `SIEMParser`
* `EDRParser`
* `CloudParser`

Mỗi parser kế thừa `BaseParser` và cài đặt logic extract entity riêng.

Ví dụ:

```text
SIEMParser
EDRParser
CloudParser
    ↓
BaseParser
```

Các parser này có logic gần giống nhau:

* đọc field từ event
* tạo entity
* tạo relationship

---

## Vấn đề

### 1. Code trùng lặp

Các parser khác nhau chủ yếu chỉ khác tên field:

```python
source_ip
destination_ip
user
hostname
```

Nhưng phần lớn logic xử lý giống nhau.

---

### 2. Khó mở rộng

Thêm nguồn log mới yêu cầu:

* tạo parser mới
* kế thừa BaseParser
* viết lại logic mapping

Điều này làm tăng số lượng class dù phần lớn code giống nhau.

---

### 3. Logic quan hệ phân tán

Relationship được suy ra bên trong từng parser.

Việc thay đổi hoặc bổ sung quan hệ yêu cầu sửa nhiều nơi.

---

## Decision

Thay thế các parser riêng biệt bằng một `BaseParser` duy nhất.

Mỗi loại log chỉ cung cấp một cấu hình gồm:

* node mapping
* edge mapping

Ví dụ:

```python
SIEM_INCLUDE = {
    "nodes": {
        "users": ["user"],
        "hosts": ["destination_host"],
        "ips": ["source_ip"]
    },
    "edges": [
        ("user", "destination_host"),
        ("destination_host", "source_ip")
    ]
}
```

---

### Node Extraction

`split_nodes_edges()` đọc cấu hình:

```python
parser_nodes = include["nodes"]
```

và chuyển field thành entity:

```python
Vertex(
    type=MAPPING_ENTITIES_TYPE[k],
    value=event.get(v)
)
```

Ví dụ:

```text
source_ip
    ↓
IP

destination_host
    ↓
Host
```

---

### Relationship Extraction

Quan hệ được khai báo tường minh:

```python
"edges": [
    ("user", "destination_host"),
    ("destination_host", "source_ip")
]
```

Parser chỉ tạo edge nếu cả hai field tồn tại trong event.

Relationship type được lấy từ:

```python
MAPPING_RELATIONSHIPS[
    (source_type, target_type)
]
```

Ví dụ:

```python
("User", "Host") -> LOGGED_IN
("Host", "IP") -> CONNECTED_TO
```

---

## Reason

* Loại bỏ code trùng lặp giữa parser.
* Giảm số lượng class parser.
* Tập trung toàn bộ logic vào `BaseParser`.
* Quan hệ được khai báo rõ ràng.
* Thêm nguồn log mới chỉ cần thêm cấu hình.

---

## Trade-offs

### Ưu điểm

* Một parser duy nhất cho mọi nguồn log.
* Dễ mở rộng.
* Dễ test.
* Relationship được khai báo rõ ràng.
* Không cần sửa code parser khi thêm log source mới.

### Nhược điểm

* Mỗi nguồn log phải định nghĩa đầy đủ:

  * nodes
  * edges
* Nếu cấu hình sai thì parser sẽ tạo graph sai.
* Log có cấu trúc nested sâu cần pre-processing trước khi parse.

---

## Consequences

Kiến trúc mới:

```text
Event
    ↓
Parser Config
    ↓
BaseParser
    ↓
Vertex / Edge
    ↓
Service Layer
    ↓
Neo4j
```

Thêm nguồn log mới:

```python
CUSTOM_INCLUDE = {
    "nodes": {...},
    "edges": [...]
}

json_format["custom"] = CUSTOM_INCLUDE
```

Không cần:

* tạo parser mới
* kế thừa BaseParser
* sửa logic xử lý

---

## Architecture

```text
Security Event
        ↓
   Parser Config
        ↓
    BaseParser
        ↓
   Nodes / Edges
        ↓
   Service Layer
        ↓
    Repository
        ↓
      Neo4j
        ↓
  Visualization
```

---

Phần "cartesian product bug" và "source_/destination_ direction" trong ADR cũ nên bỏ hoàn toàn vì implementation hiện tại của bạn không còn hoạt động theo cơ chế đó nữa. Quan hệ bây giờ được xác định tường minh bằng:

```python
"edges": [
    ("user", "destination_host")
]
```

nên ADR nên phản ánh đúng thiết kế hiện tại thay vì lịch sử của một implementation cũ.
