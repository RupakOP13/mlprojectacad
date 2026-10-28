# 📱 SMS Spam Detector — SpamShield AI

An end-to-end **Machine Learning project** that detects SMS spam using NLP and 4 classical ML classifiers, with a beautiful Flask web application.

---

## 🚀 Features

- **4 ML Models** — Naive Bayes, Logistic Regression, SVM, Random Forest
- **Real-time Prediction** — Instant spam/ham classification via REST API
- **Beautiful Web UI** — Dark mode, animations, glassmorphism design
- **Analytics Dashboard** — Model comparison charts, confusion matrices, ROC curves
- **Feature Transparency** — Explains *why* a message was flagged
- **Jupyter Notebook** — Full EDA + model training walkthrough

---

## 📁 Project Structure

```
smsspamdetect/
├── app.py                  # Flask web application
├── train.py                # Model training script (run first!)
├── requirements.txt        # Python dependencies
├── data/
│   └── spam.csv            # Dataset (auto-downloaded by train.py)
├── models/
│   ├── best_model.pkl      # Best performing model
│   ├── naive_bayes.pkl
│   ├── logistic_regression.pkl
│   ├── svm.pkl
│   ├── random_forest.pkl
│   └── metadata.pkl        # Training metadata & metrics
├── src/
│   ├── preprocessing.py    # Text cleaning, tokenization, stemming
│   └── model.py            # Model training, evaluation, saving
├── templates/
│   ├── index.html          # Main detector page
│   ├── analytics.html      # Analytics dashboard
│   └── about.html          # About & documentation
├── static/
│   ├── css/style.css       # Premium dark theme CSS
│   └── js/
│       ├── main.js         # Detector page JavaScript
│       └── analytics.js    # Charts & analytics JavaScript
└── notebooks/
    └── sms_spam_eda.ipynb  # Jupyter notebook — EDA + training
```

---

## ⚙️ Setup & Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the Models

```bash
python train.py
```

This will:
- Download the SMS Spam Collection dataset automatically
- Preprocess and clean the text
- Train 4 ML classifiers
- Evaluate and compare them
- Save the best model to `models/`

### 3. Run the Web App

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 🤖 ML Pipeline

```
Raw SMS → Clean Text → Tokenize → Remove Stopwords → Stem
        → TF-IDF (10K features, bigrams) → ML Classifier → Spam/Ham + Probability
```

### Models Compared

| Model               | Description                           |
|---------------------|---------------------------------------|
| Naive Bayes         | Probabilistic, fast, great baseline  |
| Logistic Regression | Linear, interpretable, well-regularized |
| SVM (Linear)        | Max-margin, excellent for text       |
| Random Forest       | Ensemble of 200 trees, robust        |

---

## 📊 Dataset

- **Name**: UCI SMS Spam Collection
- **Size**: 5,574 messages (4,827 ham + 747 spam)
- **Source**: University of California Irvine ML Repository
- **Balance**: ~87% ham, ~13% spam

---

## 🌐 API Endpoints

| Endpoint        | Method | Description              |
|-----------------|--------|--------------------------|
| `/`             | GET    | Main detector page       |
| `/predict`      | POST   | Predict spam/ham         |
| `/api/stats`    | GET    | Model performance stats  |
| `/analytics`    | GET    | Analytics dashboard      |
| `/about`        | GET    | About & documentation    |

### Prediction API

**Request:**
```json
POST /predict
{ "message": "FREE prize winner! Call now!" }
```

**Response:**
```json
{
  "prediction": "SPAM",
  "is_spam": true,
  "spam_probability": 97.3,
  "ham_probability": 2.7,
  "confidence": 97.3,
  "features": {
    "length": 32,
    "word_count": 5,
    "has_url": false,
    "has_phone": false,
    "spam_keywords": 3,
    "capital_ratio": 15.6
  }
}
```

---

## 📓 Jupyter Notebook

For detailed EDA and step-by-step model analysis:

```bash
cd notebooks
jupyter notebook sms_spam_eda.ipynb
```

---

## 🛠️ Tech Stack

| Tool           | Purpose              |
|----------------|----------------------|
| Python 3.10+   | Core language        |
| scikit-learn   | ML algorithms        |
| NLTK           | NLP preprocessing    |
| pandas/NumPy   | Data handling        |
| Flask          | Web framework        |
| Chart.js       | Interactive charts   |
| Jupyter        | Notebook exploration |

---

## 📜 License

MIT License — Free to use and modify.
