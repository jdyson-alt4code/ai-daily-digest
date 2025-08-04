# 🤖 AI Digest Generator

Automatically generate a daily digest of the latest AI model, tool, and research blog updates.
Outputs include:

* 📄 `digest.md`: Clean markdown blog post
* 🌐 `digest.html`: Beautiful, readable HTML article
* 👡 `digest_tweet.txt`: A tweet-sized summary

Perfect for AI curators, researchers, and developers who want a quick summary of what’s new in the ecosystem.

---

## 🎞️ Features

* ✅ Pulls from 30+ GitHub & AI blog RSS feeds
* 🧠 Uses a local Ollama model to generate structured summaries
* 🗓 Filters updates from the **last 3 days**
* 🧹 Includes recent ComfyUI workflows
* ✨ Outputs both markdown and styled HTML
* 📁 All outputs are saved by date in an `/output/YYYY-MM-DD/` folder

---

## 🧰 Requirements

Install dependencies:

```bash
pip install markdown feedparser beautifulsoup4 python-dateutil requests
```

Run a local [Ollama](https://ollama.com) instance:

```bash
ollama run gemma3:27b
```

> You can change the model in the script:
> `OLLAMA_MODEL = "gemma3:27b"`

---

## 🚀 How to Use (Windows)

### ⚙️ 1. Download & Set Up

Clone this repository or download the script folder:

```
ai_digest_automation/
│
├── digest_generator.py
├── /output/
└── [Optional] /venv/
```

If you want to use a virtual environment (recommended):

```bash
python -m venv venv
venv\Scripts\activate
pip install markdown feedparser beautifulsoup4 python-dateutil requests

```

---

### ▶️ 2. Run the Script Manually

Run once to test:

```bash
python digest_generator.py
```

Your output will appear in:

```
output/YYYY-MM-DD/
├── digest.md
├── digest.html
└── digest_tweet.txt
```

You can open `digest.html` in any browser for a blog-style view.

---

## ⚖️ Terms of Use / Fair Use Notice

This script:

* ✅ Pulls public data from **RSS feeds**
* ✅ Only summarizes short excerpts or metadata
* ✅ Links back to original sources in all output

### ⚠️ Use Responsibly:

* Avoid copying full blog content
* This tool is meant for **personal, educational, or non-commercial use**
* If you plan to redistribute the generated content (e.g. in a newsletter), consider:

  * Crediting all original authors clearly
  * Summarizing only small portions of content
  * Reaching out to blog authors for permission, if unsure

---

## 🧠 Credits & Notes

* Summarization powered by local Ollama LLM (`gemma3:27b` by default)
* HTML rendering is clean, mobile-friendly, and modern
* Fully customizable

---
