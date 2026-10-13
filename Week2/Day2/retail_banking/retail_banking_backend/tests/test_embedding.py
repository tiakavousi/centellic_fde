from embedding import embed_texts


def test_embed_texts_returns_vector()->None:
    """
    Build the embedding and assert the result.
    """
    text = "The rewards credit card carries a representative APR set out on the account summary."
    vectors, tokens = embed_texts([text], input_type="document")
    
    assert len(vectors) == 1
    assert len(vectors[0]) > 0
    assert tokens > 0