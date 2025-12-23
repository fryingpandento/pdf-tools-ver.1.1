import streamlit as st
from pypdf import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
from PIL import Image
import io
import zipfile

try:
    from streamlit_pdf_viewer import pdf_viewer
except ImportError:
    st.error("新しいライブラリが必要です。ターミナルで `pip install streamlit-pdf-viewer` を実行してください。")
    st.stop()

st.set_page_config(
    page_title="PDF Tools",
    # layout="wide", # Remove force wide to allow better mobile centering
    initial_sidebar_state="expanded"
)

# Custom CSS for Mobile Optimization
st.markdown("""
<style>
    /* Reduce top padding for mobile */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
    }
    /* Better heading sizes */
    h1 {
        font-size: 1.8rem !important;
    }
    h2 {
        font-size: 1.5rem !important;
    }
    h3 {
        font-size: 1.2rem !important;
        margin-bottom: 0.5rem;
        color: #444;
    }
    /* Button full width on mobile */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
    }
    /* Hide some heavy elements if needed via media query (optional) */
</style>
""", unsafe_allow_html=True)

st.title("PDF Tools")
st.caption("データはローカルメモリ上で安全に処理されます。")

st.sidebar.header("機能メニュー")
menu = [
    "PDF分割 (Split)", 
    "PDF結合 (Merge)", 
    "ページ並び替え (Reorder)", 
    "PDF → 画像変換", 
    "画像 → PDF変換", 
    "PDF圧縮 (Compress)", 
    "パスワード保護"
]
choice = st.sidebar.radio("機能を選択:", menu)
st.sidebar.divider()

if choice == "PDF分割 (Split)":
    st.header("PDFの分割・抽出")
    
    uploaded_file = st.file_uploader("編集するPDFをアップロードしてください", type="pdf")
    
    if uploaded_file:
        # On mobile, stack these instead of side-by-side
        # Streamlit columns collapse on mobile automatically, but we can verify order
        # Put controls first for better UX? No, preview is usually good but large.
        
        # Let's keep columns but maybe adjust ratio or let them flow
        st.subheader("設定・操作")
        with st.container(border=True):
             reader = PdfReader(uploaded_file)
             total_pages = len(reader.pages)
             st.info(f"**総ページ数:** {total_pages} ページ")

             split_mode = st.radio(
                 "分割モードを選択", 
                 ("全ページをバラバラにする (ZIP)", "範囲を指定して抽出 (Custom)")
             )

             st.divider()

             if "全ページ" in split_mode:
                 st.write("全てのページを1枚ずつのPDFファイルに分割し、ZIPでまとめます。")
                 if st.button("全ページ分割を実行", type="primary", use_container_width=True):
                     zip_buffer = io.BytesIO()
                     with zipfile.ZipFile(zip_buffer, "w") as zf:
                         for i, page in enumerate(reader.pages):
                             writer = PdfWriter()
                             writer.add_page(page)
                             pdf_bytes = io.BytesIO()
                             writer.write(pdf_bytes)
                             zf.writestr(f"page_{i+1}.pdf", pdf_bytes.getvalue())
                     
                     st.success("完了しました！")
                     st.download_button("ZIPをダウンロード", zip_buffer.getvalue(), "split_all.zip", "application/zip", use_container_width=True)

             else:
                 st.write("**抽出したい範囲を指定 (コンマ区切り)**")
                 st.caption("例: `1-3, 5` → 1〜3ページと5ページを抽出")
                 
                 range_input = st.text_input("ページ範囲", placeholder="例: 1-3, 5, 8-10")
                 
                 if st.button("指定範囲で分割を実行", type="primary", use_container_width=True):
                     if not range_input:
                         st.error("範囲を入力してください。")
                     else:
                         try:
                             parts = [p.strip() for p in range_input.split(',')]
                             output_zip_buffer = io.BytesIO()
                             files_created = 0

                             with zipfile.ZipFile(output_zip_buffer, "w") as zf:
                                 for part in parts:
                                     writer = PdfWriter()
                                     filename = ""
                                     if '-' in part:
                                         start, end = map(int, part.split('-'))
                                         start, end = max(1, start), min(total_pages, end)
                                         for i in range(start - 1, end):
                                             writer.add_page(reader.pages[i])
                                         filename = f"pages_{start}-{end}.pdf"
                                     else:
                                         p_num = int(part)
                                         if 1 <= p_num <= total_pages:
                                             writer.add_page(reader.pages[p_num - 1])
                                             filename = f"page_{p_num}.pdf"
                                     
                                     if len(writer.pages) > 0:
                                         pdf_bytes = io.BytesIO()
                                         writer.write(pdf_bytes)
                                         zf.writestr(filename, pdf_bytes.getvalue())
                                         files_created += 1

                             if files_created > 0:
                                 st.success(f"{files_created}ファイルを作成しました！")
                                 st.download_button("ダウンロード (ZIP)", output_zip_buffer.getvalue(), "split_custom.zip", "application/zip", use_container_width=True)
                             else:
                                 st.error("ページが見つかりませんでした。")
                         except ValueError:
                             st.error("入力形式を確認してください。")

        st.subheader("プレビュー")
        pdf_viewer(uploaded_file.getvalue(), height=600 if st.session_state.get('is_mobile') else 800, width=None)

