# Ghost Writer AI 👻

Transform ideas into compelling content with AI-powered writing assistance.

## Features

- 🎯 SEO-optimized blog post generation
- 🎨 AI-powered image generation with DALL-E
- 📝 Multiple tone options (Professional, Casual, Humorous, etc.)
- 📊 Customizable word count (250-2000 words)
- 💾 Download as Markdown or plain text

## Deployment

This app is deployed on Streamlit Cloud.

## Tech Stack

- **Frontend**: Streamlit
- **AI Models**: OpenAI GPT-4o & DALL-E 3
- **Language**: Python

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `api_key.py` with your OpenAI API key:
```python
   openai_api_key = "your-api-key-here"
```
4. Run: `streamlit run app.py`
