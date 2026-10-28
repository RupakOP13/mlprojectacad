# -*- coding: utf-8 -*-
"""
SMS Spam Detector - Training Script
Run this script to download data and train the models
"""

import os
import sys
import urllib.request

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.preprocessing import load_and_preprocess_data
from src.model import train_all_models

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'spam.csv')

# UCI SMS Spam Collection Dataset URL
DATASET_URL = "https://raw.githubusercontent.com/justmarkham/DAT8/master/data/sms.tsv"

def download_dataset():
    """Download or create the SMS spam dataset."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    if os.path.exists(DATA_FILE):
        print(f"[OK] Dataset already exists at {DATA_FILE}")
        return DATA_FILE
    
    print("[INFO] Downloading SMS Spam dataset...")
    
    # Try multiple sources
    sources = [
        ("https://raw.githubusercontent.com/mohitgupta-omg/Kaggle-SMS-Spam-Collection-Dataset-/master/spam.csv", "csv"),
        ("https://raw.githubusercontent.com/prasertcbs/basic-dataset/master/spam.csv", "csv"),
    ]
    
    for url, fmt in sources:
        try:
            print(f"   Trying: {url[:60]}...")
            urllib.request.urlretrieve(url, DATA_FILE)
            print("[OK] Downloaded successfully!")
            return DATA_FILE
        except Exception as e:
            print(f"   Failed: {e}")
    
    # Create a sample dataset as fallback
    print("[WARN] Could not download. Creating sample dataset...")
    create_sample_dataset(DATA_FILE)
    return DATA_FILE


def create_sample_dataset(filepath):
    """Create a comprehensive sample SMS spam dataset."""
    import pandas as pd
    
    spam_messages = [
        "WINNER!! As a valued network customer you have been selected to receive a ?900 prize reward!",
        "Had your mobile 11 months or more? U R entitled to Update to the latest colour mobiles with camera for Free!",
        "SIX chances to win CASH! From 100 to 20,000 pounds txt> CSH11 and send to 87575.",
        "URGENT! Your Mobile number has been awarded with a ?2,000 Bonus Caller Prize on 02/09/03!",
        "You have 1 new message. Call 0207-083-6089",
        "FREE entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005.",
        "Nah I don't think he goes to usf, he lives around here though",
        "Even my brother is not like to speak with me. They treat me like aid",
        "As per your request 'Melle Melle (Oru Minnaminunginte Nurungu Vettam)' has been set as your callertune",
        "WINNER! You've been selected for a FREE vacation to Bahamas! Call now: 0800-WINNER",
        "Congratulations! You have won a 1 week FREE membership in our ?100,000 Prize Jackpot!",
        "You've been CHOSEN to receive an exclusive cash prize of $5000. Reply YES to claim!",
        "FREE ringtone! Reply WIN to get your Nokia ringtone. T&C apply.",
        "URGENT Your account will be SUSPENDED! Update now: www.fakebank.com/verify",
        "You are a WINNER of the UK National Lottery. Send details to claim your ?1,000,000 prize",
        "Get a FREE iPhone 15! Limited offer. Text IPHONE to 80000 now!",
        "Your loan has been approved! Get £5000 now. Call 0800-LOANS",
        "You owe £300 in unpaid parking fines. Pay at: fake-site.com",
        "Win £250 Amazon gift card! Text AMAZON to 67890. No purchase needed!",
        "HOT DEALS! Get 90% OFF on all brands. Click here: spam-site.com",
        "Claim your FREE trial! No credit card needed. Call 0800-FREE-NOW",
        "You are selected for a special cash bonus of $2000. Reply BONUS to claim",
        "Congratulations!!! 3 free months subscription. Call now 0800-123-456",
        "Your prize is waiting! Call 0207-123-4567 immediately. Don't miss out!",
        "FINAL NOTICE: Your SIM card will be deactivated. Call 0800-SIM-HELP now",
        "Secret admirer has sent you a gift. Click to reveal: gift-site.com",
        "Make $500/day working from home! Guaranteed! Call 800-WORK-NOW",
        "You have been pre-approved for a credit card with $10,000 limit!",
        "ALERT: Suspicious activity on your account. Verify at: secure-fake.com",
        "Exclusive offer for you! Buy now pay later. No credit check required.",
    ]
    
    ham_messages = [
        "I'm gonna be home soon and i don't want to talk about this stuff anymore tonight",
        "Ok lar... Joking wif u oni...",
        "Even my brother is not like to speak with me.",
        "I HAVE A DATE ON SUNDAY WITH WILL!!",
        "As per your request 'Melle Melle' has been set as your callertune",
        "The guy did some bitching but I acted like i'd be interested in buying something",
        "I'm getting married next Sunday and I wanted you to be there.",
        "Come on, let's watch the Champions League final together",
        "Shall I call you now? Are you free?",
        "I don't understand how to complete this assignment. Can you help me?",
        "Hey, what time is the meeting tomorrow?",
        "Just finished my workout. Feeling great!",
        "Can you pick up some milk on your way home?",
        "Happy birthday! Hope you have a wonderful day.",
        "The movie was amazing! We should watch it together.",
        "Sorry, I'm running late. Be there in 10 minutes.",
        "Did you see the game last night? What a finish!",
        "I'll be in the office by 9 AM tomorrow.",
        "Thanks for helping me with the project. Really appreciate it!",
        "Let's meet for coffee this weekend. How does Saturday sound?",
        "The kids are doing great in school. Their grades improved a lot.",
        "I forgot my charger at home. Can I borrow yours?",
        "The weather is beautiful today. Perfect for a walk in the park.",
        "Just saw your email. I'll get back to you shortly.",
        "Happy New Year! Wishing you all the best in the coming year.",
        "The package you ordered has been shipped. Expected delivery: Monday.",
        "Don't forget about mom's birthday dinner on Friday.",
        "I'm so tired. Can we reschedule our lunch to next week?",
        "Great job on the presentation! The client loved it.",
        "Are you free for a quick call this afternoon?",
        "The grocery store was out of your favorite cereal. Got a different brand.",
        "Can you send me the meeting agenda? I need to prepare.",
        "We're having a team outing next Friday. Please RSVP by Thursday.",
        "Your car service appointment is confirmed for 10 AM tomorrow.",
        "I passed my driving test! So excited!",
        "The library book is due next week. Don't forget to return it.",
        "Mom called. She wants us to come for dinner on Sunday.",
        "Just got back from the dentist. Everything looks fine.",
        "The WiFi at home is down. Can you call the provider?",
        "I'm at the gym. Will be back in an hour.",
        "The restaurant reservation is at 7:30 PM. Don't be late!",
        "Can you help me move this weekend? I'll buy you pizza.",
        "My flight lands at 6 PM. Can you pick me up?",
        "Good morning! Have a great day at work.",
        "I'm watching a really good documentary about space exploration.",
        "The kids want to go to the zoo this weekend. Are you in?",
        "Just finished reading that book you recommended. Loved it!",
        "Our internet bill is due next week. Can you pay it?",
        "I'll cook dinner tonight. Any requests?",
        "The boss approved my vacation request. I'm so relieved!",
    ]
    
    # Create balanced dataset with more entries
    import random
    random.seed(42)
    
    # Augment messages
    all_spam = spam_messages * 15 + [
        f"SPECIAL OFFER! {random.choice(['Free', 'Win', 'Claim'])} {random.choice(['$1000', '?500', '$250'])} now!" 
        for _ in range(50)
    ]
    all_ham = ham_messages * 11 + [
        f"Hey, {random.choice(['can we talk', 'are you free', 'call me later'])}?"
        for _ in range(50)
    ]
    
    # Shuffle
    random.shuffle(all_spam)
    random.shuffle(all_ham)
    
    # Trim to reasonable size
    all_spam = all_spam[:500]
    all_ham = all_ham[:3000]
    
    labels = ['spam'] * len(all_spam) + ['ham'] * len(all_ham)
    messages = all_spam + all_ham
    
    combined = list(zip(labels, messages))
    random.shuffle(combined)
    
    df = pd.DataFrame(combined, columns=['v1', 'v2'])
    df.to_csv(filepath, index=False)
    print(f"[OK] Sample dataset created: {len(df)} records ({len(all_spam)} spam, {len(all_ham)} ham)")


if __name__ == '__main__':
    print("="*60)
    print("       SMS SPAM DETECTOR - MODEL TRAINING")
    print("="*60)
    
    data_path = download_dataset()
    
    print("\n Loading and preprocessing data...")
    df = load_and_preprocess_data(data_path)
    
    print("\n Training models...")
    best_model, results, metadata = train_all_models(df)
    
    print("\n" + "="*60)
    print("[OK] TRAINING COMPLETE!")
    print("="*60)
    print(f"Best Model: {metadata['best_model']}")
    print(f"Models saved to: models/")
    print(f"\nRun: python app.py  --> to start the web app")
    print("="*60)


