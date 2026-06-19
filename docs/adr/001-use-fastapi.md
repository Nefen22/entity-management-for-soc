#ADR-001: Chọn FastAPI thay vì Node.js

#Context

Hệ thông Entity Management for SOC cần:
    -REST API cho ingestion, enrichment và graph query.
    -Kết nối Neo4j.
    -Xử lí enrichment bất đồng bộ.
    -Có khả năng mở rộng, tích hợp AI/LLM trong tương lai.
    -Thời gian triển khai ngắn.
Các lựa chọn cân nhắc:
    -FastAPI (Python)
    -Express/NestJS (Node.js)

#Decision

Sử dụng FastAPI 

#Reason

##Hệ sinh thái về an toàn thông tin mạnh
Nhiều thư viện enrichment có sẵn:
    -geoip2
    -ipaddress
    -whois 
    -requests
    -virustotal-python

##Thuận lợi khi tích hợp AI/LLM
Trong tương lai có thể dùng AI để hỗ trợ Entity extraction bằng free-text alert.
Các nhiều framework AI chủ yếu hỗ trợ Python.

##Hỗ trợ async tốt
Phù hợp các tác vụ I/O như:
    -Neo4j
    -Virustotal

#Trade-offs

##Hiệu năng thấp hơn Node.js
FastAPI thường chậm hơn Node.js khi I/O với thông lượng lớn

#Consequences

##Ưu:
    -MVP hoàn thành nhanh.
    -Dễ tích hợp enrichment.
    -Dễ tích hợp AI/LLM.
    -Code gọn.

##Nhược:
    -Throughput thấp hơn Node.js ở quy mô rất lớn.