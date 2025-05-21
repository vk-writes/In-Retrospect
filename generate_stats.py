import json
from datetime import datetime

def generate_full_html_report():
    with open("stats_data.json", "r", encoding="utf-8") as f:
        stats = json.load(f)

    # Build HTML content with all stats sections and link style2.css
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Stats Report</title>
<link rel="stylesheet" href="style2.css" />
</head>
<body>
  <h1>Stats Report</h1>

  <div class="stats-grid">
    <div class="stat-card">
      <h2>Summary</h2>
      <p><strong>Last Updated:</strong> {stats.get('last_updated', 'N/A')}</p>
      <p><strong>Article Count:</strong> {stats.get('article_count', 0)}</p>
      <p><strong>Total Words:</strong> {stats.get('total_words', 0)}</p>
      <p><strong>Average Words per Article:</strong> {stats.get('avg_words', 0)}</p>
      <p><strong>Longest Article:</strong> {stats.get('longest_article', 'N/A')}</p>
    </div>

    <div class="stat-card">
      <h2>Top Words</h2>
      <ul>
        {"".join(f"<li>{word}</li>" for word in stats.get('top_words', []))}
      </ul>
    </div>

    <div class="stat-card">
      <h2>Entity Counts (Top 10)</h2>
      <ul>
        {"".join(f"<li>{entity}: {count}</li>" for entity, count in stats.get('entity_counts', []))}
      </ul>
    </div>

    <div class="stat-card">
      <h2>Lexical Diversity per Article</h2>
      <ul>
        {"".join(f"<li>{article}: {diversity:.2f}</li>" for article, diversity in stats.get('lexical_diversities', {}).items())}
      </ul>
    </div>

    <div class="stat-card">
      <h2>Readability Scores</h2>
      <ul>
      {"".join(
          f"<li>{article}: Flesch Reading Ease {scores.get('flesch_reading_ease', 'N/A'):.2f}, FK Grade {scores.get('flesch_kincaid_grade', 'N/A'):.2f}</li>"
          for article, scores in stats.get('readabilities', {}).items()
      )}
      </ul>
    </div>

    <div class="stat-card">
      <h2>Sentiment Scores</h2>
      <ul>
      {"".join(
          f"<li>{article}: Polarity {scores.get('polarity', 'N/A'):.2f}, Subjectivity {scores.get('subjectivity', 'N/A'):.2f}</li>"
          for article, scores in stats.get('sentiments', {}).items()
      )}
      </ul>
    </div>

    <div class="stat-card">
      <h2>Sentence Stats</h2>
      <ul>
      {"".join(
          f"<li>{article}: Sentences {stats_['sentence_count']}, Avg Length {stats_['avg_sentence_length']:.2f}, Longest {stats_['longest_sentence_length']}</li>"
          for article, stats_ in stats.get('sentence_stats', {}).items()
      )}
      </ul>
    </div>

    <div class="stat-card">
      <h2>Keywords per Article</h2>
      {"".join(
          f"<div><strong>{article}</strong><ul>" + "".join(f"<li>{kw}</li>" for kw in kws) + "</ul></div>"
          for article, kws in stats.get('keywords', {}).items()
      )}
    </div>
  </div>

  <img src="wordcloud.png" alt="Word Cloud" style="max-width:100%; margin-top: 2rem; border-radius: 1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.1);" />

</body>
</html>
"""
    with open("stats.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    generate_full_html_report()
    print("stats.html generated with full details and styling.")
