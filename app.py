import streamlit as st
import os
import time
from openai import OpenAI

# Configure OpenAI - Use Streamlit secrets
try:
    openai_api_key = st.secrets["openai_api_key"]
except:
    # Fallback for local development
    try:
        from api_key import openai_api_key
    except:
        st.error("Please configure your OpenAI API key in Streamlit secrets")
        st.stop()

client = OpenAI(api_key=openai_api_key)

# Set app to wide mode
st.set_page_config(layout="wide", page_title="Ghost Writer AI 👻")

# Sidebar User Input
with st.sidebar:
    st.title("Input Your Blog Details")
    st.subheader("Provide the necessary information to generate your blog post")

    # Blog Title Input
    blog_title = st.text_input("Blog Title")

    # Blog Keywords Input
    blog_keywords = st.text_area("Blog Keywords (separated by commas)")

    # Blog Tone Selection
    blog_tone = st.selectbox("Select Blog Tone", ["Professional", "Casual", "Humorous", "Inspirational", "Informative"])
    
    # Blog Length Selection
    blog_length = st.select_slider("Number of words", range(250, 2000, 250), value=500)

    # Number of Images Selection
    num_images = st.number_input("Number of Images", min_value=0, max_value=10, value=0)

    # Generate Button
    generate_button = st.button("Generate Blog Post")


def generate_dalle_image(prompt, size="1024x1024"):
    """Generate image using DALL-E"""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        st.warning(f"Could not generate image: {str(e)}")
        return None


