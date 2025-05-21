import os
import re
import spacy
import json
from collections import Counter, defaultdict
from datetime import datetime
from textstat import flesch_reading_ease, flesch_kincaid_grade
from textblob import TextBlob
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Configuration
EXCLUDED_FILES = {
    'index.html', 'stats.html', 'about.html', 'contact.html',
    'style.css', 'style2.css', 'navbar.js', '404.html'
}
STOPWORDS = {
    'the', 'and', 'of', 'to', 'a', 'in', 'that', 'it', 'is', 'was',
    'for', 'with', 'on', 'as', 'at', 'by', 'this', 'be', 'are'
}

POS_FULL_NAMES = {
    "ADJ": "Adjectives", "ADP": "Adpositions", "ADV": "Adverbs",
    "AUX": "Auxiliary Verbs", "CCONJ": "Coordinating Conjunctions", "DET": "Determiners",
    "INTJ": "Interjections", "NOUN": "Nouns", "NUM": "Numerals", "PART": "Particles",
    "PRON": "Pronouns", "PROPN": "Proper Nouns", "PUNCT": "Punctuation",
    "SCONJ": "Subordinating Conjunctions", "SYM": "Symbols", "VERB": "Verbs",
    "X": "Other", "SPACE": "Spaces"
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
    all_text_for_wordcloud = []
    article_text_map = {}

    print("Scanning articles...")
    for filename in os.listdir('.'):
        if filename.endswith('.html') and filename not in EXCLUDED_FILES:
            print(f"  Processing {filename}")
            with open(filename, 'r', encoding='utf-8') as f:
                raw_html = f.read()
                text = re.sub(r'<[^>]+>', ' ', raw_html)
                text_lower = text.lower()
                doc = nlp(text_lower)

                articles.append(filename)
                total_words += len([t for t in doc if t.is_alpha])

                for token in doc:
                    if token.is_alpha and not token.is_stop:
                        word_counter[token.text] += 1
                        pos_counters[token.pos_][token.text] += 1

                words = [t.text for t in doc if t.is_alpha]
                lexical_diversities[filename] = len(set(words)) / len(words) if words else 0

                doc_full = nlp(text)
                lengths = [len(sent) for sent in doc_full.sents]
                sentence_stats[filename] = {
                    'avg_sentence_length': sum(lengths) / len(lengths) if lengths else 0,
                    'longest_sentence_length': max(lengths) if lengths else 0,
                    'sentence_count': len(lengths)
                }

                readabilities[filename] = {
                    'flesch_reading_ease': flesch_reading_ease(text),
                    'flesch_kincaid_grade': flesch_kincaid_grade(text)
                }

                blob = TextBlob(text)
                sentiments[filename] = {
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                }

                for ent in doc.ents:
                    entity_counter[ent.label_] += 1

                article_text_map[filename] = text
                all_text_for_wordcloud.append(text)

    # TF-IDF keyword extraction
    tfidf_vectorizer = TfidfVectorizer(stop_words=list(STOPWORDS), max_features=1000)
    filenames = list(article_text_map.keys())
    texts_list = list(article_text_map.values())
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts_list)
    feature_names = tfidf_vectorizer.get_feature_names_out()
    keywords = {}

    for i, filename in enumerate(filenames):
        row = tfidf_matrix[i].toarray()[0]
        top_indices = row.argsort()[::-1][:10]
        top_words = [feature_names[i] for i in top_indices if row[i] > 0]
        keywords[filename] = top_words

    article_lengths = {name: os.path.getsize(name) for name in articles}
    longest_article = max(article_lengths, key=article_lengths.get) if articles else "None"

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


def generate_html(stats):
    def ul(items): 
        return "<ul>" + "".join(f"<li>{k}: {v:.3f}</li>" for k, v in items.items()) + "</ul>"

    pos_html = "".join(
        f"<p><strong>{POS_FULL_NAMES.get(pos, pos)}:</strong> {', '.join(words)}</p>"
        for pos, words in stats['pos_summary'].items()
    )
    lex_html = ul(stats['lexical_diversities'])
    sent_html = "".join(
        f"<p><strong>{k}:</strong> Avg: {v['avg_sentence_length']:.1f}, Longest: {v['longest_sentence_length']}, Count: {v['sentence_count']}</p>"
        for k, v in stats['sentence_stats'].items()
    )
    read_html = "".join(
        f"<p><strong>{k}:</strong> Flesch: {v['flesch_reading_ease']:.1f}, Grade: {v['flesch_kincaid_grade']:.1f}</p>"
        for k, v in stats['readabilities'].items()
    )
    sentim_html = "".join(
        f"<p><strong>{k}:</strong> Polarity: {v['polarity']:.2f}, Subjectivity: {v['subjectivity']:.2f}</p>"
        for k, v in stats['sentiments'].items()
    )
    entity_html = ul(dict(stats['entity_counts']))
    keywords_html = "".join(
        f"<p><strong>{k}:</strong> {', '.join(v)}</p>" for k, v in stats['keywords'].items()
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Fun Stats</title>
  <link rel="stylesheet" href="style2.css" />
  <script src="navbar.js" defer></script>
</head>
<body>
  <h1>📊 Fun Stats</h1>
  <div class="stats-grid">
    <section class="stats-section stat-card"><h2>📚 Articles</h2><p>Total: {stats['article_count']}</p><p>Longest: {stats['longest_article']}</p></section>
    <section class="stats-section stat-card"><h2>📝 Words</h2><p>Total: {stats['total_words']}</p><p>Average: {stats['avg_words']}/article</p></section>
    <section class="stats-section stat-card"><h2>🔠 Top Words</h2><ol>{"".join(f"<li>{w}</li>" for w in stats['top_words'])}</ol></section>
    <section class="stats-section stat-card"><h2>🏷️ Parts of Speech</h2>{pos_html}</section>
    <section class="stats-section stat-card"><h2>🧠 Lexical Diversity</h2>{lex_html}</section>
    <section class="stats-section stat-card"><h2>✍️ Sentence Stats</h2>{sent_html}</section>
    <section class="stats-section stat-card"><h2>📖 Readability</h2>{read_html}</section>
    <section class="stats-section stat-card"><h2>🙂 Sentiment</h2>{sentim_html}</section>
    <section class="stats-section stat-card"><h2>🏷️ Named Entities</h2>{entity_html}</section>
    <section class="stats-section stat-card"><h2>🔑 Keywords</h2>{keywords_html}</section>
    <section class="stats-section stat-card"><h2>🌈 Word Cloud</h2><img src="wordcloud.png" alt="Word Cloud" /></section>
  </div>
</body>
</html>"""
    return html



if __name__ == '__main__':
    stats = analyze_articles()
    with open('stats.html', 'w', encoding='utf-8') as f:
        f.write(generate_html(stats))
    print("✅ stats.html and wordcloud.png generated successfully!")
