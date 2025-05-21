import os
import re
import spacy
import json
from collections import Counter
from datetime import datetime

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Configuration
EXCLUDED_FILES = {
    'index.html', 'stats.html', 'about.html', 'contact.html', 
    'style.css', 'navbar.js', '404.html'
}
STOPWORDS = {
    'the', 'and', 'of', 'to', 'a', 'in', 'that', 'it', 'is', 'was',
    'for', 'with', 'on', 'as', 'at', 'by', 'this', 'be', 'are'
}


def analyze_articles():
    total_words = 0
    articles = []
    word_counter = Counter()
    pos_counters = {
        'NOUN': Counter(),
        'VERB': Counter(),
        'ADJ': Counter(),
        'ADV': Counter()
    }

    print("Scanning articles...")
    for filename in os.listdir('.'):
        if filename.endswith('.html') and filename not in EXCLUDED_FILES:
            print(f"  Processing {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                text = re.sub(r'<[^>]+>', ' ', f.read())
                doc = nlp(text.lower())
                total_words += len(doc)
                articles.append(filename)
                for token in doc:
                    if token.is_alpha and not token.is_stop:
                        word_counter[token.text] += 1
                        if token.pos_ in pos_counters:
                            pos_counters[token.pos_][token.text] += 1

    article_lengths = {name: os.path.getsize(name) for name in articles}
    longest_article = max(article_lengths, key=article_lengths.get) if articles else "None"

    stats = {
        'article_count': len(articles),
        'total_words': total_words,
        'avg_words': total_words // len(articles) if articles else 0,
        'top_words': [w for w, _ in word_counter.most_common(10)],
        'top_nouns': [w for w, _ in pos_counters['NOUN'].most_common(5)],
        'top_verbs': [w for w, _ in pos_counters['VERB'].most_common(5)],
        'top_adjectives': [w for w, _ in pos_counters['ADJ'].most_common(5)],
        'top_adverbs': [w for w, _ in pos_counters['ADV'].most_common(5)],
        'longest_article': longest_article.replace('.html', ''),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    }

    with open("stats_data.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    return stats


def generate_html(stats):
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Fun Stats</title>
    <link rel=\"stylesheet\" href=\"style.css\" />
    <script src=\"navbar.js\" defer></script>
    <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
</head>
<body>
    <h1>📊 Fun Stats</h1>
    <div class=\"stats-grid\">
        <div class=\"stat-card\">
            <h2>📚 Articles</h2>
            <p>Total: {stats['article_count']}</p>
            <p>Longest: {stats['longest_article']}</p>
        </div>
        <div class=\"stat-card\">
            <h2>📝 Words</h2>
            <p>Total: {stats['total_words']:,}</p>
            <p>Average: {stats['avg_words']:,}/article</p>
        </div>
        <div class=\"stat-card\">
            <h2>🔠 Top Words</h2>
            <ol>{''.join(f'<li>{word}</li>' for word in stats['top_words'])}</ol>
        </div>
        <div class=\"stat-card\">
            <h2>🏷️ Parts of Speech</h2>
            <p><strong>Nouns:</strong> {', '.join(stats['top_nouns'])}</p>
            <p><strong>Verbs:</strong> {', '.join(stats['top_verbs'])}</p>
            <p><strong>Adjectives:</strong> {', '.join(stats['top_adjectives'])}</p>
            <p><strong>Adverbs:</strong> {', '.join(stats['top_adverbs'])}</p>
        </div>
        <div class=\"stat-card\">
            <h2>⏰ Last Updated</h2>
            <p>{stats['last_updated']}</p>
        </div>
    </div>
    <canvas id=\"chart\" width=\"400\" height=\"200\"></canvas>
    <script>
        const chart = new Chart(document.getElementById('chart'), {
            type: 'bar',
            data: {
                labels: {json.dumps(stats['top_words'])},
                datasets: [{
                    label: 'Top Words',
                    data: {json.dumps([1]*len(stats['top_words']))},
                    backgroundColor: 'rgba(54, 162, 235, 0.7)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Top Words Chart' }
                }
            }
        });
    </script>
</body>
</html>
"""


if __name__ == '__main__':
    stats = analyze_articles()
    with open('stats.html', 'w', encoding='utf-8') as f:
        f.write(generate_html(stats))
    print("✅ Enhanced stats.html generated successfully!")
