1.	Why do we split documents into chunks at all? Name two of the three forces pulling on chunk size.
In order to have more precise vectors, so they fit into the LLM & embedding model context window, and reducing the cost & latency (less token in retriveal)  and reducing the hallucination risk. 
3 forces pulling on chunks:
    - retrieval quality
    - cost
    - hallucination risk
-----
2.	What is the weakness of fixed 100-word chunks? Give a concrete example from our corpus.
can end up with cut off sentences and chunks that loses the semantic because it does not include the heading in the text , for example Tokyo offices  
-----
3.	What does overlap fix, and what can it never fix?
overlap fixes the lost of content in the middle of a word or snetece but it can not fix the heading and contextual loss as well as cut off sentences
-----
4.	pack meets a sentence longer than the word limit. What does it do with it, and why?
When the pack function encounters a single sentence that is longer than the max_words limit, it keeps the entire sentence intact in a single chunk and does not split it.
it is used to use "Whole sentences only" and "Never chop a sentence." & Preserves semantic integrity.
-----
5.	In sentences_100, a heading can end up at the bottom of one chunk, away from its own text. Why does that happen, and how does by_section avoid it?
because sentences_100 will chunk the full sentence with a max amount of 100 words extra this might include the heading of the next section, this method is not semantic chunking therefore this can happen.
-----
6.	What does the contextual prefix add to a chunk, and what does it cost?
contextual prefix adds the title and heading to each chunk and it can cost in longer chunker , more tokens due to duplications
----- 
7.	What is an evidence span, and why only count a retrieved chunk as a hit if it holds the whole span?
An evidence span is the exact piece of text in a document that supports an answer to a question. We only count a retrieved chunk as a hit if it contains the entire evidence span, because a partial match may not provide enough information to support the answer accurately.
-----
8.	Recall@3 and MRR can disagree. Give an example of when.
Recall@3 and MRR can disagree when a query requires multiple relevant documents. For example, if the system retrieves one relevant document at rank 1 but misses the other relevant documents in the top 3, the MRR is high (1.0) because the first relevant document is ranked first, while Recall@3 is low because not all relevant documents were retrieved.
-----
9.	Why does build store a fingerprint, and what three things can make it trigger a rebuild?
The build function stores a fingerprint (a short SHA-256 hash) to check whether the existing Chroma index is still up to date and avoid unnecessary re-embedding.
three things can make it trigger a rebuild: model's name, chunks content and order
----
10.	You change the chunking strategy. What else in the system might quietly stop being right, and how would you find out?
relevance floor and top_k