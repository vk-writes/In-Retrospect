import os
import re
from collections import Counter
from datetime import datetime

# Configuration - Edit these if needed
EXCLUDED_FILES = {
    'index.html', 'stats.html', 'about.html', 'contact.html', 
    'style.css', 'navbar.js', '404.html'  # Add any other files to ignore
}
STOPWORDS = {
    'the', 'and', 'of', 'to', 'a', 'in', 'that', 'it', 'is', 'was',
    'for', 'with', 'on', 'as', 'at', 'by', 'this', 'be', 'are'
}

def analyze_articles():
    word_counts = Counter()
    total_words = 0
    articles = []
    
    print("Scanning articles...")
    for filename in os.listdir('.'):
        if filename.endswith('.html') and filename not in EXCLUDED_FILES:
            print(f"  Processing {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                text = re.sub(r'<[^>]+>', ' ', f.read())  # Remove HTML tags
                words = re.findall(r'\b[a-z]+\b', text.lower())  # Only alphabetic words
                word_counts.update(words)
                total_words += len(words)
                articles.append(filename)
    
    # Calculate stats
    top_words = [
        word for word, count in word_counts.most_common(30) 
        if word not in STOPWORDS and len(word) > 3
    ][:10]
    
    article_lengths = {name: os.path.getsize(name) for name in articles}
    longest_article = max(article_lengths, key=article_lengths.get) if articles else "None"
    
    return {
        'article_count': len(articles),
        'total_words': total_words,
        'avg_words': total_words // len(articles) if articles else 0,
        'top_words': top_words,
        'longest_article': longest_article.replace('.html', ''),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    }

def generate_html(stats):
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Fun Stats</title>
    <link rel="stylesheet" href="style.css" />
    <script src="navbar.js" defer></script>
</head>
<body>
    <h1>📊 Fun Stats</h1>
    <div class="stats-grid">
        <!-- Article Stats -->
        <div class="stat-card">
            <h2>📚 Articles</h2>
            <p>Total: {stats['article_count']}</p>
            <p>Longest: {stats['longest_article']}</p>
        </div>
        
        <!-- Word Stats -->
        <div class="stat-card">
            <h2>📝 Words</h2>
            <p>Total: {stats['total_words']:,}</p>
            <p>Average: {stats['avg_words']:,}/article</p>
        </div>
        
        <!-- Top Words -->
        <div class="stat-card">
            <h2>🔠 Top Words</h2>
            <ol>
                {"".join(f"<li>{word.title()}</li>" for word in stats['top_words'])}
            </ol>
        </div>
        
        <!-- Meta -->
        <div class="stat-card">
            <h2>⏰ Last Updated</h2>
            <p>{stats['last_updated']}</p>
            <p><small>(Updates daily)</small></p>
        </div>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    stats = analyze_articles()
    with open('stats.html', 'w', encoding='utf-8') as f:
        f.write(generate_html(stats))
    print("✅ stats.html generated successfully!")
