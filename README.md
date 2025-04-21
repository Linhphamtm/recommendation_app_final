# 🚀 Hệ thống Gợi ý Sản phẩm Shopee

**Người thực hiện:** Phạm Thị Mai Linh & Tô Nguyễn Phương Anh  
**Ngày báo cáo:** 13/04/2025

---

## 📌 Giới thiệu

Dự án xây dựng hệ thống gợi ý sản phẩm thời trang nam trên Shopee, sử dụng mô hình đã huấn luyện sẵn để đảm bảo tốc độ khởi chạy nhanh và ổn định:

- **Gợi ý theo nội dung sản phẩm (Product-based):**
  - Sử dụng mô hình **Cosine Similarity**.
  - Mô hình đã được huấn luyện và lưu dưới dạng: `product_cosine.pkl`.
  - Người dùng nhập mô tả sản phẩm để tìm sản phẩm tương tự.

- **Gợi ý theo người dùng (User-based):**
  - Sử dụng thuật toán **Surprise SVD**.
  - Mô hình đã được huấn luyện và lưu dưới dạng: `surprise_model.pkl`.
  - Hệ thống gợi ý dựa trên lịch sử đánh giá của người dùng.

📌 Ứng dụng phù hợp để demo báo cáo, hoặc mở rộng thành sản phẩm thực tế.

---

## 📂 Cấu trúc Project

```text
├── app.py               # Ứng dụng chính Streamlit
├── product_cosine.pkl   # Mô hình Cosine Similarity đã huấn luyện
├── surprise_model.pkl   # Mô hình Surprise SVD đã huấn luyện
├── requirements.txt     # Danh sách thư viện cần thiết
└── README.md            # Hướng dẫn sử dụng
```

---

## ⚙️ Hướng dẫn Cài đặt (Local)

### 1. Clone dự án

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng

```bash
streamlit run app.py
```

---

