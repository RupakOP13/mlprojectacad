"""
SMS Spam Detector - Data Preprocessing Module
Handles text cleaning, tokenization, and feature extraction
"""

import re
import string
import nltk
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Download required NLTK data
def download_nltk_data():
    resources = ['punkt', 'stopwords', 'punkt_tab']
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            print(f"Warning: Could not download {resource}: {e}")

download_nltk_data()

stemmer = PorterStemmer()

def get_stopwords():
    try:
        return set(stopwords.words('english'))
    except:
        return set()

STOP_WORDS = get_stopwords()

def clean_text(text):
    """Clean and normalize raw SMS text."""
    if not isinstance(text, str):
        text = str(text)
    
    # Lowercase
    text = text.lower()
    
    # Remove URLs (replace with token so model learns 'url' = spam signal)
    text = re.sub(r'http\S+|www\S+|https\S+', 'url', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', 'email', text)
    
    # Replace phone numbers (10+ digits or formatted patterns)
    text = re.sub(r'\b\d{10,}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b', 'phone', text)
    
    # Replace shortcode numbers (e.g. 5-digit premium-rate numbers like 80488, 88888)
    text = re.sub(r'\b\d{4,6}\b', 'shortcode', text)
    
    # Replace currency amounts (e.g. $500, PS1000, 1000 pounds)
    text = re.sub(r'(?:[$£€]\s*\d+(?:[,.]\d+)?|\d+(?:[,.]\d+)?\s*(?:dollars?|pounds?|euros?|gbp|usd))', 'money_amount', text, flags=re.I)
    
    # Replace remaining standalone numbers
    text = re.sub(r'\b\d+(?:\.\d+)?(?:p|%|k|m)?\b', 'num', text)
    
    # Normalize repeated characters (e.g. 'freeee' -> 'free', '!!!!' -> '!')
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    
    # Remove punctuation (but keep spaces)
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def tokenize_and_stem(text):
    """Tokenize and apply stemming to text."""
    try:
        tokens = word_tokenize(text)
    except:
        tokens = text.split()
    
    tokens = [
        stemmer.stem(token)
        for token in tokens
        if token not in STOP_WORDS and len(token) > 2
    ]
    return ' '.join(tokens)

def preprocess(text):
    """Full preprocessing pipeline."""
    cleaned = clean_text(text)
    stemmed = tokenize_and_stem(cleaned)
    return stemmed

# ---------------------------------------------------------------------------
# Comprehensive spam signal keyword groups
# Each group targets a distinct spam tactic recognized in academic literature
# ---------------------------------------------------------------------------

# 1. Urgency / Time-Pressure
URGENCY_WORDS = [
    'urgent', 'immediately', 'expires', 'expiring', 'deadline', 'act now',
    'don\'t delay', 'last chance', 'today only', 'limited time', 'hurry',
    'quick', 'fast', 'right now', 'don\'t wait', 'ending soon', 'final notice',
    'closing soon', 'responds immediately', 'reply now', 'asap'
]

# 2. Prize / Lottery / Gambling
PRIZE_WORDS = [
    'winner', 'won', 'win', 'winning', 'prize', 'jackpot', 'lottery', 'lotto',
    'raffle', 'draw', 'selected', 'chosen', 'lucky', 'luck', 'sweepstake',
    'grand prize', 'guaranteed prize', 'cash prize', 'free entry', 'competition',
    'congratulations', 'congrats', 'you have been selected'
]

# 3. Money / Financial Bait
MONEY_WORDS = [
    'free', 'cash', 'money', 'earn', 'income', 'salary', 'revenue',
    'investment', 'profit', 'bonus', 'reward', 'voucher', 'coupon', 'discount',
    'credit', 'loan', 'debt', 'mortgage', 'insurance', 'claim', 'compensation',
    'refund', 'payment', 'payout', 'transfer', 'cheque', 'check', 'bank',
    'financial', 'fund', 'grant', 'thousand', 'million', 'billion', 'pounds',
    'dollars', 'euros'
]

# 4. Action Imperatives / Call-to-Action
ACTION_WORDS = [
    'call', 'text', 'reply', 'click', 'visit', 'go to', 'send', 'subscribe',
    'sign up', 'register', 'download', 'install', 'apply', 'confirm', 'verify',
    'enter', 'submit', 'fill in', 'complete', 'respond', 'contact us'
]

# 5. Fake Authority / Official-sounding Cues
AUTHORITY_WORDS = [
    'bank', 'government', 'official', 'authorized', 'verified', 'legitimate',
    'legal', 'confidential', 'notification', 'alert', 'important message',
    'account', 'security', 'customer service', 'support team', 'helpdesk',
    'representative', 'agent', 'department', 'notice'
]

# 6. Subscription / Opt-out Traps
SUBSCRIPTION_WORDS = [
    'stop', 'opt out', 'unsubscribe', 'cancel', 'to stop', 'txt stop',
    'reply stop', 'per week', 'per month', 'per day', 'weekly', 'monthly',
    'subscription', 'service charge', 'premium rate'
]

# 7. Adult / Pharma / Illicit Content
ADULT_WORDS = [
    'adult', 'sex', 'xxx', 'hot', 'naked', 'girls', 'viagra', 'cialis',
    'enlargement', 'pharmacy', 'prescription', 'pills', 'drugs', 'weight loss',
    'diet', 'slim', 'fat', 'dating', 'singles', 'meet'
]

# 8. Phishing / Credential Harvesting
PHISHING_WORDS = [
    'username', 'password', 'pin', 'account number', 'sort code', 'ssn',
    'social security', 'date of birth', 'your details', 'personal information',
    'update your', 'verify your', 'confirm your', 'login', 'log in',
    'access', 'authenticate'
]


def extract_features(text):
    """Extract 35+ hand-crafted spam signal features from raw SMS text."""
    features = {}
    
    if not isinstance(text, str):
        text = str(text)
    
    text_lower = text.lower()
    words = text.split()
    
    # --- Basic structural features ---
    features['length'] = len(text)
    features['word_count'] = len(words)
    features['avg_word_length'] = sum(len(w) for w in words) / max(len(words), 1)
    
    # --- Character-level features ---
    features['num_digits'] = sum(c.isdigit() for c in text)
    features['num_uppercase'] = sum(c.isupper() for c in text)
    features['num_exclamation'] = text.count('!')
    features['num_question'] = text.count('?')
    features['num_dots'] = text.count('.')
    features['num_commas'] = text.count(',')
    features['num_colons'] = text.count(':')
    features['num_semicolons'] = text.count(';')
    features['num_asterisk'] = text.count('*')          # often used for emphasis in spam
    features['num_hash'] = text.count('#')              # hashtag / shortcode spam
    features['num_percent'] = text.count('%')           # discount/offer spam
    features['num_ampersand'] = text.count('&')         # often in promotional URLs
    features['capital_ratio'] = features['num_uppercase'] / max(len(text), 1)
    features['digit_ratio'] = features['num_digits'] / max(len(text), 1)
    features['punct_ratio'] = sum(c in string.punctuation for c in text) / max(len(text), 1)
    
    # --- Currency / money symbols ---
    features['num_currency'] = sum(c in '$£€' for c in text)
    features['has_currency'] = int(features['num_currency'] > 0)
    
    # --- ALL-CAPS words (a strong spam signal) ---
    caps_words = [w for w in words if w.isupper() and len(w) > 2]
    features['num_caps_words'] = len(caps_words)
    features['caps_word_ratio'] = len(caps_words) / max(len(words), 1)
    
    # --- Repeated characters (e.g., 'freeee!!!') ---
    features['has_repeated_chars'] = int(bool(re.search(r'(.)\1{2,}', text)))
    
    # --- Network / contact features ---
    features['has_url'] = int(bool(re.search(r'http|www|\.com|\.net|\.org|\.co\.uk|\.info', text, re.I)))
    features['has_phone'] = int(bool(re.search(r'\b\d{10,}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', text)))
    features['has_shortcode'] = int(bool(re.search(r'\b\d{4,6}\b', text)))
    features['has_email'] = int(bool(re.search(r'\S+@\S+\.\S+', text, re.I)))
    
    # --- Keyword group counters ---
    features['urgency_count']      = sum(kw in text_lower for kw in URGENCY_WORDS)
    features['prize_count']        = sum(kw in text_lower for kw in PRIZE_WORDS)
    features['money_count']        = sum(kw in text_lower for kw in MONEY_WORDS)
    features['action_count']       = sum(kw in text_lower for kw in ACTION_WORDS)
    features['authority_count']    = sum(kw in text_lower for kw in AUTHORITY_WORDS)
    features['subscription_count'] = sum(kw in text_lower for kw in SUBSCRIPTION_WORDS)
    features['adult_count']        = sum(kw in text_lower for kw in ADULT_WORDS)
    features['phishing_count']     = sum(kw in text_lower for kw in PHISHING_WORDS)
    
    # --- Total spam signal score (sum of all group hits) ---
    features['total_spam_signal_score'] = (
        features['urgency_count'] + features['prize_count'] +
        features['money_count'] + features['action_count'] +
        features['authority_count'] + features['subscription_count'] +
        features['adult_count'] + features['phishing_count']
    )
    
    # --- Backward-compatible combined keyword count ---
    all_spam_keywords = (
        URGENCY_WORDS + PRIZE_WORDS + MONEY_WORDS + ACTION_WORDS +
        AUTHORITY_WORDS + SUBSCRIPTION_WORDS + ADULT_WORDS + PHISHING_WORDS
    )
    features['spam_keyword_count'] = sum(kw in text_lower for kw in all_spam_keywords)
    
    return features

def load_and_preprocess_data(filepath):
    """Load the SMS spam dataset and preprocess it."""
    try:
        df = pd.read_csv(filepath, encoding='latin-1')
    except Exception as e:
        raise ValueError(f"Could not load data from {filepath}: {e}")
    
    # Handle different column naming conventions
    if 'v1' in df.columns and 'v2' in df.columns:
        df = df[['v1', 'v2']].copy()
        df.columns = ['label', 'message']
    elif 'Category' in df.columns and 'Message' in df.columns:
        df = df[['Category', 'Message']].copy()
        df.columns = ['label', 'message']
    elif 'label' in df.columns and 'message' in df.columns:
        df = df[['label', 'message']].copy()
    else:
        raise ValueError(f"Unexpected columns: {df.columns.tolist()}")
    
    # Drop NaN
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    
    # Encode labels
    df['label_num'] = df['label'].map({'ham': 0, 'spam': 1})
    df.dropna(subset=['label_num'], inplace=True)
    df['label_num'] = df['label_num'].astype(int)
    
    # Preprocess text
    print("Preprocessing text...")
    df['cleaned'] = df['message'].apply(preprocess)
    
    # Extract features
    print("Extracting features...")
    feature_df = df['message'].apply(lambda x: pd.Series(extract_features(x)))
    df = pd.concat([df.reset_index(drop=True), feature_df.reset_index(drop=True)], axis=1)
    
    print(f"Dataset loaded: {len(df)} samples | Spam: {df['label_num'].sum()} | Ham: {(df['label_num']==0).sum()}")
    return df

