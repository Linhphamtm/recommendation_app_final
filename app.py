# FINAL APP - CLEAN & STABLE VERSION
# Người thực hiện: Phạm Thị Mai Linh
# Ngày báo cáo: 13/04/2025

import streamlit as st
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# =============================
# CONFIG APP
# =============================
st.set_page_config(page_title='Hệ thống gợi ý sản phẩm', layout='wide', initial_sidebar_state='expanded')

# =============================
# SIDEBAR
# =============================
st.sidebar.title('📂 Điều hướng')
page = st.sidebar.radio('Chọn mục', ['Insight', 'App'])

st.sidebar.markdown("""
### 🧑‍💻 Người thực hiện
**Phạm Thị Mai Linh**

### 📅 Ngày báo cáo
**13/04/2025**
""")

# =============================
# LOAD MODELS & DATA
# =============================
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

# =============================
# INSIGHT PAGE
# =============================
if page == 'Insight':
    st.title('📊 Project Insight')

    st.header('🎯 Mục tiêu project')
    st.markdown("""
    Xây dựng hệ thống gợi ý sản phẩm thời trang nam trên Shopee, nhằm hỗ trợ người tiêu dùng dễ dàng tìm kiếm sản phẩm phù hợp dựa trên:

    - **Gợi ý theo nội dung sản phẩm:** Dựa trên mô tả chi tiết của sản phẩm.
    - **Gợi ý theo người dùng:** Dựa trên lịch sử đánh giá và tương tác của người dùng.
    """)

    st.header('📊 Khám phá dữ liệu (EDA)')
    st.subheader('Wordcloud mô tả sản phẩm')
    text = ' '.join(df_product['final_cleaned_tokens'].apply(lambda x: ' '.join(x)))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

    st.subheader('Phân phối rating sản phẩm')
    st.bar_chart(df_product['rating'].value_counts().sort_index())

    st.subheader('Phân phối rating từ người dùng')
    st.bar_chart(df_user['rating'].value_counts().sort_index())

    st.header('🧹 Các bước làm sạch dữ liệu')
    st.markdown("""
    **Bước 1:** Chuẩn hóa văn bản mô tả sản phẩm.

    **Bước 2:** Loại bỏ nhiễu và pattern không mong muốn.

    **Bước 3:** Tokenization và loại bỏ stopword.

    **Bước 4:** Kết quả: Văn bản sạch trong `final_cleaned_tokens`.
    """)

    st.header('🧩 Thuật toán sử dụng')
    st.markdown("""
    - **Cosine Similarity:** Đo mức độ tương đồng giữa các sản phẩm.
    - **Surprise SVD:** Dự đoán sản phẩm phù hợp với từng người dùng.
    """)

    st.header('📈 Đánh giá thuật toán')
    st.markdown("""
    **Cosine Similarity:**
    - Ưu điểm: Dễ triển khai, trực quan.
    - Hạn chế: Không cá nhân hóa.

    **Surprise SVD:**
    - Ưu điểm: Cá nhân hóa theo lịch sử người dùng.
    - Hạn chế: Cần đủ dữ liệu người dùng để huấn luyện.
    """)

# =============================
# APP PAGE (RECOMMENDATION)
# =============================
elif page == 'App':
    st.title('🤖 Recommendation App')

    tab1, tab2 = st.tabs(['🛍️ Gợi ý theo sản phẩm', '👥 Gợi ý theo người dùng'])

    # Product-based tab
    with tab1:
        st.header('Gợi ý theo sản phẩm (Content-based)')
        user_input = st.text_input('Nhập mô tả sản phẩm bạn muốn tìm gợi ý:')
        top_k = st.slider('Số lượng sản phẩm gợi ý:', 1, 20, 5)

        if st.button('📊 Hiển thị gợi ý sản phẩm'):
            if not user_input.strip():
                st.warning('⚠️ Vui lòng nhập mô tả sản phẩm.')
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

                st.markdown('### 🎯 Kết quả gợi ý:')
                for rec in recommendations:
                    cols = st.columns([1, 3])
                    if rec['Ảnh']:
                        cols[0].image(rec['Ảnh'], width=120)
                    cols[1].markdown(f"**{rec['Tên sản phẩm']}**")
                    cols[1].markdown(f"💰 {rec['Giá']} | ⭐️ Điểm tương đồng: {rec['Điểm tương đồng']}")
                    cols[1].markdown(f"🔗 {rec['Link']}")
                    cols[1].markdown('---')

                results_df = pd.DataFrame(recommendations)
                csv = results_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button('📥 Tải kết quả về CSV', data=csv, file_name='recommendations_product.csv', mime='text/csv')

    # User-based tab
    with tab2:
        st.header('Gợi ý theo người dùng (Collaborative filtering)')
        selected_user = st.selectbox('Chọn User bạn muốn tìm gợi ý:', valid_user_ids)
        top_k_user = st.slider('Số lượng sản phẩm gợi ý:', 1, 20, 5, key='user_slider')

        if st.button('📊 Hiển thị gợi ý người dùng'):
            user_ratings = df_user[df_user['user_id'] == selected_user]
            if user_ratings.empty:
                st.warning('⚠️ Người dùng này không có đánh giá trong dữ liệu!')
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

                st.markdown('### 🎯 Kết quả gợi ý:')
                for rec in recommendations:
                    cols = st.columns([1, 3])
                    if rec['Ảnh']:
                        cols[0].image(rec['Ảnh'], width=120)
                    cols[1].markdown(f"**{rec['Tên sản phẩm']}**")
                    cols[1].markdown(f"💰 {rec['Giá']} | ⭐️ Rating dự đoán: {rec['Rating dự đoán']}")
                    cols[1].markdown(f"🔗 {rec['Link']}")
                    cols[1].markdown('---')

                results_df_user = pd.DataFrame(recommendations)
                csv = results_df_user.to_csv(index=False).encode('utf-8-sig')
                st.download_button('📥 Tải kết quả về CSV', data=csv, file_name='recommendations_user.csv', mime='text/csv')
