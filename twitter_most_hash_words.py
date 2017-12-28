# Print most common words in a corpus collected from Twitter
#
# Full description:
# http://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/
# http://marcobonzanini.com/2015/03/09/mining-twitter-data-with-python-part-2/
# http://marcobonzanini.com/2015/03/17/mining-twitter-data-with-python-part-3-term-frequencies/
#
# Run:
# python twitter_most_common_words.py <filename.jsonl>

import sys
import json
from collections import Counter
import re
from nltk.corpus import stopwords
import string
import vincent
 
punctuation = list(string.punctuation)
stop = stopwords.words('english') + punctuation + ['RT', 'via']
 
emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
 
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]
    
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)
 
def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s, lowercase=True):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens


if __name__ == '__main__':
    fname = sys.argv[1]

    with open(fname, 'r') as f:
        count_all = Counter()
        for line in f:
            tweet = json.loads(line)
#            tokens = preprocess(tweet['text'])
            terms_stop = [term for term in preprocess(tweet['text']) if term not in stop]
            # Count hashtags only
            terms_hash = [term for term in preprocess(tweet['text']) 
              if term.startswith('#') and
		not term.endswith('#')]
            count_all.update(terms_hash)
        print(count_all.most_common(5))

word_freq = count_all.most_common(10)
labels, freq = zip(*word_freq)
data = {'data': freq, 'x': labels}
bar = vincent.Bar(data, iter_idx='x')
bar.to_json('data/term_freq.json')
