CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS parent_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    language_pair TEXT NOT NULL,
    navigator_analysis TEXT NOT NULL,
    error_snippet TEXT,
    working_fix_snippet TEXT,
    test_feedback TEXT,
    attempt_number INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS child_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL REFERENCES parent_documents(id) ON DELETE CASCADE,
    language_pair TEXT NOT NULL,
    navigator_analysis TEXT NOT NULL,
    embedding vector(384) 
    -- vector(384) matches all-MiniLM-L6-v2's output dimension — it always produces 384-dimensional 
    --  embeddings.If you use a different model later this number changes, which is one reason to document your 
    -- embedding model choice somewhere in your repo.
);

CREATE INDEX IF NOT EXISTS child_vectors_embedding_idx 
ON child_vectors 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
--vector_cosine_ops means similarity is measured by cosine distance 
-- lists = 100 is the number of clusters IVFFlat builds internally. 
-- Rule of thumb: sqrt(number of rows) — so 100 is appropriate up to about 10,000 
-- stored experiences, which you won't hit for a while.

-- ------------------------------------------------------------------------------------
-- Users table for authentication
-- ------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
