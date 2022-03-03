# Pyserini: uniCOIL (w/ TILDE) for MS MARCO (V2) Passage Ranking

This page describes how to reproduce experiments using uniCOIL with TILDE document expansion on the MS MARCO V2 passage corpus, as described in the following paper:

> Shengyao Zhuang and Guido Zuccon. [Fast Passage Re-ranking with Contextualized Exact Term
Matching and Efficient Passage Expansion.](https://arxiv.org/pdf/2108.08513) _arXiv:2108.08513_.

The original uniCOIL model is described here:

> Jimmy Lin and Xueguang Ma. [A Few Brief Notes on DeepImpact, COIL, and a Conceptual Framework for Information Retrieval Techniques.](https://arxiv.org/abs/2106.14807) _arXiv:2106.14807_.

In the original uniCOIL paper, doc2query-T5 is used to perform document expansion, which is slow and expensive.
As an alternative, Zhuang and Zuccon proposed to use the TILDE model to expand the documents instead, resulting in a faster and cheaper process that is just as effective.
For details of how to use TILDE to expand documents, please refer to the [TIDLE repo](https://github.com/ielab/TILDE).
For additional details on the original uniCOIL design (with doc2query-T5 expansion), please refer to the [COIL repo](https://github.com/luyug/COIL/tree/main/uniCOIL).

In this guide, we start with a version of the MS MARCO V2 passage corpus that has already been processed with uniCOIL + TILDE, i.e., gone through document expansion and term re-weighting.
Thus, no neural inference is involved.

## Data Prep

> You can skip the data prep and indexing steps if you use our pre-built indexes. Skip directly down to the "Retrieval" section below.

We're going to use the repository's root directory as the working directory.
First, we need to download and extract the MS MARCO V2 passage dataset with uniCOIL + TILDE processing:

```bash
# Alternate mirrors of the same data, pick one:
wget https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/data/msmarco-passage-v2-unicoil-tilde-expansion-b8.tar -P collections/
wget https://vault.cs.uwaterloo.ca/s/tb3m3J45HFJNAbq/download -O collections/msmarco-passage-v2-unicoil-tilde-expansion-b8.tar

tar -xvf collections/msmarco-passage-v2-unicoil-tilde-expansion-b8.tar -C collections/
```

To confirm, `msmarco-passage-v2-unicoil-tilde-expansion-b8.tar` is around 58 GB and should have an MD5 checksum of `acc4c9bc3506c3a496bf3e009fa6e50b`.

## Indexing

We can now index these docs:

```bash
python -m pyserini.index.lucene \
  --collection JsonVectorCollection \
  --input collections/msmarco-passage-v2-unicoil-tilde-expansion-b8/ \
  --index indexes/lucene-index.msmarco-v2-passage-unicoil-tilde-expansion/ \
  --generator DefaultLuceneDocumentGenerator \
  --threads 12 \
  --impact --pretokenized
```

The important indexing options to note here are `--impact --pretokenized`: the first tells Pyserini not to encode BM25 doclengths into Lucene's norms (which is the default) and the second option says not to apply any additional tokenization on the uniCOIL tokens.

Upon completion, we should have an index with 138,364,198 documents.
The indexing speed may vary; on a modern desktop with an SSD (using 12 threads, per above), indexing takes around 5 hours.

<!-- This is deprecated because we have pre-built indexes. Retaining for historic reasons.

If you want to save time and skip the indexing step, download the prebuilt index directly:

```bash
# Alternate mirrors of the same data, pick one:
wget https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/data/lucene-index.msmarco-v2-passage-unicoil-tilde-expansion-b8.tar.gz -P indexes/
wget https://vault.cs.uwaterloo.ca/s/rmFJCYEqfPrxcFE/download -O indexes/lucene-index.msmarco-v2-passage-unicoil-tilde-expansion-b8.tar.gz

tar -xzvf indexes/lucene-index.msmarco-v2-passage-unicoil-tilde-expansion-b8.tar.gz -C indexes/
```

To confirm, `lucene-index.msmarco-v2-passage-unicoil-tilde-expansion-b8.tar.gz` is around 30 GB and should have an MD5 checksum of `0f9b1f90751d49dd3a66be54dd0b4f82`.
This pre-built index was created with the above command, but with the addition of the `-optimize` option to merge index segments.

-->

## Retrieval

> If you've skipped the data prep and indexing steps and wish to directly use our pre-built indexes, use `--index msmarco-v2-passage-unicoil-tilde` in the command below.

We can now run retrieval:

```bash
python -m pyserini.search.lucene \
  --index indexes/lucene-index.msmarco-v2-passage-unicoil-tilde-expansion \
  --topics msmarco-v2-passage-dev \
  --encoder ielab/unicoil-tilde200-msmarco-passage \
  --output runs/run.msmarco-v2-passage-dev-unicoil-tilde-expansion.txt \
  --batch 144 --threads 36 \
  --hits 1000 \
  --impact
```

Here, we are using the transformer model to encode the queries on the fly using the CPU.
Note that the important option here is `--impact`, where we specify impact scoring.
With these impact scores, query evaluation is already slower than bag-of-words BM25; on top of that we're adding neural inference on the CPU.
A complete run should take around 30 minutes.

To evaluate, using `trec_eval`:

```bash
$ python -m pyserini.eval.trec_eval -c -M 100 -m map -m recip_rank msmarco-v2-passage-dev runs/run.msmarco-v2-passage-dev-unicoil-tilde-expansion.txt
Results:
map                   	all	0.1476
recip_rank            	all	0.1486

$ python -m pyserini.eval.trec_eval -c -m recall.100,1000 msmarco-v2-passage-dev runs/run.msmarco-v2-passage-dev-unicoil-tilde-expansion.txt
Results:
recall_100            	all	0.5630
recall_1000           	all	0.7733
```

There might be small differences in score due to platform differences in neural inference.
The above score was obtained on Linux; macOS results may be slightly different.

Alternatively, we can use pre-tokenized queries with pre-computed weights.
First, fetch the queries:

```bash
# Alternate mirrors of the same data, pick one:
wget https://rgw.cs.uwaterloo.ca/JIMMYLIN-bucket0/data/topics.msmarco-v2-passage.dev.unicoil-tilde-expansion.tsv.gz -P collections/
wget https://vault.cs.uwaterloo.ca/s/AAgRffaWQXdo8zi/download -O collections/topics.msmarco-v2-passage.dev.unicoil-tilde-expansion.tsv.gz
```

The MD5 checksum of the topics file should be `9c4fe0513cc8f45b44809f65c3c8bc20`.

We can now run retrieval:

```bash
python -m pyserini.search.lucene \
  --index indexes/lucene-index.msmarco-v2-passage-unicoil-tilde-expansion \
  --topics collections/topics.msmarco-v2-passage.dev.unicoil-tilde-expansion.tsv.gz \
  --output runs/run.msmarco-v2-passage-dev-unicoil-tilde-expansion.txt \
  --batch 144 --threads 36 \
  --hits 1000 \
  --impact
```

Here, we also specify `--impact` for impact scoring.
Since we're not applying neural inference over the queries, retrieval is faster, typically less than 10 minutes.
To evaluate using `trec_eval`, follow the same instructions above.
These results may be slightly different from the figures above, but they should be the same across platforms.

## Reproduction Log[*](reproducibility.md)

+ Results reproduced by [@lintool](https://github.com/lintool) on 2021-09-19 (commit [`6b9cc5b`](https://github.com/castorini/pyserini/commit/6b9cc5b1c2fee89597c5841a9f88395cf76bf60a))
+ Results reproduced by [@MXueguang](https://github.com/MXueguang) on 2021-09-22 (commit [`a4c12d2`](https://github.com/castorini/pyserini/commit/a4c12d28979b4ed9177845733932f94a1fcdfe64))
+ Results reproduced by [@prasys](https://github.com/prasys) on 2021-02-14 (commit [`3732c8e`](https://github.com/castorini/pyserini/commit/3732c8e3f1b72113a3961444b1ac37878afcbb64))
