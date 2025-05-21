import os
import re
from collections import Counter
from datetime import datetime

# ---- IGNORE THESE FILES ----
EXCLUDED_FILES = {"index.html", "stats.html", "about.html", "contact.html"}  # Add others as needed

def analyze_articles():
    word_counts = Counter()
    total_words = 0
    articles = []

    # Scan all HTML files in the root directory
    for file in os.listdir("."):
        if file.endswith(".html") and file not in EXCLUDED_FILES:
            with open(file, "r", encoding="utf-8") as f:
                text = re.sub(r"<[^>]+>", " ", f.read())  # Remove HTML tags
                words = re.findall(r"\b\w+\b", text.lower())
                word_counts.update(words)
                total_words += len(words)
                articles.append(file)

    # Get top words (excluding common stopwords)
    stopwords = {"the", "and", "of", "to", "in", "a", "is", "that", "it", "for", "you", "with", "as", "on", "was"}
    top_words = [word for word, count in word_counts.most_common(50) if word not in stopwords][:10]

    return {
        "article_count": len(articles),
        "total_words": total_words,
        "top_words": top_words,
        "longest_article": max(articles, key=lambda x: os.path.getsize(x)) if articles else "None",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

# ---- GENERATE HTML ----
stats = analyze_articles()

html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Fun Stats</title>
    <link rel="stylesheet" href="style.css" />
    <script src="navbar.js" defer></script>
</head>
<body>
    <h1>📊 Fun Stats</h1>
    <div class="stats-grid">
        <div class="stat-card">
            <h2>📚 Articles</h2>
            <p>Total: {stats["article_count"]}</p>
            <p>Longest: {stats["longest_article"].replace(".html", "")}</p>
        </div>
        <div class="stat-card">
            <h2>📝 Words</h2>
            <p>Total: {stats["total_words"]:,}</p>
            <p>Avg/article: {stats["total_words"] // stats["article_count"] if stats["article_count"] else 0:,}</p>
        </div>
        <div class="stat-card">
            <h2>🔠 Top Words</h2>
            <ol>
                {"".join(f"<li>{word}</li>" for word in stats["top_words"])}
            </ol>
        </div>
        <div class="stat-card">
            <h2>⏰ Last Updated</h2>
            <p>{stats["last_updated"]} (UTC)</p>
        </div>
    </div>
</body>
</html>
"""

with open("stats.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Stats page generated!")
