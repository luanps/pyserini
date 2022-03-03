#
# Pyserini: Reproducible IR research with sparse and dense representations
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import faiss
import pickle
import argparse
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--embeddings', type=str, required=True, help="Path to embeddings file from generate_passage_embeddings.py from dkrr repo")
    parser.add_argument('--output', type=str, help='Path to store faiss IndexFlatIP', required=True)
    args = parser.parse_args()

    with open(args.embeddings, 'rb') as embeddings_file:
        ids, embeddings = pickle.load(embeddings_file)
        embeddings = np.array(embeddings, dtype=np.float32)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        faiss.write_index(index, args.output)
    
    
