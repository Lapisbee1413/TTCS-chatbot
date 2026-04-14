"""Quick test for document_validator"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from document_validator import validate_legal_document, format_validation_report

# Test 1: Vietnamese legal doc (Nghi Dinh)
vn_text = """
NGHỊ ĐỊNH SỐ 45/2024/NĐ-CP
Căn cứ Luật Tổ chức Chính phủ ngày 19 tháng 6 năm 2015;
Theo đề nghị của Bộ trưởng Bộ Tài chính;
Chính phủ ban hành Nghị định quy định chi tiết:

Chương I. QUY ĐỊNH CHUNG
Điều 1. Phạm vi điều chỉnh
Nghị định này quy định chi tiết một số điều của Luật.
Điều 2. Đối tượng áp dụng
1. Cơ quan nhà nước
2. Tổ chức, cá nhân

Chương II. QUY ĐỊNH CỤ THỂ
Điều 3. Nguyên tắc chung
Khoản 1. Đảm bảo công bằng
Khoản 2. Minh bạch
Điều 4. Trách nhiệm thi hành
Điều 5. Hiệu lực thi hành
Nơi nhận:
"""
r = validate_legal_document(vn_text)
print(format_validation_report(r))
print(f"=> Score={r['score']} Quality={r['quality']} Lang={r['language']} Type={r['document_type']['label']}")

# Test 2: English legal doc
en_text = """
AGREEMENT NO. 2024/AB-001
This Agreement is entered into between Party A and Party B.

Chapter I. GENERAL PROVISIONS
Article 1. Scope of Application
This agreement governs the terms and conditions of the contract.
Article 2. Definitions
Article 3. Obligations
Clause 1. Party A shall provide services.
Clause 2. Party B shall make payment.
Article 4. Termination
Article 5. Dispute Resolution
Article 6. Governing Law
Article 7. Force Majeure
Article 8. Final Provisions
This agreement shall enter into force on the date of signing.
"""
r = validate_legal_document(en_text)
print(format_validation_report(r))
print(f"=> Score={r['score']} Quality={r['quality']} Lang={r['language']} Type={r['document_type']['label']}")

# Test 3: Garbage
garbage = """
hello world this is just some random text
lorem ipsum dolor sit amet consectetur
foo bar baz qux nothing legal here
1234567890 abcdefg hijklmnop
"""
r = validate_legal_document(garbage)
print(format_validation_report(r))
print(f"=> Score={r['score']} Quality={r['quality']} Lang={r['language']}")

# Test 4: Chi thi (non-standard)
chi_thi = """
CHỈ THỊ SỐ 05/CT-TTg
Căn cứ Luật Tổ chức Chính phủ;
Theo đề nghị của Bộ Công an;
Thủ tướng Chính phủ chỉ thị:

Một là, tăng cường trách nhiệm của các cơ quan;
Hai là, đẩy mạnh công tác tuyên truyền pháp luật;
Ba là, xử lý nghiêm các hành vi vi phạm;
Bốn là, tổ chức thực hiện nghiêm túc.

1. Bộ Công an chịu trách nhiệm thi hành
2. Các bộ, ngành phối hợp thực hiện
3. Ủy ban nhân dân các tỉnh tổ chức triển khai

Nơi nhận:
"""
r = validate_legal_document(chi_thi)
print(format_validation_report(r))
print(f"=> Score={r['score']} Quality={r['quality']} Lang={r['language']} Type={r['document_type']['label']}")
