# Artha AI

> Generate production-ready labeled datasets for Indian languages in minutes

**Artha AI** is an AI-powered platform that generates high-quality labeled datasets in **Hindi, Gujarati, Tamil, Marathi, Bengali, Telugu, Kannada** and more. Perfect for training sentiment analysis, intent classification, and toxicity detection models.

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue)](https://artha-ai.dev)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

---

## 🎯 Features

✨ **8+ Indian Languages** - Hindi, Gujarati, Tamil, Marathi, Bengali, Telugu, Kannada, English

🤖 **AI-Powered Labeling** - Automatic sentiment, intent, and toxicity detection

📊 **Multiple Export Formats** - CSV, JSON, Excel, Parquet, HuggingFace

⚡ **Fast Generation** - Get 100+ labeled rows in 2-5 minutes

✅ **Quality Assured** - Built-in quality scoring and balance checks

🔒 **Secure & Private** - Your data stays private and secure

---

## 🚀 How It Works

1. **Select Languages** → Choose from 8+ Indian languages
2. **Choose Label Type** → Sentiment, Intent, or Toxicity
3. **Set Quantity** → 10 to 500 rows per language
4. **Generate** → AI processes your request
5. **Download** → Get your labeled dataset in multiple formats

---

## 💡 Use Cases

- **Sentiment Analysis** - Train models for e-commerce reviews, social media monitoring
- **Intent Classification** - Build chatbots and virtual assistants
- **Toxicity Detection** - Content moderation for Indian language platforms
- **Research & Academia** - Dataset generation for NLP research
- **Startup MVPs** - Quick prototyping for AI products

---

## 🎥 Demo

Visit [artha-ai.dev](https://artha-ai.dev) to try it now!

*(Add screenshots or demo video here)*

---

## 📊 Example Output

```csv
text_clean,label_sentiment,confidence,language
"यह बहुत अच्छा है",positive,0.92,hi
"આ સરસ છે",positive,0.89,gu
"यह ठीक नहीं है",negative,0.87,hi
```

**22 columns per row** including:
- Original & cleaned text
- Sentiment/Intent/Toxicity labels
- Confidence scores
- Language detection
- Source metadata
- Quality indicators

---

## 🏗️ Tech Stack

**Frontend:** Next.js, React, TypeScript, TailwindCSS

**Backend:** FastAPI, Celery, PostgreSQL, Redis

**AI/ML:** Groq, OpenRouter, Anthropic Claude, OpenAI

**Infrastructure:** Vercel, Railway, Supabase, Upstash

---

## 🛠️ For Developers

Want to contribute or run locally?

### Quick Start

```bash
# Clone repository
git clone https://github.com/Parshva2605/Artha.ai.git
cd Artha.ai

# Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# Configure environment
cp .env.example .env
# Add your API keys

# Run with Docker
docker compose up
```

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed instructions.

### API Access

```python
import requests

response = requests.post('https://api.artha-ai.dev/api/generate-dataset', 
    json={
        "languages": ["hi", "gu"],
        "quantity_per_language": 100,
        "label_type": "sentiment",
        "export_formats": ["csv", "json"]
    }
)
```

API documentation: [api.artha-ai.dev/docs](https://api.artha-ai.dev/docs)

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 📧 Support

- **Email:** support@artha-ai.dev
- **GitHub Issues:** [Report a bug](https://github.com/Parshva2605/Artha.ai/issues)
- **Documentation:** [docs.artha-ai.dev](https://docs.artha-ai.dev)

---

## 🙏 Acknowledgments

Built for the Indian AI ecosystem to support low-resource language development.

---

**[Try Artha AI Now →](https://artha-ai.dev)**

Made with ❤️ for Indian Language AI