def generate_blog_post(blog_title, blog_keywords, blog_tone, blog_length, num_images):
    """Generate blog post using OpenAI GPT with comprehensive prompt"""
    
    # Create the comprehensive prompt
    system_prompt = """You are an expert content writer and blogger with years of experience creating engaging, SEO-optimized content across various niches. Your task is to generate high-quality blog posts that captivate readers and provide genuine value."""
    
    # Conditional image instructions
    image_instructions = ""
    if num_images > 0:
        image_instructions = f"""
6. IMAGE SUGGESTIONS:
   - Provide {num_images} specific image placement suggestions throughout the blog
   - For each image, describe: what it should show, where it should be placed, and why it enhances the content
   - Format image suggestions as: [IMAGE PLACEHOLDER: Brief description of what the image should show]
"""
    else:
        image_instructions = """
6. NO IMAGES:
   - Do NOT include any image placeholders or suggestions
   - Focus purely on text content
"""
    
    user_prompt = f"""Generate a comprehensive, well-structured blog post based on the following parameters:

INPUTS:
- Title: {blog_title}
- Keywords: {blog_keywords}
- Tone: {blog_tone}
- Word Count: {blog_length} words
- Number of Images: {num_images}

REQUIREMENTS:

1. STRUCTURE:
   - Craft a compelling, attention-grabbing introduction (10-15% of total length)
   - Organize content with clear H2 and H3 headings for readability
   - Include 3-5 main sections that flow logically
   - Write a strong conclusion with a call-to-action or key takeaway

2. CONTENT QUALITY:
   - Provide original, insightful content that demonstrates expertise
   - Include relevant examples, statistics, or case studies where appropriate
   - Maintain the specified tone ({blog_tone}) consistently throughout
   - Naturally incorporate the provided keywords without keyword stuffing
   - Use transition phrases to ensure smooth flow between sections

3. READABILITY:
   - Write for an online audience with scannable content
   - Use short paragraphs (2-4 sentences each)
   - Include bullet points or numbered lists where appropriate
   - Vary sentence length for natural rhythm
   - Avoid jargon unless the topic demands it (then explain technical terms)

4. ENGAGEMENT:
   - Hook readers in the first 2-3 sentences
   - Use storytelling elements where relevant
   - Ask rhetorical questions to maintain reader interest
   - Include actionable insights or practical tips
   - End with a memorable conclusion that reinforces main points

5. SEO OPTIMIZATION:
   - Incorporate keywords naturally in headings and throughout content
   - Front-load important information
   - Use semantic variations of main keywords

{image_instructions}

OUTPUT FORMAT:
Deliver the blog post in clean markdown format with:
- Clear heading hierarchy (# for title, ## for H2, ### for H3)
- Proper paragraph breaks
- Bold text for emphasis where appropriate
- Bullet points or numbered lists where they enhance readability
- Image placement markers clearly indicated ONLY if images are requested

Begin writing the blog post now:
"""

    try:
        full_response = ""
        
        # Generate content with OpenAI
        response_placeholder = st.empty()
        
        stream = client.chat.completions.create(
            model="gpt-4o",  
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=True,
            temperature=0.7,
            max_tokens=4096,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                response_placeholder.markdown(full_response)
        
        # Generate images if num_images > 0
        image_urls = []
        if num_images > 0:
            # Extract image descriptions from the blog content
            import re
            image_descriptions = re.findall(r'\[IMAGE PLACEHOLDER: (.*?)\]', full_response)
            
            for i, desc in enumerate(image_descriptions[:num_images]):
                with st.spinner(f"Generating image {i+1}/{num_images}..."):
                    # Create a more detailed prompt for DALL-E
                    image_prompt = f"{desc}, high quality, professional photography style"
                    image_url = generate_dalle_image(image_prompt)
                    if image_url:
                        image_urls.append(image_url)
                        # Replace placeholder with actual image
                        full_response = full_response.replace(
                            f'[IMAGE PLACEHOLDER: {desc}]',
                            f'![Generated Image {i+1}]({image_url})\n*{desc}*'
                        )
                        response_placeholder.markdown(full_response)
                        time.sleep(1)  # Small delay between image generations
        
        return full_response, image_urls
        
    except Exception as e:
        error_msg = str(e)
        st.error(f"An error occurred: {error_msg}")
        return None, []


# Main content area
# Only show header if no blog post is being generated
if not generate_button or not blog_title or not blog_keywords:
    # Title of the app
    st.title("Ghost Writer AI 👻")

    # Subheader of the app
    st.subheader("Transform ideas into compelling content with AI-powered writing assistance")

    # Description
    st.write("Whether you're battling writer's block, seeking creative inspiration, or crafting your next masterpiece, Ghost Writer AI brings professional-quality writing to your fingertips. Powered by advanced AI, this tool helps you generate blog posts, stories, and creative content that resonates with your audience.")

if generate_button:
    if not blog_title:
        st.warning("Please enter a blog title to generate content.")
    elif not blog_keywords:
        st.warning("Please enter at least one keyword.")
    else:
        # Generate blog post directly without showing configuration
        blog_content, image_urls = generate_blog_post(
            blog_title=blog_title,
            blog_keywords=blog_keywords,
            blog_tone=blog_tone,
            blog_length=blog_length,
            num_images=num_images
        )
        
        if blog_content:
            st.success("Blog post generated successfully!")
            
            # Display metrics
            cols = st.columns(4 if image_urls else 3)
            with cols[0]:
                word_count = len(blog_content.split())
                st.metric("Word Count", f"{word_count:,}")
            with cols[1]:
                char_count = len(blog_content)
                st.metric("Character Count", f"{char_count:,}")
            with cols[2]:
                reading_time = max(1, word_count // 200)
                st.metric("Reading Time", f"{reading_time} min")
            
            if image_urls and len(cols) > 3:
                with cols[3]:
                    st.metric("Images Generated", len(image_urls))
            
            st.divider()
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="Download as Markdown",
                    data=blog_content,
                    file_name=f"{blog_title.replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col2:
                plain_text = blog_content.replace('#', '').replace('**', '')
                st.download_button(
                    label="Download as Text",
                    data=plain_text,
                    file_name=f"{blog_title.replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col3:
                if st.button("Generate Another Version", use_container_width=True):
                    st.rerun()
            
else:
    st.info("Fill in the details in the sidebar and click 'Generate Blog Post' to get started!")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>Powered by OpenAI GPT-4 & DALL-E • Ghost Writer AI 👻</p>
</div>
""", unsafe_allow_html=True)