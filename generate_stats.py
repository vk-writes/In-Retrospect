import os
import re
import spacy
import json
from collections import Counter, defaultdict
from datetime import datetime
from textstat import flesch_reading_ease, flesch_kincaid_grade
from textblob import TextBlob
from wordcloud import WordCloud
import yake

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

EXCLUDED_FILES = {
    'index.html', 'stats.html', 'about.html', 'contact.html',
    'style.css', 'style2.css', 'navbar.js', '404.html'
}
STOPWORDS = {
    'the', 'and', 'of', 'to', 'a', 'in', 'that', 'it', 'is', 'was',
    'for', 'with', 'on', 'as', 'at', 'by', 'this', 'be', 'are'
}

def analyze_articles():
    total_words = 0
    articles = []
    word_counter = Counter()
    pos_counters = defaultdict(Counter)
    lexical_diversities = {}
    sentence_stats = {}
    readabilities = {}
    sentiments = {}
    entity_counter = Counter()
    keywords = {}
    all_text_for_wordcloud = []

    kw_extractor = yake.KeywordExtractor(
        lan="en", n=3, dedupLim=0.9, top=10, stopwords=STOPWORDS
    )

    for filename in os.listdir('.'):
        if filename.endswith('.html') and filename not in EXCLUDED_FILES:
            with open(filename, 'r', encoding='utf-8') as f:
                raw_html = f.read()
                text = re.sub(r'<[^>]+>', ' ', raw_html)
                doc = nlp(text.lower())

                articles.append(filename)
                total_words += len([t for t in doc if t.is_alpha])

                # Word counts and POS
                for token in doc:
                    if token.is_alpha and not token.is_stop:
                        word_counter[token.text] += 1
                        pos_counters[token.pos_][token.text] += 1

                # Lexical diversity
                words = [t.text for t in doc if t.is_alpha]
                lexical_diversities[filename] = len(set(words)) / len(words) if words else 0

                # Sentence stats
                doc_full = nlp(text)
                lengths = [len(sent) for sent in doc_full.sents]
                avg_sentence_length = sum(lengths) / len(lengths) if lengths else 0
                longest_sentence_length = max(lengths) if lengths else 0
                sentence_stats[filename] = {
                    'avg_sentence_length': avg_sentence_length,
                    'longest_sentence_length': longest_sentence_length,
                    'sentence_count': len(lengths)
                }

                # Readability
                flesch_score = flesch_reading_ease(text)
                fk_grade = flesch_kincaid_grade(text)
                readabilities[filename] = {
                    'flesch_reading_ease': flesch_score,
                    'flesch_kincaid_grade': fk_grade
                }

                # Sentiment
                blob = TextBlob(text)
                sentiments[filename] = {
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                }

                # Named Entities
                doc_ner = nlp(text)
                for ent in doc_ner.ents:
                    entity_counter[ent.label_] += 1

                # Keyword extraction
                extracted_keywords = kw_extractor.extract_keywords(text)
                keywords[filename] = [kw for kw, _ in extracted_keywords]

                all_text_for_wordcloud.append(text)

    article_lengths = {name: os.path.getsize(name) for name in articles}
    longest_article = max(article_lengths, key=article_lengths.get) if articles else "None"

    # Generate word cloud image
    combined_text = " ".join(all_text_for_wordcloud)
    wc = WordCloud(width=800, height=400, background_color='white', stopwords=STOPWORDS).generate(combined_text)
    wc.to_file("wordcloud.png")

    stats = {
        'article_count': len(articles),
        'total_words': total_words,
        'avg_words': total_words // len(articles) if articles else 0,
        'top_words': [w for w, _ in word_counter.most_common(10)],
        'longest_article': longest_article.replace('.html', ''),
        'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
        'pos_summary': {
            pos: [w for w, _ in words.most_common(5)]
            for pos, words in sorted(pos_counters.items())
        },
        'lexical_diversities': lexical_diversities,
        'sentence_stats': sentence_stats,
        'readabilities': readabilities,
        'sentiments': sentiments,
        'entity_counts': entity_counter.most_common(10),
        'keywords': keywords
    }

    with open("stats_data.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    return stats

def generate_full_html_report():
    stats = analyze_articles()

    html = f"""
<!DOCTYPE html>
<link rel="stylesheet" href="style2.css" />
<script src="navbar.js" defer></script>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Stats Report</title>
  <link rel="stylesheet" href="style2.css" />
</head>
<button id="darkModeToggle" class="dark-toggle">Toggle Dark Mode</button>
<body>
  <h1>Stats Report</h1>

  <div class="stats-grid">
    <div class="stat-card">
      <h2>General Stats</h2>
      <p><strong>Last Updated:</strong> {stats['last_updated']}</p>
      <p><strong>Article Count:</strong> {stats['article_count']}</p>
      <p><strong>Total Words:</strong> {stats['total_words']}</p>
      <p><strong>Average Words per Article:</strong> {stats['avg_words']}</p>
      <p><strong>Longest Article:</strong> {stats['longest_article']}</p>
    </div>

    <div class="stat-card">
      <h2>Top Words</h2>
      <ul>
        {''.join(f"<li>{word}</li>" for word in stats['top_words'])}
      </ul>
    </div>

    <div class="stat-card">
      <h2>Entity Counts (Top 10)</h2>
      <ul>
        {''.join(f"<li>{entity}: {count}</li>" for entity, count in stats['entity_counts'])}
      </ul>
    </div>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <h2>Lexical Diversities</h2>
      <ul>
        {''.join(f"<li>{file}: {diversity:.2f}</li>" for file, diversity in stats['lexical_diversities'].items())}
      </ul>
    </div>

    <div class="stat-card">
      <h2>Sentence Stats</h2>
      <ul>
        {''.join(
          f"<li>{file}: Avg Len: {vals['avg_sentence_length']:.1f}, Longest: {vals['longest_sentence_length']}, Count: {vals['sentence_count']}</li>" 
          for file, vals in stats['sentence_stats'].items())}
      </ul>
    </div>

    <div class="stat-card">
      <h2>Readability Scores</h2>
      <ul>
        {''.join(
          f"<li>{file}: Flesch Ease: {vals['flesch_reading_ease']:.1f}, Flesch-Kincaid Grade: {vals['flesch_kincaid_grade']:.1f}</li>"
          for file, vals in stats['readabilities'].items())}
      </ul>
    </div>
  </div>

  <div class="stats-grid">
    <div class="stat-card" style="grid-column: span 2;">
      <h2>Sentiments</h2>
      <ul>
        {''.join(
          f"<li>{file}: Polarity: {vals['polarity']:.2f}, Subjectivity: {vals['subjectivity']:.2f}</li>"
          for file, vals in stats['sentiments'].items())}
      </ul>
    </div>
  </div>

  <div class="stat-section">
    <h2>Keywords Extracted</h2>
    {''.join(
      f"<h3>{file}</h3><ul>{''.join(f'<li>{kw}</li>' for kw in kws)}</ul>"
      for file, kws in stats['keywords'].items())}
  </div>

  <img src="wordcloud.png" alt="Word Cloud" style="max-width:100%; border-radius: 1rem; margin-top: 2rem;" />
</body>
</html>
    """

    with open("stats.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    generate_full_html_report()