elif choice == "PDF結合 (Merge)":
    st.header("複数のPDFを結合")
    uploaded_files = st.file_uploader("結合するPDFを選択 (複数可)", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        # Stacked layout: Controls top, Preview bottom
        st.subheader("結合設定")
        with st.container(border=True):
            st.write(f"**選択ファイル数:** {len(uploaded_files)}")
            st.caption("アップロードした順序で結合されます。")
            
            st.markdown("---")
            for f in uploaded_files:
                try:
                    reader = PdfReader(f)
                    num_pages = len(reader.pages)
                    st.text(f"📄 {f.name} ({num_pages} pages)")
                    # Reset file pointer for subsequent operations
                    f.seek(0)
                except Exception as e:
                    st.text(f"📄 {f.name} (Error reading pages)")
                    f.seek(0)
            st.markdown("---")

            if st.button("結合を実行", type="primary", use_container_width=True):
                merger = PdfWriter()
                for pdf in uploaded_files:
                    merger.append(pdf)
                
                output_buffer = io.BytesIO()
                merger.write(output_buffer)
                merger.close()
                
                st.success("結合完了！")
                st.download_button("結合PDFをダウンロード", output_buffer.getvalue(), "merged.pdf", "application/pdf", use_container_width=True)

        st.subheader("プレビュー確認")
        selected_preview = st.selectbox("プレビューするファイルを選択", [f.name for f in uploaded_files])
        
        target_file = next((f for f in uploaded_files if f.name == selected_preview), None)
        if target_file:
            pdf_viewer(target_file.getvalue(), height=600 if st.session_state.get('is_mobile') else 600)

# === 新機能: ページ並び替え ===
elif choice == "ページ並び替え (Reorder)":
    st.header("ページの順番を入れ替え")
    uploaded_file = st.file_uploader("PDFを選択", type="pdf")

    if uploaded_file:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        
        # Stacked layout: Controls top, Preview bottom
        st.subheader("並び順の設定")
        with st.container(border=True):
            st.info(f"**総ページ数:** {total_pages}")
            
            default_order = ",".join([str(i+1) for i in range(total_pages)])
            st.caption("欲しい順番にページ番号をコンマ区切りで入力してください。")
            
            new_order_str = st.text_area("新しいページ順序", value=default_order, height=100)
            
            if st.button("並び替えを実行", type="primary", use_container_width=True):
                try:
                    # 入力文字列を解析
                    order_list = [int(p.strip()) for p in new_order_str.split(',') if p.strip()]
                    
                    # 妥当性チェック
                    if any(p < 1 or p > total_pages for p in order_list):
                        st.error(f"ページ番号は 1 から {total_pages} の間で指定してください。")
                    else:
                        writer = PdfWriter()
                        for p_num in order_list:
                            writer.add_page(reader.pages[p_num - 1])
                        
                        out_buf = io.BytesIO()
                        writer.write(out_buf)
                        
                        st.success("並び替え完了！")
                        st.download_button("PDFをダウンロード", out_buf.getvalue(), "reordered.pdf", "application/pdf", use_container_width=True)
                        
                        # 結果プレビュー
                        st.markdown("---")
                        st.subheader("結果プレビュー")
                        pdf_viewer(out_buf.getvalue(), height=500)
                        
                except ValueError:
                    st.error("数字とコンマ(,)のみで入力してください。")

        st.subheader("ページ構成確認")
        st.caption("各ページの番号を確認してください。")
        
        # 高速化のため、画像生成はボタンアクションにするか、軽量に行う
        if st.checkbox("各ページのサムネイルを表示する", value=True):
            try:
                with st.spinner("サムネイル生成中..."):
                    # pdf2imageを使ってサムネイル生成
                    images = convert_from_bytes(uploaded_file.getvalue())
                    
                    # グリッド表示
                    cols = st.columns(3)
                    for i, img in enumerate(images):
                        with cols[i % 3]:
                            st.image(img, caption=f"Page {i+1}", use_container_width=True)
            except Exception as e:
                st.warning("サムネイルエラー: " + str(e))

elif choice == "PDF → 画像変換":
    st.header("PDFを画像(JPEG)に変換")
    uploaded_file = st.file_uploader("PDFを選択", type="pdf")
    
    if uploaded_file:
        # Stacked layout
        st.subheader("変換設定")
        with st.container(border=True):
            if st.button("画像に変換する", type="primary", use_container_width=True):
                try:
                    with st.spinner("変換中..."):
                        images = convert_from_bytes(uploaded_file.read())
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w") as zf:
                            for i, img in enumerate(images):
                                img_byte_arr = io.BytesIO()
                                img.save(img_byte_arr, format='JPEG')
                                zf.writestr(f"page_{i+1}.jpg", img_byte_arr.getvalue())
                        st.success("完了！")
                        st.download_button("画像ZIPをダウンロード", zip_buffer.getvalue(), "pdf_images.zip", "application/zip", use_container_width=True)
                except Exception as e:
                    st.error(f"エラー: {e}")

        st.subheader("プレビュー")
        pdf_viewer(uploaded_file.getvalue(), height=500 if st.session_state.get('is_mobile') else 700)

elif choice == "画像 → PDF変換":
    st.header("画像をPDFに変換")
    uploaded_files = st.file_uploader("画像を選択", type=["jpg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        st.subheader("PDF作成設定")
        with st.container(border=True):
            st.write(f"**枚数:** {len(uploaded_files)}枚")
            
            if st.button("PDFを作成", type="primary", use_container_width=True):
                image_list = []
                for img_file in uploaded_files:
                    image = Image.open(img_file).convert('RGB')
                    image_list.append(image)
                
                pdf_bytes = io.BytesIO()
                image_list[0].save(pdf_bytes, save_all=True, append_images=image_list[1:], format="PDF")
                st.success("完了！")
                st.download_button("PDFをダウンロード", pdf_bytes.getvalue(), "images.pdf", "application/pdf", use_container_width=True)

        st.subheader("画像プレビュー")
        cols = st.columns(3)
        for i, img_file in enumerate(uploaded_files):
            with cols[i % 3]:
                st.image(img_file, use_container_width=True)

elif choice == "PDF圧縮 (Compress)":
    st.header("PDFファイルサイズ圧縮")
    st.markdown("用途に合わせて圧縮モードを選択してください。")

    uploaded_file = st.file_uploader("圧縮するPDFをアップロード", type="pdf")

    if uploaded_file:
        # File ID check to clear cache if different file uploaded
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get("last_uploaded_file_id") != file_id:
            st.session_state["compressed_pdf"] = None
            st.session_state["last_uploaded_file_id"] = file_id

        file_size = len(uploaded_file.getvalue()) / 1024 / 1024
        st.info(f"現在のサイズ: **{file_size:.2f} MB**")

        col1, col2 = st.columns(2)
        with col1:
             mode = st.radio(
                "圧縮モード",
                ("標準 (Standard)", "高圧縮 (Strong)"),
                captions=[
                    "データの整理を行い、画質を落とさずに少し軽くします。",
                    "ページを画像化して再構築します。画質は落ちますがサイズは劇的に小さくなります。"
                ]
            )
        
        with col2:
             if "Strong" in mode:
                 quality = st.slider("画質品質 (低いほど軽い)", 10, 90, 50, help="数値を下げると画質が荒くなりますが、ファイルサイズは小さくなります。")
             else:
                 st.write("") # Spacer

        if "compressed_pdf" not in st.session_state:
            st.session_state["compressed_pdf"] = None
        
        # Check cache explicitly
        has_cache = st.session_state["compressed_pdf"] is not None

        if st.button("圧縮を実行", type="primary", use_container_width=True):
            output_buffer = io.BytesIO()
            
            try:
                # Reset file pointer just in case
                uploaded_file.seek(0)
                
                if "Standard" in mode:
                    # pypdfによる可逆圧縮 (ストリーム圧縮 & 重複排除)
                    with st.spinner("標準圧縮を実行中..."):
                        reader = PdfReader(uploaded_file)
                        writer = PdfWriter()
                        
                        for page in reader.pages:
                            writer.add_page(page)
                            try:
                                # Add page first, then compress the object in the writer
                                # This is safer than modifying the reader's page in-place
                                writer.pages[-1].compress_content_streams()
                            except Exception:
                                # Check if compression fails, just continue with uncompressed page
                                pass
                        
                        # メタデータ削減設定 (可能な場合)
                        # writer.compress_identical_objects = True # エラーの原因になることがあるため無効化 

                        writer.write(output_buffer)
                
                else:
                    # 画像化による強力圧縮
                    with st.spinner("高圧縮処理を実行中 (これには時間がかかります)..."):
                        # PDFを画像に変換 (DPIを少し下げる)
                        # Reset file pointer
                        uploaded_file.seek(0)
                        images = convert_from_bytes(uploaded_file.read(), dpi=150)
                        
                        image_list = []
                        for img in images:
                            # JPEGとして保存してサイズ削減
                            img_byte_arr = io.BytesIO()
                            img.convert('RGB').save(img_byte_arr, format='JPEG', quality=quality)
                            # 再度開いてリストに追加
                            image_list.append(Image.open(img_byte_arr))
                        
                        if image_list:
                            image_list[0].save(
                                output_buffer, 
                                save_all=True, 
                                append_images=image_list[1:], 
                                format="PDF"
                            )

                # Store result in session state
                st.session_state["compressed_pdf"] = output_buffer.getvalue()
                output_size = len(st.session_state["compressed_pdf"]) / 1024 / 1024
                reduction = (1 - output_size / file_size) * 100
                st.session_state["compression_results"] = (output_size, reduction)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
        
        # Display results if available
        if st.session_state["compressed_pdf"]:
            output_size, reduction = st.session_state.get("compression_results", (0, 0))
            
            st.success("圧縮完了！")
            col_res1, col_res2 = st.columns(2)
            col_res1.metric("圧縮後のサイズ", f"{output_size:.2f} MB", f"{reduction:.1f}% 削減")
            
            st.download_button(
                "圧縮PDFをダウンロード", 
                st.session_state["compressed_pdf"], 
                "compressed.pdf", 
                "application/pdf", 
                use_container_width=True,
                key="download_compressed_pdf"
            )

elif choice == "パスワード保護":
    st.header("PDF暗号化")
    uploaded_file = st.file_uploader("PDFを選択", type="pdf")
    
    if uploaded_file:
        st.subheader("セキュリティ設定")
        with st.container(border=True):
            password = st.text_input("パスワードを設定", type="password")
            
            if st.button("暗号化を実行", type="primary", use_container_width=True):
                if password:
                    reader = PdfReader(uploaded_file)
                    writer = PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)
                    writer.encrypt(password)
                    out_buf = io.BytesIO()
                    writer.write(out_buf)
                    st.success("暗号化完了！")
                    st.download_button("保護されたPDFをダウンロード", out_buf.getvalue(), "protected.pdf", "application/pdf", use_container_width=True)
                else:
                    st.warning("パスワードを入力してください。")

        st.subheader("プレビュー")
        pdf_viewer(uploaded_file.getvalue(), height=500 if st.session_state.get('is_mobile') else 700)