from flask import Flask, request, jsonify, render_template
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime, timedelta

# Download VADER only once
nltk.download('vader_lexicon')

app = Flask(__name__)

API_KEY = "ef0affc9a61f437d8ec0c1c4a3b04a9d"
# -----------------------------------------------------------------------------------------

# ✅ Home page
@app.route('/')
def home():
    return render_template("home.html")

# ✅ Analyzer UI page
@app.route('/analyze')
def analyzer():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/premium')
def premium():
    return render_template("premium.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

# -----------------------------------------------------------------------------------------

#  Backend API for sentiment analysis
@app.route('/analyze/result')
def analyze_sentiment():
    company = request.args.get('company')
    days = int(request.args.get('days', 1))

    if not company:
        return jsonify({"error": "Missing 'company' parameter"}), 400

    # Fetch news
    from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    url = f"https://newsapi.org/v2/everything?q={company}&from={from_date}&sortBy=publishedAt&apiKey={API_KEY}&pageSize=10"
    response = requests.get(url)
    data = response.json()

    if data.get("status") != "ok":
        return jsonify({"error": "News API issue"}), 500

    # Analyze with VADER
    analyzer = SentimentIntensityAnalyzer()
    results = []

    for article in data.get("articles", []):
        title = article['title']
        link = article['url']
        score = analyzer.polarity_scores(title)['compound']
        sentiment = (
            "Positive" if score > 0.05 else
            "Negative" if score < -0.05 else
            "Neutral"
        )
        results.append({
            "headline": title,
            "link": link,
            "score": round(score, 2),
            "sentiment": sentiment
        })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

