# 20 Newsgroups

About 18,000 Usenet posts from 20 newsgroups, split by date into a train (60%) and a
test (40%) set, with duplicates and some headers removed ("bydate" version).

## Files

- `20news-bydate.tar.gz`: extracts to `20news-bydate-train/<newsgroup>/<message id>` and
  `20news-bydate-test/<newsgroup>/<message id>`.

## Source

Jason Rennie's page: http://qwone.com/~jason/20Newsgroups/ (collected by Ken Lang).

## License

No explicit license. The dataset has been freely redistributed for research and teaching
for decades (e.g. by scikit-learn's `fetch_20newsgroups`); the posts belong to their
authors.
