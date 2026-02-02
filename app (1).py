import streamlit as st
from PIL import Image
from io import BytesIO
import random

st.set_page_config(page_title="画像ツール", layout="wide")

st.title("📸 画像ツール")

if 'saved_side_images' not in st.session_state:
    st.session_state.saved_side_images = []

tab1, tab2, tab3 = st.tabs(["4分割のみ", "合成", "ワンステップ"])

def crop_to_16_9(img):
    """画像を16:9にトリミング"""
    target_ratio = 16 / 9
    current_ratio = img.width / img.height
    
    if current_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        right = left + new_width
        img_cropped = img.crop((left, 0, right, img.height))
    else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        bottom = top + new_height
        img_cropped = img.crop((0, top, img.width, bottom))
    
    return img_cropped

def split_4(img_cropped):
    """16:9の画像を4分割"""
    crop_width, crop_height = img_cropped.size
    center_x = crop_width // 2
    center_y = crop_height // 2
    
    return [
        img_cropped.crop((0, 0, center_x, center_y)),
        img_cropped.crop((center_x, 0, crop_width, center_y)),
        img_cropped.crop((0, center_y, center_x, crop_height)),
        img_cropped.crop((center_x, center_y, crop_width, crop_height))
    ], crop_width, crop_height

def resize_to_side_size(img, target_width, target_height):
    """画像を上下用サイズにトリミング＆リサイズ"""
    target_ratio = target_width / target_height
    current_ratio = img.width / img.height
    
    if current_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        right = left + new_width
        img_cropped = img.crop((left, 0, right, img.height))
    else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        bottom = top + new_height
        img_cropped = img.crop((0, top, img.width, bottom))
    
    side_img = img_cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
    return side_img

# ===== タブ1：4分割のみ =====
with tab1:
    st.subheader("画像を16:9にして4分割")
    
    uploaded_file = st.file_uploader("画像をアップロード", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], key="split_only")
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        original_width, original_height = img.size
        
        st.write(f"**元のサイズ:** {original_width} × {original_height}")
        
        img_cropped = crop_to_16_9(img)
        crop_width, crop_height = img_cropped.size
        st.write(f"**16:9トリミング後:** {crop_width} × {crop_height}")
        
        split_images, cw, ch = split_4(img_cropped)
        
        st.subheader("分割結果")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**1. 左上**")
            st.image(split_images[0], use_column_width=True)
        
        with col2:
            st.write("**2. 右上**")
            st.image(split_images[1], use_column_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.write("**3. 左下**")
            st.image(split_images[2], use_column_width=True)
        
        with col4:
            st.write("**4. 右下**")
            st.image(split_images[3], use_column_width=True)
        
        st.subheader("ダウンロード")
        
        col1, col2, col3, col4 = st.columns(4)
        
        for i, split_img in enumerate(split_images):
            with st.columns(4)[i]:
                buf = BytesIO()
                split_img.save(buf, format='PNG')
                buf.seek(0)
                st.download_button(f"{i+1}.png", buf.getvalue(), f"{i+1}.png", "image/png", key=f"split_{i}")
    
    else:
        st.info("👆 画像をアップロードしてください")

# ===== タブ2：合成 =====
with tab2:
    st.subheader("4分割メイン画像の上下に各2枚ずつ追加")
    
    st.write("**メイン画像をアップロード（4分割されます）**")
    main_file = st.file_uploader("メイン画像", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], key="main_composite")
    
    st.write("---")
    
    if len(st.session_state.saved_side_images) > 0:
        st.write(f"✓ 前回保存した上下用画像: {len(st.session_state.saved_side_images)}枚")
        
        use_saved = st.radio(
            "上下用画像の選択",
            ["前回の画像を使用", "新しい画像をアップロード"],
            key="radio_composite"
        )
        
        if use_saved == "新しい画像をアップロード":
            st.write("**新しい上下用画像をアップロード（4枚、不足時はランダム補充）**")
            side_files = st.file_uploader("上下用画像", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], accept_multiple_files=True, key="sides_composite")
            if len(side_files) > 0:
                st.session_state.saved_side_images = [Image.open(f) for f in side_files]
                st.success(f"✓ {len(side_files)}枚の画像を保存しました")
    else:
        st.write("**上下用画像をアップロード（4枚、不足時はランダム補充）**")
        side_files = st.file_uploader("上下用画像", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], accept_multiple_files=True, key="sides_composite")
        if len(side_files) > 0:
            st.session_state.saved_side_images = [Image.open(f) for f in side_files]
            st.success(f"✓ {len(side_files)}枚の画像を保存しました")
    
    if main_file is not None and len(st.session_state.saved_side_images) > 0:
        
        main_img = Image.open(main_file)
        original_width, original_height = main_img.size
        
        st.write(f"**メイン画像サイズ:** {original_width} × {original_height}")
        
        main_cropped = crop_to_16_9(main_img)
        crop_width, crop_height = main_cropped.size
        st.write(f"**16:9トリミング後:** {crop_width} × {crop_height}")
        
        split_images, cw, ch = split_4(main_cropped)
        
        side_width = crop_width
        side_height = crop_height // 2
        
        st.write(f"**上下用画像のサイズ:** {side_width} × {side_height}")
        
        # 4枚が必要（上2枚 + 下2枚）
        needed = 4
        final_sides = st.session_state.saved_side_images.copy()
        
        if len(final_sides) < needed:
            shortage = needed - len(final_sides)
            for _ in range(shortage):
                final_sides.append(random.choice(st.session_state.saved_side_images))
        
        random.shuffle(final_sides)
        resized_sides = [resize_to_side_size(img.copy(), side_width, side_height) for img in final_sides[:needed]]
        
        # 上部2枚、メイン、下部2枚を縦に繋ぐ
        top_img1 = resized_sides[0]
        top_img2 = resized_sides[1]
        bottom_img1 = resized_sides[2]
        bottom_img2 = resized_sides[3]
        
        # メイン画像（4分割）を1つの画像として作成
        main_split_width = crop_width // 2
        main_split_height = crop_height // 2
        
        main_combined_height = crop_height
        main_combined = Image.new('RGB', (crop_width, main_combined_height))
        
        y_offset = 0
        main_combined.paste(split_images[0], (0, y_offset))
        main_combined.paste(split_images[1], (main_split_width, y_offset))
        y_offset += main_split_height
        
        main_combined.paste(split_images[2], (0, y_offset))
        main_combined.paste(split_images[3], (main_split_width, y_offset))
        
        # 5つを縦に繋ぐ（全体用）
        total_height = top_img1.height + top_img2.height + main_combined.height + bottom_img1.height + bottom_img2.height
        final_image = Image.new('RGB', (crop_width, total_height))
        
        y_offset = 0
        final_image.paste(top_img1, (0, y_offset))
        y_offset += top_img1.height
        
        final_image.paste(top_img2, (0, y_offset))
        y_offset += top_img2.height
        
        final_image.paste(main_combined, (0, y_offset))
        y_offset += main_combined.height
        
        final_image.paste(bottom_img1, (0, y_offset))
        y_offset += bottom_img1.height
        
        final_image.paste(bottom_img2, (0, y_offset))
        
        st.subheader("プレビュー")
        st.image(final_image, use_column_width=True)
        
        st.subheader("ダウンロード")
        
        buf = BytesIO()
        final_image.save(buf, format='PNG')
        buf.seek(0)
        st.download_button("合成画像.png", buf.getvalue(), "合成画像.png", "image/png", key="download_composite")
    
    else:
        st.info("👆 メイン画像と上下用画像をアップロードしてください")

