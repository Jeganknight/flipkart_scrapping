#!pip install pandas
#!pip install scikit-learn
#!pip install vaderSentiment
#!pip install nltk
import pandas as pd
import nltk
nltk.download('stopwords')
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from nltk.corpus import stopwords
import re
from sklearn.preprocessing import StandardScaler


df = pd.read_csv('review_data.csv')


analyzer = SentimentIntensityAnalyzer()

def preprocess_text(text):
    text = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.lower()
    stop_words = set(stopwords.words('english'))
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)


df['cleaned_comments'] = df['Comment'].apply(preprocess_text)

df['sentiment_score'] = df['cleaned_comments'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

tfidf = TfidfVectorizer(max_df=0.8, min_df=3, stop_words='english', ngram_range=(1, 2))
tfidf_matrix = tfidf.fit_transform(df['cleaned_comments'])
feature_names = tfidf.get_feature_names_out()

tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

df = df.join(tfidf_df)


df['Likes_Dislikes'] = df['Like Count'] - df['Dislike Count']
df['weighted_sentiment'] = df['sentiment_score'] * df['Likes_Dislikes']


product_summary = df.groupby('Product Name').agg({
       'weighted_sentiment': 'mean',
       'Like Count': 'sum',
       'Dislike Count': 'sum',
       'sentiment_score': 'mean',

   }).reset_index()

scaler = StandardScaler()
product_summary[['weighted_sentiment', 'Likes', 'Dislikes']] = scaler.fit_transform(
      product_summary[['weighted_sentiment', 'Like Count', 'Dislike Count']]
   )



top_laptops = product_summary.sort_values(by='weighted_sentiment', ascending=False).head(5)

import matplotlib.pyplot as plt
import seaborn as sns


sns.set(style="whitegrid")


plt.figure(figsize=(12, 8))
sns.barplot(x='weighted_sentiment', y='Product Name', data=top_laptops, palette='viridis')
plt.title('Top Laptops by Weighted Sentiment')
plt.xlabel('Weighted Sentiment')
plt.ylabel('Product Name')
plt.show()

#Adjusting weights 

like_weight = 0.5
dislike_weight = -0.5

df['adjusted_weighted_sentiment'] = df['sentiment_score'] * (df['Like Count'] * like_weight - df['Dislike Count'] * dislike_weight)

product_summary = df.groupby('Product Name').agg({
    'adjusted_weighted_sentiment': 'mean',
    'Like Count': 'sum',
    'Dislike Count': 'sum',
    'sentiment_score': 'mean',
}).reset_index()


top_laptops_adjusted = product_summary.sort_values(by='adjusted_weighted_sentiment', ascending=False).head(5)
#print(top_laptops_adjusted)


plt.figure(figsize=(12, 8))
sns.barplot(x='adjusted_weighted_sentiment', y='Product Name', data=top_laptops_adjusted, palette='viridis')
plt.title('Top Laptops by Adjusted Weighted Sentiment')
plt.xlabel('Adjusted Weighted Sentiment')
plt.ylabel('Product Name')
plt.show()

print("Completed")