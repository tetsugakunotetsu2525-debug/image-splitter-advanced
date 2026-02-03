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
                if 'comp_sides' in st.session_state:
                    del st.session_state.comp_sides
                st.success(f"✓ {len(side_files)}枚の画像を保存しました")
    else:
        st.write("**上下用画像をアップロード（4枚、不足時はランダム補充）**")
        side_files = st.file_uploader("上下用画像", type=['png', 'jpg', 'jpeg', 'bmp', 'gif'], accept_multiple_files=True, key="sides_composite")
        if len(side_files) > 0:
            st.session_state.saved_side_images = [Image.open(f) for f in side_files]
            if 'comp_sides' in st.session_state:
                del st.session_state.comp_sides
            st.success(f"✓ {len(side_files)}枚の画像を保存しました")
    
    if main_file is not None and len(st.session_state.saved_side_images) > 0:
        
        main_img = Image.open(main_file)
        original_width, original_height = main_img.size
        
        st.write(f"**メイン画像サイズ:** {original_width} × {original_height}")
        
        main_cropped = crop_to_16_9(main_img)
        crop_width, crop_height = main_cropped.size
        st.write(f"**16:9トリミング後:** {crop_width} × {crop_height}")
        
        split_images, cw, ch = split_4(main_cropped)
        
        split_width = crop_width // 2
        split_height = crop_height // 2
        
        st.write(f"**基準サイズ（メイン分割後）:** {split_width} × {split_height}")
        
        needed = 4
        final_sides = st.session_state.saved_side_images.copy()
        
        if len(final_sides) < needed:
            shortage = needed - len(final_sides)
            for _ in range(shortage):
                final_sides.append(random.choice(st.session_state.saved_side_images))
        
        if 'comp_heights' not in st.session_state:
            st.session_state.comp_heights = {}
        
        if 'comp_sides' not in st.session_state:
            st.session_state.comp_sides = {}
            for idx in range(4):
                shuffled = final_sides.copy()
                random.shuffle(shuffled)
                st.session_state.comp_sides[idx] = shuffled
        
        final_images = []
        
        for idx, split_img in enumerate(split_images):
            shuffled_sides = st.session_state.comp_sides[idx]
            
            if idx not in st.session_state.comp_heights:
                st.session_state.comp_heights[idx] = generate_heights(split_height)
            
            h1, h2, h3, h4 = st.session_state.comp_heights[idx]
            
            top_img1 = resize_to_split_size(shuffled_sides[0].copy(), split_width, h1)
            top_img2 = resize_to_split_size(shuffled_sides[1].copy(), split_width, h2)
            bottom_img1 = resize_to_split_size(shuffled_sides[2].copy(), split_width, h3)
            bottom_img2 = resize_to_split_size(shuffled_sides[3].copy(), split_width, h4)
            
            total_height = h1 + h2 + split_height + h3 + h4
            combined = Image.new('RGB', (split_width, total_height))
            
            y_offset = 0
            combined.paste(top_img1, (0, y_offset))
            y_offset += h1
            
            combined.paste(top_img2, (0, y_offset))
            y_offset += h2
            
            combined.paste(split_img, (0, y_offset))
            y_offset += split_height
            
            combined.paste(bottom_img1, (0, y_offset))
            y_offset += h3
            
            combined.paste(bottom_img2, (0, y_offset))
            
            final_images.append(combined)
        
        st.subheader("プレビュー")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.image(final_images[0], width=150)
        with col2:
            st.image(final_images[1], width=150)
        with col3:
            st.image(final_images[2], width=150)
        with col4:
            st.image(final_images[3], width=150)
        
        st.subheader("ダウンロード")
        
        zip_data = create_zip(final_images)
        st.download_button(
            label="📦 ZIP一括ダウンロード",
            data=zip_data,
            file_name="合成画像.zip",
            mime="application/zip",
            key="comp_zip"
        )
        
        st.write("**個別ダウンロード**")
        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1:
            buf = BytesIO()
            final_images[0].save(buf, format='PNG')
            buf.seek(0)
            st.download_button("1.png", buf.getvalue(), "1.png", "image/png", key="comp_1", use_container_width=True)
        with col2:
            buf = BytesIO()
            final_images[1].save(buf, format='PNG')
            buf.seek(0)
            st.download_button("2.png", buf.getvalue(), "2.png", "image/png", key="comp_2", use_container_width=True)
        with col3:
            buf = BytesIO()
            final_images[2].save(buf, format='PNG')
            buf.seek(0)
            st.download_button("3.png", buf.getvalue(), "3.png", "image/png", key="comp_3", use_container_width=True)
        with col4:
            buf = BytesIO()
            final_images[3].save(buf, format='PNG')
            buf.seek(0)
            st.download_button("4.png", buf.getvalue(), "4.png", "image/png", key="comp_4", use_container_width=True)
    
    else:
        st.info("👆 メイン画像と上下用画像をアップロードしてください")