# ===== タブ3：ワンステップ =====
with tab3:
    st.subheader("一気に処理（4分割+合成）")
    
    st.write("**メイン画像をアップロード**")
    main_file_onestep = st.file_uploader("メイン画像", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], key="main_onestep")
    
    st.write("**上下用画像をアップロード（4枚、不足時はランダム補充）**")
    side_files_onestep = st.file_uploader("上下用画像", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], accept_multiple_files=True, key="sides_onestep")
    
    if main_file_onestep is not None and len(side_files_onestep) > 0:
        st.write(f"✓ {len(side_files_onestep)}枚の上下用画像がアップロードされました")
        
        main_img = Image.open(main_file_onestep)
        original_width, original_height = main_img.size
        
        st.write(f"**メイン画像サイズ:** {original_width} × {original_height}")
        
        main_cropped = crop_to_16_9(main_img)
        crop_width, crop_height = main_cropped.size
        st.write(f"**16:9トリミング後:** {crop_width} × {crop_height}")
        
        split_images, cw, ch = split_4(main_cropped)
        
        side_width = crop_width
        side_height = crop_height // 2
        
        st.write(f"**上下用画像のサイズ:** {side_width} × {side_height}")
        
        side_images = [Image.open(f) for f in side_files_onestep]
        
        needed = 4
        final_sides = side_images.copy()
        
        if len(final_sides) < needed:
            shortage = needed - len(final_sides)
            for _ in range(shortage):
                final_sides.append(random.choice(side_images))
        
        random.shuffle(final_sides)
        resized_sides = [resize_to_side_size(img.copy(), side_width, side_height) for img in final_sides[:needed]]
        
        top_img1 = resized_sides[0]
        top_img2 = resized_sides[1]
        bottom_img1 = resized_sides[2]
        bottom_img2 = resized_sides[3]
        
        main_split_width = crop_width // 2
        main_split_height = crop_height // 2
        
        main_combined_height = crop_height
        main_combined = Image.new('RGB', (crop_width, main_combined_height))
        
        y_offset = 0
        main_combined.paste(split_images[0], (0, y_offset))
        main_combined.paste(split_images[1], (main_split_width, y_offset))
        y_offset += main_split_height
        
        main_combined.paste(split_images[2], (0, y_offset))
        main_combined.paste(split_images[3], (main_split_width, y_offset))
        
        total_height = top_img1.height + top_img2.height + main_combined.height + bottom_img1.height + bottom_img2.height
        final_image = Image.new('RGB', (crop_width, total_height))
        
        y_offset = 0
        final_image.paste(top_img1, (0, y_offset))
        y_offset += top_img1.height
        
        final_image.paste(top_img2, (0, y_offset))
        y_offset += top_img2.height
        
        final_image.paste(main_combined, (0, y_offset))
        y_offset += main_combined.height
        
        final_image.paste(bottom_img1, (0, y_offset))
        y_offset += bottom_img1.height
        
        final_image.paste(bottom_img2, (0, y_offset))
        
        st.subheader("プレビュー")
        st.image(final_image, use_column_width=True)
        
        st.subheader("ダウンロード")
        
        buf = BytesIO()
        final_image.save(buf, format='PNG')
        buf.seek(0)
        st.download_button("合成画像.png", buf.getvalue(), "合成画像.png", "image/png", key="download_onestep")
    
    else:
        st.info("👆 メイン画像と上下用画像をアップロードしてください")
