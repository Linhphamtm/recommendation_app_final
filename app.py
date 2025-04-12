# Final App - Product & User Recommendation System
# Người thực hiện: Phạm Thị Mai Linh
# Ngày báo cáo: 13/04/2025

import streamlit as st
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ================================
# Cấu hình App
# ================================
st.set_page_config(page_title='Hệ thống gợi ý sản phẩm', layout='wide', initial_sidebar_state='expanded')

# ================================
# Sidebar - Navigation và Thông tin
# ================================
st.sidebar.title('📂 Điều hướng')
page = st.sidebar.radio("Chọn mục", ['Insight', 'App'])

st.sidebar.markdown("""
### 🧑‍💻 Người thực hiện
**Phạm Thị Mai Linh**

### 📅 Ngày báo cáo
**13/04/2025**
""")

# ================================
# Load model và dữ liệu đồng bộ
# ================================
with open('product_cosine.pkl', 'rb') as f:
    product_model = pickle.load(f)

vectorizer = product_model['vectorizer']
tfidf_matrix = product_model['tfidf_matrix']
df_product = product_model['dataframe']

with open('surprise_model.pkl', 'rb') as f:
    user_model = pickle.load(f)

algo = user_model['model']
df_user = user_model['df_sample']

# Chỉ lấy user_id có product_id trùng với df_product
valid_user_ids = df_user[df_user['product_id'].isin(df_product['product_id'])]['user_id'].unique().tolist()

# ================================
# Trang Insight
# ================================
if page == 'Insight':
    st.title('📊 Project Insight')

    # --- Mục tiêu Project ---
    st.header('🎯 Mục tiêu project')
    st.markdown("""
    Xây dựng hệ thống gợi ý sản phẩm thời trang nam trên Shopee, nhằm hỗ trợ người tiêu dùng dễ dàng tìm kiếm sản phẩm phù hợp dựa trên:

    - **Gợi ý theo nội dung sản phẩm:** Dựa trên mô tả chi tiết của sản phẩm.
    - **Gợi ý theo người dùng:** Dựa trên lịch sử đánh giá và tương tác của người dùng.
    """)

    # --- EDA ---
    st.header('📊 Khám phá dữ liệu (EDA)')

    # Wordcloud mô tả sản phẩm
    st.subheader('Wordcloud mô tả sản phẩm')
    text = ' '.join(df_product['final_cleaned_tokens'].apply(lambda x: ' '.join(x)))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

    # Phân phối rating sản phẩm
    st.subheader('Phân phối rating sản phẩm')
    st.bar_chart(df_product['rating'].value_counts().sort_index())

    # Phân phối rating user-based
    st.subheader('Phân phối rating từ người dùng')
    st.bar_chart(df_user['rating'].value_counts().sort_index())

    # --- Các bước làm sạch dữ liệu ---
    st.header('🧹 Các bước làm sạch dữ liệu')
    st.markdown("""
    **Bước 1:** Chuẩn hóa văn bản mô tả sản phẩm.
    - Xử lý encoding, chuẩn hóa Unicode, loại bỏ ký tự không cần thiết.

    **Bước 2:** Loại bỏ nhiễu và pattern không mong muốn.
    - Xóa các mẫu spam, từ ngữ quảng cáo trùng lặp.

    **Bước 3:** Tách từ (Tokenization) và loại bỏ stopword.
    - Tách các từ trong câu và loại bỏ từ dừng không cần thiết.

    **Bước 4:** Kết quả cuối cùng.
    - Văn bản sạch và được xử lý trong cột `final_cleaned_tokens` sẵn sàng cho vector hóa.
    """)

    # --- Thuật toán sử dụng ---
    st.header('🧩 Thuật toán sử dụng')
    st.markdown("""
    - **Cosine Similarity:** Đo lường mức độ tương đồng giữa các sản phẩm dựa trên mô tả.
    - **Surprise SVD:** Phân rã ma trận để dự đoán sản phẩm phù hợp với từng người dùng.
    """)

    # --- Đánh giá thuật toán ---
    st.header('📈 Đánh giá thuật toán sử dụng')
    st.markdown("""
    **Cosine Similarity:**
    - Ưu điểm: Dễ triển khai, trực quan, hoạt động tốt khi dữ liệu mô tả sản phẩm được làm sạch tốt.
    - Hạn chế: Không cá nhân hóa theo người dùng.

    **Surprise SVD:**
    - Ưu điểm: Cá nhân hóa gợi ý theo lịch sử người dùng.
    - Hạn chế: Cần đủ dữ liệu người dùng để huấn luyện chính xác.
    """)

