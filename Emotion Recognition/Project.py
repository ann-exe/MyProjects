import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
# import nltk
# import ssl
import emoji
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

sns.set()
sns.color_palette("rocket")

"""
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download("all")
"""

data = "data.csv"

df = pd.read_csv(data)

df.rename(columns={"Sl no": "S/N", "Search key": "Keywords", "Feeling": "Feelings"}, inplace=True)
columns = ["Tweets", "Keywords", "Feelings"]
df = df[columns]


def preprocessing_text(txt):
    pattern = r"http*.([^\s]+)"
    txt = re.sub(pattern, "", txt)
    pattern = r"ed.([^\s]+)"
    txt = re.sub(pattern, "", txt)
    pattern = r"\#(.*)\:" + " "
    text = re.sub(pattern, "", txt)
    token = TweetTokenizer(strip_handles=True, reduce_len=True, preserve_case=False)
    tokens = token.tokenize(text)
    tokens_cleared = [x for x in tokens if x not in stopwords.words("english")]
    tokens_lemmatized = [WordNetLemmatizer().lemmatize(x) for x in tokens_cleared]
    processed_text = " ".join(tokens_lemmatized)
    processed_text = emoji.demojize(processed_text).replace("_", " ")
    pattern = r"[^A-Za-z ]+"
    processed_text = re.sub(pattern, "", processed_text)
    processed_text = processed_text.strip()
    return processed_text


df["Tweets"] = df["Tweets"].apply(preprocessing_text)
df["Tweets"] = df["Tweets"].str.strip()
df["Tweets"].replace("", None, inplace=True)
df["Feelings"].replace("angry", "anger", inplace=True)
df["Feelings"].replace("happy", "happiness", inplace=True)
df["Feelings"].replace("sad", "sadness", inplace=True)
df = df.drop_duplicates()
df = df.dropna()

df.to_csv(path_or_buf="Tweets.csv", index=False)

plt.figure()
ax = sns.countplot(df, x="Feelings", palette="rocket_r")
ax.set_xlabel("Feelings", labelpad=20)
ax.set_ylabel("Occurrences", labelpad=20)
ax.set_title("Number of occurrences for each feeling", pad=20)
plt.show()
