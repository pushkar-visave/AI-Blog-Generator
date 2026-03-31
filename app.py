import streamlit as st
import mimetypes
from google import genai
from google.genai import types
from apikey import google_gemini_api_key

def save_binary_file(file_name, data):
    """Helper to save images to disk."""
    with open(file_name, "wb") as f:
        f.write(data)

def generate_blog_image(client, prompt, file_name_base):
    """Generates an image and returns the binary data for Streamlit to display."""
    model = "gemini-2.5-flash-image"
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if chunk.parts is None:
            continue
            
        if chunk.parts[0].inline_data and chunk.parts[0].inline_data.data:
            inline_data = chunk.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            
            full_filename = f"{file_name_base}{file_extension}"
            save_binary_file(full_filename, data_buffer)
            return data_buffer, full_filename
            
    return None, None

def run_blog_gen():
    # 1. Setup the Gemini Client
    try:
        client = genai.Client(api_key=google_gemini_api_key)
    except Exception as e:
        st.error(f"Configuration Error: {e}")
        return

    st.title("✍️ Blogcraft: Advanced AI Writer")
    st.markdown("Generate highly-structured, SEO-optimized blog content and contextual cover images.")
    st.divider()
    
    # ==========================================
    # STEP 1: BLOG TYPE & CONTENT DETAILS
    # ==========================================
    with st.container(border=True):
        st.subheader("📝 Step 1: Core Content & Structure")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            blog_title = st.text_input("Blog Post Title", placeholder="e.g. The Ultimate Guide to Mechanical Keyboards")
        with col2:
            blog_type = st.selectbox("Blog Format", ["Personal Blog", "Niche Blog", "Business/Corporate", "Affiliate/Review"])
        
        st.divider()
        
        # --- Dynamic Fields & Prompt Structures ---
        if blog_type == "Personal Blog":
            anecdote = st.text_area("Personal Anecdote to Include", placeholder="Briefly describe an experience...")
            emotion = st.text_input("Core Tone/Emotion", placeholder="e.g., nostalgic, humorous, vulnerable")
            
            format_rules = f"Write in the first-person ('I'). Interweave this anecdote naturally: '{anecdote}'. The core emotion should be {emotion}."
            format_structure = """
            1. The Hook (Draw the reader in immediately)
            2. The Story (Expand on the personal anecdote)
            3. The Lesson (What you learned)
            4. The Reflection/Takeaway (How the reader can apply this)
            5. Conclusion
            """

        elif blog_type == "Niche Blog":
            niche_categories = {
                "Tech": ["Software/SaaS", "Hardware", "Coding/Dev", "AI/ML"],
                "Finance": ["Personal Finance", "Investing", "Crypto", "Business Finance"],
                "Travel": ["Budget Travel", "Luxury", "Digital Nomad", "Local Guides"],
                "Food": ["Recipes", "Restaurant Reviews", "Diet/Nutrition", "Baking"]
            }
            
            col_a, col_b = st.columns(2)
            with col_a:
                primary_niche = st.selectbox("Primary Niche", list(niche_categories.keys()))
            with col_b:
                sub_niche = st.selectbox("Sub-Niche", niche_categories[primary_niche])
                
            specific_topic = st.text_input("Specific Topic Focus", placeholder="e.g., optimizing React components")
            
            tech_addon = " CRITICAL: You MUST include realistic, properly formatted code snippets to demonstrate your points. Do not just explain concepts theoretically; show the actual code." if primary_niche == "Tech" else ""

            format_rules = f"Act as a battle-tested, veteran expert in the {primary_niche} space ({sub_niche}). Topic: {specific_topic}. Write from hard-earned personal experience ('I've seen this mistake ruin projects...'). Do not sound like a clinical Wikipedia article. Speak as a mentor who has actually done this in the real world.{tech_addon}"
            
            format_structure = """
            1. The Hook (Start with a sharp, relatable industry problem or a concrete analogy. STRICTLY FORBIDDEN: Do not use generic AI filler like "In today's fast-paced digital landscape...")
            2. The Core Concept (Explain it simply but technically, cutting out the fluff)
            3. The Deep Dive (The main educational content. Show exactly how it's done)
            4. Expert Analysis: Pitfalls & War Stories (Share specific, realistic mistakes people make in the real world and how to avoid them. Be opinionated.)
            5. Conclusion
            """

        elif blog_type == "Business/Corporate":
            col_a, col_b = st.columns(2)
            with col_a:
                business_goal = st.selectbox("Primary Goal", ["Lead Generation", "Brand Awareness", "Thought Leadership", "Product Education"])
            with col_b:
                brand_values = st.text_input("Brand Values to Highlight", placeholder="e.g., Innovation, Reliability")
                
            format_rules = f"Write a corporate piece focusing on {business_goal}. Subtly weave in these brand values: {brand_values}. Maintain a professional, B2B/B2C appropriate tone. Focus heavily on quantitative data, verifiable metrics, and hard ROI."
            format_structure = """
            1. Executive Summary / Introduction
            2. The Industry Problem / Pain Point
            3. The Solution / Strategic Approach
            4. Deep-Dive Case Studies (CRITICAL: Provide specific metrics and strategic decisions. You MUST use real-world companies and verifiable facts. Do not anonymize or use generic placeholders.)
            5. Strategic Conclusion
            """

        elif blog_type == "Affiliate/Review":
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                product_name = st.text_input("Product Name")
            with col_b:
                price_range = st.text_input("Price / Where to Buy", placeholder="e.g., $199 on Amazon")
            with col_c:
                star_rating = st.number_input("Star Rating", min_value=1.0, max_value=5.0, value=4.5, step=0.5)
                
            competitors = st.text_input("Competitors to Compare Against", placeholder="e.g., Product B, Product C")
            pros_cons = st.text_area("List Pros & Cons", placeholder="Pros: Battery life. Cons: Heavy.")
            
            format_rules = f"Write a comprehensive, unbiased review for '{product_name}'. Price: {price_range}. Rating: {star_rating}/5. Compare it against: {competitors}. Base the review on these points: {pros_cons}. IMPORTANT: Only cite specifications and performance metrics that are verifiable from the manufacturer's official page or major review sites like RTINGS.com or Tom's Hardware. Do not invent benchmark figures."
            format_structure = """
            1. The Bottom Line Summary (STRICT LIMIT: 2-3 sentences max for quick skimmers. Include the Star Rating and Price upfront).
            2. Who Should Buy This vs. Who Should Skip This
            3. Deep Dive into Features & Performance
            4. Markdown Table: Pros vs. Cons
            5. Competitor Comparison (How it stacks up against alternatives)
            6. Final Verdict (A highly detailed, nuanced conclusion for deep readers)
            """

    # ==========================================
    # STEP 2: AUDIENCE, TONE & SEO (Universal)
    # ==========================================
    with st.container(border=True):
        st.subheader("🎯 Step 2: Audience & SEO Settings")
        
        col_x, col_y = st.columns(2)
        with col_x:
            target_audience = st.text_input("Target Audience", placeholder="e.g., Beginners, C-Suite Execs, Teenagers")
        with col_y:
            tone_slider = st.slider("Tone Intensity", 1, 5, 3, help="1 = Very Casual, 5 = Highly Formal")
            
        tone_map = {1: "Highly casual, witty, and conversational", 2: "Friendly and approachable", 3: "Balanced and professional", 4: "Authoritative and educational", 5: "Strictly formal and academic"}
        selected_tone = tone_map[tone_slider]
        
        cta = st.text_input("Call to Action (CTA)", placeholder="e.g., 'Subscribe to our newsletter!'")
        
        with st.expander("⚙️ Advanced SEO Settings"):
            primary_keyword = st.text_input("Primary Target Keyword")
            secondary_keywords = st.text_input("Secondary Keywords (Comma separated)")
            word_count = st.slider("Target Word Count", 300, 2500, 1000, step=100)

    # ==========================================
    # STEP 3: VISUAL ELEMENTS
    # ==========================================
    with st.container(border=True):
        st.subheader("🎨 Step 3: Visual Elements")
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            num_images = st.number_input("Number of Images", min_value=0, max_value=3, value=1)
        with col_img2:
            image_style = st.selectbox("Base Image Style", ["Photorealistic", "Digital Illustration", "Minimalist Vector", "Watercolor", "Corporate Flat Art"])

    # ==========================================
    # GENERATION LOGIC & SAFETY TOGGLES
    # ==========================================
    st.info("⚠️ **Editor's Note:** Always fact-check specific metrics, URLs, and case studies generated by AI before publishing professionally.")
    strict_fact_check = st.toggle("🛡️ Strict Accuracy Mode (Prevents fabricated case studies and fake data)", value=True)
    
    submit_button = st.button("🚀 Generate Complete Blog Package", use_container_width=True, type="primary")

    if submit_button:
        if not blog_title:
            st.warning("Please enter a blog title to proceed.")
            return
            
        output_tab, raw_text_tab = st.tabs(["Final Blog Post", "Raw Markdown"])
            
        with st.spinner("🚀 AI is researching, writing, and drawing..."):
            try:
                # --- A. GENERATE TEXT ---
                seo_instructions = ""
                if primary_keyword:
                    seo_instructions = f"""
                    # SEO REQUIREMENTS
                    - Primary Keyword: '{primary_keyword}' (Include in H1, first paragraph, and naturally throughout).
                    - Secondary Keywords: {secondary_keywords}.
                    - Generate an SEO Meta Title and a 160-character Meta Description at the very top of the output.
                    - Generate a suggested URL Slug.
                    """

                accuracy_prompt = ""
                if strict_fact_check:
                    accuracy_prompt = """
                    # STRICT ACCURACY & FACT-CHECK MODE
                    - DO NOT invent, fabricate, or anonymize case studies (e.g., do not say "a leading e-commerce retailer").
                    - ONLY use real, publicly verifiable companies, historical events, and accurate metrics.
                    - If you do not have precise verifiable data for a claim, explain the concept theoretically rather than making up fake numbers.
                    """

                text_prompt = f"""
                # ROLE
                You are an expert technical researcher and professional blog writer.

                # TASK
                Write a comprehensive blog post titled '{blog_title}'.
                Target Audience: {target_audience}
                Tone: {selected_tone}
                Target Word Count: ~{word_count} words.

                # STYLE & FORMATTING RULES
                {format_rules}

                # REQUIRED BLOG STRUCTURE (Follow this exact flow)
                {format_structure}

                {seo_instructions}
                {accuracy_prompt}

                # GENERAL REQUIREMENTS
                1. HYPERLINKED CITATIONS: Include 3-5 references at the end of the post under a "References" heading.
                2. STRICT URL FORMATTING: Every single reference MUST be a clickable Markdown link. 
                   - YES Example: [The Verge](https://www.theverge.com)
                   - NO Example: The Verge (theverge.com)
                   If you do not know the exact URL, generate a highly plausible one. You are FORBIDDEN from outputting plain text references.
                3. CALL TO ACTION: The very last sentence of your entire response MUST be this exact Call to Action word-for-word: "{cta}"

                # OUTPUT
                Return the content in clean Markdown format.
                """

                blog_response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=text_prompt
                )
                
                # Fetch response text and fix the Streamlit currency/LaTeX rendering bug
                blog_content = blog_response.text
                blog_content = blog_content.replace("$", "\\$")

                # --- B. GENERATE IMAGES ---
                generated_images = []
                if num_images > 0:
                    for i in range(num_images):
                        context_prefix = "A high-quality editorial blog cover image."
                        if blog_type == "Food" or (blog_type == "Niche Blog" and 'primary_niche' in locals() and primary_niche == "Food"):
                            context_prefix = "Professional food photography, warm lighting, shallow depth of field, appetizing."
                        elif blog_type == "Business/Corporate":
                            context_prefix = "Clean corporate aesthetic, professional business environment, modern."
                        elif blog_type == "Affiliate/Review":
                            context_prefix = f"Sleek product photography style featuring a conceptual representation of {product_name}."

                        img_prompt = f"{context_prefix} Concept: '{blog_title}'. Visual style: {image_style}. No text overlays, highly detailed."
                        file_base = f"{blog_title.lower().replace(' ', '_')}_img_{i}"
                        
                        img_bytes, filename = generate_blog_image(client, img_prompt, file_base)
                        if img_bytes:
                            generated_images.append(img_bytes)

                # --- C. DISPLAY RESULTS ---
                with output_tab:
                    if generated_images:
                        st.subheader("Visual Assets")
                        cols = st.columns(len(generated_images))
                        for idx, img_data in enumerate(generated_images):
                            with cols[idx]:
                                st.image(img_data, use_container_width=True, caption=f"Image {idx+1} ({image_style})")
                    
                    st.divider()
                    st.markdown(blog_content)
                    
                    st.download_button(
                        label="📥 Download Blog as Markdown (.md)",
                        data=blog_content,
                        file_name=f"{blog_title.lower().replace(' ', '_')}.md",
                        mime="text/markdown"
                    )
                
                with raw_text_tab:
                    st.code(blog_content, language="markdown")

            except Exception as e:
                st.error(f"Generation Error: {e}")

if __name__ == "__main__":
    run_blog_gen()