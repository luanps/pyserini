# msmarco-v2-doc-segmented-d2q-t5

Lucene index of the MS MARCO V2 segmented document corpus, with doc2query-T5 expansions.

This index was generated on 2022/02/01 at Anserini commit [`06fb4f`](https://github.com/castorini/anserini/commit/9ea3159adeeffd84e10e197af4c36febb5b74c7b) on `orca` with the following command:

```
target/appassembler/bin/IndexCollection -collection MsMarcoV2DocCollection \
  -generator DefaultLuceneDocumentGenerator -threads 24 \
  -input /store/collections/msmarco/msmarco_v2_doc_segmented_d2q-t5/ \
  -index indexes/lucene-index.msmarco-v2-doc-segmented-d2q-t5.20220201.9ea315/ \
  -optimize
```

Note that this index stores term frequencies only, which supports bag-of-words queries, but no phrase queries and no relevance feedback. In addition, there is no way to fetch the raw text.
