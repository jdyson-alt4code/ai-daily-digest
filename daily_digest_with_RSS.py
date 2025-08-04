import os
import logging
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from dateutil import parser as date_parser
import markdown

# --- CONFIG ---
OLLAMA_MODEL = "gemma3:27b"
OLLAMA_URL = "http://localhost:11434"

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
THREE_DAYS_AGO = datetime.now(timezone.utc) - timedelta(days=3)

OUTPUT_BASE_DIR = "output"

# --- RSS Feeds: Core, HuggingFace, AI Companies ---
RSS_FEEDS = [
    # Core tools/models
    "https://github.com/comfyui/comfyui/releases.atom",
    "https://github.com/ollama/ollama/releases.atom",
    "https://github.com/facebookresearch/llama/releases.atom",
    "https://github.com/QwenLM/Qwen/releases.atom",
    "https://github.com/QwenLM/Qwen-VL/releases.atom",
    "https://github.com/QwenLM/Qwen1.5/releases.atom",
    "https://github.com/mistralai/mistral-src/releases.atom",
    "https://github.com/huggingface/transformers/releases.atom",
    "https://github.com/huggingface/datasets/releases.atom",
    "https://github.com/Stability-AI/stablediffusion/releases.atom",
    "https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases.atom",
    "https://github.com/ortis-ai/ToolKit/releases.atom",
    "https://github.com/midudev/llama-chat/releases.atom",
    "https://github.com/cocktailpeanut/dalai/releases.atom",

    # Hugging Face ecosystem
    "https://github.com/huggingface/accelerate/releases.atom",
    "https://github.com/huggingface/huggingface_hub/releases.atom",
    "https://github.com/huggingface/peft/releases.atom",
    "https://github.com/huggingface/text-generation-inference/releases.atom",
    "https://github.com/huggingface/optimum/releases.atom",
    "https://github.com/huggingface/evaluate/releases.atom",
    "https://github.com/huggingface/autotrain-advanced/releases.atom",

    # AI model companies
    "https://github.com/databrickslabs/dolly/releases.atom",
    "https://github.com/databricks/dbrx/releases.atom",
    "https://github.com/THUDM/ChatGLM3/releases.atom",
    "https://github.com/ZhipuAI/releases.atom",
    "https://github.com/mindsdb/mindsdb/releases.atom",
    "https://github.com/SeldonIO/seldon-core/releases.atom",
    "https://github.com/SeldonIO/alibi-detect/releases.atom",
    "https://github.com/Mintplex-Labs/anything-llm/releases.atom",
    "https://github.com/e2b-dev/awesome-ai-agents/releases.atom",
    "https://github.com/Shubhamsaboo/awesome-llm-apps/releases.atom",

    # AI Blogs
    "https://openai.com/blog/rss.xml",
    "https://deepmind.com/blog/feed/basic",
    "https://github.blog/ai-and-ml/feed",
    "https://blog.clarifai.com/feed",
    "https://blog.datarobot.com/blog/feed",
    "https://iris.ai/feed",
    "https://www.singularityweblog.com/blog/feed"
]

