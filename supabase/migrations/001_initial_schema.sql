-- Review Summary Platform: Initial Schema
-- Creates reviews and summaries tables with RLS policies and indexes.

-- reviews table
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('product', 'book', 'restaurant', 'movie', 'other')),
    rating SMALLINT CHECK (rating BETWEEN 1 AND 5),
    source VARCHAR(500),
    author_id UUID REFERENCES auth.users(id),
    summary_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- summaries table
CREATE TABLE summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    summary TEXT NOT NULL,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'negative', 'neutral', 'mixed')),
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score BETWEEN -1.00 AND 1.00),
    keywords TEXT[] DEFAULT '{}',
    pros TEXT[] DEFAULT '{}',
    cons TEXT[] DEFAULT '{}',
    ai_model VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- FK
ALTER TABLE reviews ADD CONSTRAINT fk_summary FOREIGN KEY (summary_id) REFERENCES summaries(id);

-- RLS
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE summaries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "reviews_read_all" ON reviews FOR SELECT USING (true);
CREATE POLICY "reviews_insert_auth" ON reviews FOR INSERT WITH CHECK (auth.uid() = author_id);
CREATE POLICY "summaries_read_all" ON summaries FOR SELECT USING (true);

-- Indexes
CREATE INDEX idx_reviews_category ON reviews(category);
CREATE INDEX idx_reviews_author ON reviews(author_id);
CREATE INDEX idx_reviews_created ON reviews(created_at DESC);