# ================================
# Trang App (Recommendation)
# ================================
elif page == 'App':
    st.title('🤖 Recommendation App')

    tab1, tab2 = st.tabs(["🛍️ Gợi ý theo sản phẩm", "👥 Gợi ý theo người dùng"])

    # --- Tab 1: Product-based ---
    with tab1:
        st.header('Gợi ý theo sản phẩm (Content-based)')
        user_input = st.text_input('Nhập mô tả sản phẩm bạn muốn tìm gợi ý:')
        top_k = st.slider('Số lượng sản phẩm gợi ý:', min_value=1, max_value=20, value=5)

        if st.button('📊 Hiển thị gợi ý sản phẩm'):
            if not user_input.strip():
                st.warning("⚠️ Vui lòng nhập mô tả sản phẩm để nhận gợi ý.")
            else:
                user_input_vector = vectorizer.transform([user_input])
                sim_scores = list(enumerate(cosine_similarity(user_input_vector, tfidf_matrix)[0]))
                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[:top_k]

                recommendations = []
                for idx, score in sim_scores:
                    row = df_product.iloc[idx]
                    recommendations.append({
                        'Ảnh': row['image'] if pd.notna(row['image']) else '',
                        'Tên sản phẩm': row['product_name'],
                        'Giá': f"{row['price']:.0f} VND" if pd.notna(row['price']) else 'N/A',
                        'Điểm tương đồng': f"{score:.2f}",
                        'Link': f"[Xem sản phẩm]({row['link']})" if pd.notna(row['link']) else "N/A"
                    })

                st.markdown("### 🎯 Kết quả gợi ý:")

                for rec in recommendations:
                    cols = st.columns([1, 3])
                    if rec['Ảnh']:
                        cols[0].image(rec['Ảnh'], width=120)
                    else:
                        cols[0].empty()

                    cols[1].markdown(f"**{rec['Tên sản phẩm']}**")
                    cols[1].markdown(f"💰 {rec['Giá']} | ⭐️ Điểm tương đồng: {rec['Điểm tương đồng']}")
                    cols[1].markdown(f"🔗 {rec['Link']}")
                    cols[1].markdown("---")

                results_df = pd.DataFrame(recommendations)
                csv = results_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Tải kết quả về CSV", data=csv, file_name='recommendations_product.csv', mime='text/csv')

    # --- Tab 2: User-based ---
    with tab2:
        st.header('Gợi ý theo người dùng (Collaborative filtering)')

        selected_user = st.selectbox('Chọn User bạn muốn tìm gợi ý:', valid_user_ids)
        top_k_user = st.slider('Số lượng sản phẩm gợi ý:', min_value=1, max_value=20, value=5, key='user_slider')

        if st.button('📊 Hiển thị gợi ý người dùng'):
            user_ratings = df_user[df_user['user_id'] == selected_user]
            if user_ratings.empty:
                st.warning("⚠️ Người dùng này không có đánh giá trong dữ liệu!")
            else:
                all_product_ids = df_product['product_id'].unique()
                predictions = [(product_id, algo.predict(selected_user, product_id).est) for product_id in all_product_ids]
                predictions = sorted(predictions, key=lambda x: x[1], reverse=True)[:top_k_user]

                recommendations = []
                for pid, est in predictions:
                    row = df_product[df_product['product_id'] == pid].iloc[0]
                    recommendations.append({
                        'Ảnh': row['image'] if pd.notna(row['image']) else '',
                        'Tên sản phẩm': row['product_name'],
                        'Giá': f"{row['price']:.0f} VND" if pd.notna(row['price']) else 'N/A',
                        'Rating dự đoán': f"{est:.2f}",
                        'Link': f"[Xem sản phẩm]({row['link']})" if pd.notna(row['link']) else "N/A"
                    })

                st.markdown("### 🎯 Kết quả gợi ý:")

                for rec in recommendations:
                    cols = st.columns([1, 3])
                    if rec['Ảnh']:
                        cols[0].image(rec['Ảnh'], width=120)
                    else:
                        cols[0].empty()

                    cols[1].markdown(f"**{rec['Tên sản phẩm']}**")
                    cols[1].markdown(f"💰 {rec['Giá']} | ⭐️ Rating dự đoán: {rec['Rating dự đoán']}")
                    cols[1].markdown(f"🔗 {rec['Link']}")
                    cols[1].markdown("---")

                results_df_user = pd.DataFrame(recommendations)
                csv = results_df_user.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Tải kết quả về CSV", data=csv, file_name='recommendations_user.csv', mime='text/csv')