COMFYUI_SITE = "https://comfyanonymous.github.io/ComfyUI_examples/"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def fetch_summary_from_link(url):
    try:
        r = requests.get(url, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = soup.find_all("p")
        return " ".join(p.get_text() for p in paragraphs[:3]).strip()
    except Exception:
        return ""

def fetch_rss_updates():
    entries = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                pub_str = entry.get("published", "") or entry.get("updated", "")
                if not pub_str:
                    continue
                try:
                    pub_dt = date_parser.parse(pub_str)
                    if pub_dt.tzinfo is None:
                        pub_dt = pub_dt.replace(tzinfo=timezone.utc)
                except Exception:
                    continue
                if pub_dt < THREE_DAYS_AGO:
                    continue

                summary = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text().strip()
                if not summary and entry.get("link"):
                    summary = fetch_summary_from_link(entry.get("link"))
                if not summary:
                    continue

                entries.append({
                    "title": entry.get("title", "No title").strip(),
                    "url": entry.get("link", ""),
                    "summary": summary,
                    "published": pub_dt.strftime("%Y-%m-%d"),
                    "source": feed.feed.get("title", "Unknown Source").strip()
                })
        except Exception as e:
            logging.warning(f"Error with feed {feed_url}: {e}")
    return sorted(entries, key=lambda x: x["published"], reverse=True)

def check_comfyui_examples_update():
    updates = []
    try:
        r = requests.get(COMFYUI_SITE)
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.find_all("a"):
            href = link.get("href", "")
            if href and (href.endswith(".json") or "workflow" in href.lower()):
                updates.append({"title": link.text.strip() or href, "url": COMFYUI_SITE + href})
    except Exception as e:
        updates.append({"title": "Error fetching ComfyUI examples", "url": str(e)})
    return updates

def format_digest(rss_entries, comfyui_updates):
    lines = [f"# 🤖 AI Digest — {TODAY}", ""]
    lines.append("## 📡 Recent AI Updates (last 3 days)\n")

    grouped = {}
    for e in rss_entries:
        grouped.setdefault(e["source"], []).append(e)

    for source, items in grouped.items():
        lines.append(f"### 🏷 {source}")
        for item in items:
            lines.append(f"**{item['title']}**  \n[{item['url']}]({item['url']})  \n📅 {item['published']}")
            lines.append(f"> {item['summary'][:400]}...\n")
    lines.append("\n## 🧩 New ComfyUI Workflows")
    if comfyui_updates:
        for u in comfyui_updates:
            lines.append(f"- 🔗 [{u['title']}]({u['url']})")
    else:
        lines.append("_None this week._")

    lines.append(f"\n---\n_Total feeds: {len(RSS_FEEDS)} | Entries: {len(rss_entries)}_")
    return "\n".join(lines)

def ollama_generate(prompt):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )
    response.raise_for_status()
    return response.json()["response"]

def summarize_with_ollama(raw_digest):
    prompt = (
        f"You are an expert AI newsletter writer.\n"
        f"Today is {TODAY}. Using the following AI tool/model updates from the last 3 days, write a structured, well-written blog post.\n\n"
        f"Guidelines:\n"
        f"- Start with a short intro about trends this week in AI.\n"
        f"- Break down updates by tool or company.\n"
        f"- Explain *why* each update is important.\n"
        f"- Link to the source.\n"
        f"- Close with a reflection or insight.\n\n"
        f"Data:\n{raw_digest}\n\n"
        f"Now write the blog post."
    )
    return ollama_generate(prompt)

def generate_tweet_from_digest(markdown_text):
    prompt = (
        "Write a compelling tweet (≤280 characters) summarizing this daily AI digest. "
        "Highlight 1–2 key updates developers would care about. No hashtags or emojis. Write it like a real tweet.\n\n"
        + markdown_text
    )
    return ollama_generate(prompt)

def save_html_from_markdown(markdown_text, output_dir):
    html_content = markdown.markdown(markdown_text, extensions=["fenced_code", "tables"])
    styled_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Daily Digest — {TODAY}</title>
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            margin: 2rem auto;
            max-width: 800px;
            padding: 1rem;
            background-color: #f9f9f9;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2b2b2b;
        }}
        a {{
            color: #007acc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        blockquote {{
            background-color: #f0f0f0;
            border-left: 4px solid #ccc;
            margin: 1em 0;
            padding: 0.5em 1em;
            font-style: italic;
        }}
        code {{
            background-color: #eee;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        pre {{
            background: #272822;
            color: #f8f8f2;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
    """.strip()

    html_path = os.path.join(output_dir, "digest.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(styled_html)

def main():
    logging.info("Fetching RSS updates...")
    rss = fetch_rss_updates()
    logging.info("Checking ComfyUI examples...")
    comfy = check_comfyui_examples_update()
    logging.info("Formatting digest...")
    raw_digest = format_digest(rss, comfy)

    logging.info("Generating article with Ollama...")
    markdown_summary = summarize_with_ollama(raw_digest)

    output_dir = os.path.join(OUTPUT_BASE_DIR, TODAY)
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "digest.md"), "w", encoding="utf-8") as f:
        f.write(markdown_summary)

    save_html_from_markdown(markdown_summary, output_dir)

    logging.info("Generating tweet from article...")
    tweet = generate_tweet_from_digest(markdown_summary)
    with open(os.path.join(output_dir, "digest_tweet.txt"), "w", encoding="utf-8") as f:
        f.write(tweet.strip())

    logging.info(f"✅ Saved to {output_dir}")
    print(f"\n📣 Suggested Tweet:\n{tweet.strip()}")

if __name__ == "__main__":
    main()
