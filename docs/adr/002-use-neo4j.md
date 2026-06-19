### Quyết định công nghệ: Neo4j

#### Quyết định

Hệ thống sử dụng **Neo4j** làm cơ sở dữ liệu chính để lưu trữ và quản lý các entity cùng mối quan hệ giữa chúng.

#### Lý do lựa chọn

Bài toán của hệ thống tập trung vào việc quản lý và truy vấn mối quan hệ giữa các thực thể an ninh mạng như User, Host, IP, Domain, File Hash và các thực thể mở rộng khác. Các tác vụ điều tra thường yêu cầu truy vết qua nhiều bước liên kết (multi-hop traversal), ví dụ:

```text
User → Host → IP → Domain
```

hoặc

```text
User → Host → File Hash → CVE
```

Neo4j được lựa chọn vì:

* Là cơ sở dữ liệu đồ thị (Graph Database) được thiết kế tối ưu cho dữ liệu có nhiều quan hệ.
* Hỗ tr nhiều phépợ truy vấn multi-hop hiệu quả mà không cần thực hiện JOIN phức tạp như cơ sở dữ liệu quan hệ.
* Cung cấp sẵn các khả năng tìm đường đi (Path Finding) giữa các entity.
* Hỗ trợ câu lệnh `MERGE` giúp tự động nhận diện và gộp các entity trùng lặp trong quá trình ingest dữ liệu.
* Mô hình dữ liệu linh hoạt, dễ dàng mở rộng thêm các loại entity mới như URL, Process, Email, CVE hoặc Cloud Resource.
* Sử dụng ngôn ngữ truy vấn Cypher trực quan và phù hợp với bài toán điều tra trên đồ thị.

#### Ví dụ sử dụng

Truy vấn đường đi giữa User và Domain:

```text
john.doe
    ↓
LOGGED_IN
    ↓
DESKTOP-001
    ↓
CONNECTED_TO
    ↓
192.168.1.100
    ↓
RESOLVES
    ↓
malicious.ru
```

Truy vấn như trên có thể được thực hiện dễ dàng bằng cơ chế graph traversal của Neo4j.

### So sánh Neo4j với các Graph Database khác

#### Neo4j

Ưu điểm:

* Graph database phổ biến nhất hiện nay.
* Tài liệu phong phú, cộng đồng lớn.
* Ngôn ngữ truy vấn Cypher trực quan và dễ học.
* Hỗ trợ tốt các bài toán path-finding, graph traversal.
* Có Neo4j Browser hỗ trợ trực quan hóa đồ thị.
* Hỗ trợ MERGE giúp chống trùng lặp entity.
* Triển khai đơn giản bằng Docker.

Nhược điểm:

* Một số tính năng nâng cao thuộc phiên bản Enterprise.
* Hiệu năng ghi dữ liệu cực lớn có thể không bằng một số graph database phân tán.

Đánh giá:

Phù hợp nhất với quy mô và mục tiêu của dự án.

---

#### JanusGraph

Ưu điểm:

* Thiết kế cho hệ thống phân tán.
* Có thể scale ngang rất lớn.
* Hỗ trợ backend như Cassandra, HBase.

Nhược điểm:

* Triển khai phức tạp.
* Cần thêm nhiều thành phần hạ tầng.
* Khó sử dụng cho dự án nhỏ hoặc MVP.

Đánh giá:

Phù hợp với hệ thống production quy mô rất lớn (hàng trăm triệu hoặc hàng tỷ node), vượt quá nhu cầu của dự án.

---

#### TigerGraph

Ưu điểm:

* Hiệu năng rất cao.
* Tối ưu cho graph analytics.
* Hỗ trợ xử lý dữ liệu quy mô lớn.

Nhược điểm:

* Hệ sinh thái nhỏ hơn Neo4j.
* Tài liệu và cộng đồng hạn chế hơn.
* Một số tính năng yêu cầu bản thương mại.

Đánh giá:

Mạnh về hiệu năng nhưng quá mức cần thiết cho bài toán hiện tại.

---

#### Amazon Neptune

Ưu điểm:

* Dịch vụ managed của AWS.
* Không cần tự vận hành database.
* Hỗ trợ Gremlin và SPARQL.

Nhược điểm:

* Khóa chặt vào hệ sinh thái AWS.
* Chi phí cao hơn.
* Khó triển khai môi trường local để demo.

Đánh giá:

Phù hợp với hệ thống cloud-native nhưng không phù hợp cho đồ án hoặc dự án học tập.

---

#### ArangoDB

Ưu điểm:

* Multi-model database.
* Hỗ trợ Document + Graph.
* Linh hoạt trong lưu trữ dữ liệu.

Nhược điểm:

* Khả năng graph không mạnh bằng Neo4j.
* Cộng đồng nhỏ hơn.

Đánh giá:

Lựa chọn tốt nếu cần kết hợp document database và graph database trong cùng hệ thống.

---

#### Dgraph

Ưu điểm:

* Thiết kế hiện đại.
* Hiệu năng cao.
* Hỗ trợ GraphQL.

Nhược điểm:

* Hệ sinh thái nhỏ.
* Ít tài liệu hơn Neo4j.

Đánh giá:

Tiềm năng nhưng chưa phổ biến bằng Neo4j.

---

### Kết luận

Dự án yêu cầu:

* Lưu trữ entity và relationship.
* Truy vấn multi-hop.
* Path finding.
* Entity deduplication.
* Visualization.
* Triển khai nhanh trong thời gian ngắn.

Trong các lựa chọn đã khảo sát, Neo4j cung cấp đầy đủ các tính năng trên với độ phức tạp triển khai thấp nhất, tài liệu tốt nhất và cộng đồng lớn nhất. Vì vậy Neo4j được lựa chọn làm graph database cho hệ thống.
