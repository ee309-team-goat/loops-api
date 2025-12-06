# English Word Frequency Data

This directory contains word frequency data collected from reliable sources for English vocabulary learning and analysis.

## Directory Structure

```
data/
└── frequency/
    ├── COCA_5000.csv                     # Top 5000 words from COCA corpus
    ├── google_ngram_frequency_alpha.txt  # 246k words from Google Books Ngram
    ├── oxford-3000.csv                   # Oxford 3000 with CEFR levels
    └── oxford-5000.csv                   # Oxford 5000 with CEFR levels
```

## Data Sources

### 1. COCA Word Frequency List (Top 5000)

**File:** `frequency/COCA_5000.csv`

**Source:** Corpus of Contemporary American English (COCA)

**Description:**
- Contains the top 5,000 most frequent words (lemmas) from the COCA corpus
- Based on 1+ billion words of text from 1990-2019
- Includes frequency data across 8 genres: blogs, web, TV/Movies, spoken, fiction, magazine, newspaper, and academic

**Data Fields:**
- `rank`: Frequency rank (1-5000)
- `lemma`: Base form of the word
- `PoS`: Part of speech tag
- `freq`: Total frequency count
- `perMil`: Frequency per million words
- Genre-specific frequency data (blog, web, TVM, spok, fic, mag, news, acad)

**Citation:**
```
Davies, Mark. (2008-) The Corpus of Contemporary American English (COCA).
Available online at https://www.english-corpora.org/coca/
```

**Repository:** https://github.com/brucewlee/COCA-WordFrequency

**Official Website:** https://www.wordfrequency.info/free.asp

**License:**
- Free for academic and non-commercial use
- Data reposted for academic reproducibility
- Original data © Mark Davies

**Notes:**
- The full COCA corpus contains 60,000+ words, but only the top 5,000 are freely available
- Extended lists (20k, 60k) are available for purchase at wordfrequency.info

---

### 2. Google Books Ngram Word Frequency

**File:** `frequency/google_ngram_frequency_alpha.txt`

**Source:** Google Books Ngram Corpus (processed by hackerb9/gwordlist)

**Description:**
- Contains 246,591 alphabetically-verified English words sorted by frequency
- Extracted from Google Books corpus (1+ trillion words)
- Cleaned and verified using GCIDE (Webster), WordNet, and OED dictionaries
- Removes OCR errors, foreign text, and symbols

**Data Fields:**
- `RANKING`: Frequency rank (1-246,591)
- `WORD`: Word in lowercase
- `COUNT`: Total occurrence count in corpus
- `PERCENT`: Percentage of total corpus
- `CUMULATIVE`: Cumulative percentage

**Citation:**
```
Google Books Ngram Corpus, processed and distributed by hackerb9/gwordlist.
Available at https://github.com/hackerb9/gwordlist
```

**Repository:** https://github.com/hackerb9/gwordlist

**Official Google Source:** https://storage.googleapis.com/books/ngrams/books/datasetsv3.html

**License:**
- Data freely available from Google Books Ngram project
- Processed data distributed under open license for academic use

**Notes:**
- Based on books published up to 2019
- Multiple dictionary verification ensures word validity
- Largest free English word frequency dataset available

---

### 3. Oxford 3000 Word List with CEFR Levels

**File:** `frequency/oxford-3000.csv`

**Source:** Oxford University Press - Oxford Learner's Dictionaries

**Description:**
- The 3,000 most important words to learn in English
- Selected by language experts based on frequency and pedagogical value
- Covers CEFR levels A1-B2
- Includes words that are:
  - Most frequently used in English
  - Essential for practical communication
  - Important across different text types

**Data Fields:**
- `word`: The English word
- `class`: Part of speech (noun, verb, adjective, etc.)
- `level`: CEFR proficiency level (a1, a2, b1, b2)

**CEFR Levels:**
- **A1**: Beginner
- **A2**: Elementary
- **B1**: Intermediate
- **B2**: Upper-Intermediate

**Selection Criteria:**
- Frequency in English corpora
- Range across different types of texts
- Relevance for language learners (e.g., body parts, travel terms)
- Expert consultation with language education professionals

**Citation:**
```
Oxford University Press. The Oxford 3000™.
Available at https://www.oxfordlearnersdictionaries.com/about/wordlists/oxford3000-5000
```

**Repository:** https://github.com/Berehulia/Oxford-3000-5000

**Official Website:** https://www.oxfordlearnersdictionaries.com/about/wordlists/oxford3000-5000

**License:**
- © Oxford University Press
- Free for educational and non-commercial use
- All credit to Oxford Learner's Dictionaries

---

### 4. Oxford 5000 Word List with CEFR Levels

**File:** `frequency/oxford-5000.csv`

**Source:** Oxford University Press - Oxford Learner's Dictionaries

**Description:**
- Extended core word list for advanced learners
- Includes Oxford 3000 + additional 2,000 words
- Covers CEFR levels A1-C1
- Designed for advanced learners progressing from B2 to C1

**Data Fields:**
- `word`: The English word
- `class`: Part of speech (noun, verb, adjective, etc.)
- `level`: CEFR proficiency level (a1, a2, b1, b2, c1)

**CEFR Levels Covered:**
- **A1-B2**: Same as Oxford 3000
- **B2-C1**: Additional 2,000 advanced vocabulary words

**Citation:**
```
Oxford University Press. The Oxford 5000™.
Available at https://www.oxfordlearnersdictionaries.com/about/wordlists/oxford3000-5000
```

**Repository:** https://github.com/Berehulia/Oxford-3000-5000

**Official Website:** https://www.oxfordlearnersdictionaries.com/about/wordlists/oxford3000-5000

**License:**
- © Oxford University Press
- Free for educational and non-commercial use

---

## Data Statistics

| Dataset | Words | Format | CEFR Levels | Frequency Data |
|---------|-------|--------|-------------|----------------|
| COCA 5000 | 5,000 | CSV | ❌ | ✅ Genre-specific |
| Google Ngram | 246,591 | TXT | ❌ | ✅ Global counts |
| Oxford 3000 | ~3,000 | CSV | ✅ A1-B2 | ❌ |
| Oxford 5000 | ~5,000 | CSV | ✅ A1-C1 | ❌ |

## Usage Notes

### For Korean Vocabulary Learning App

While these datasets contain English word frequency data, they are valuable for:

1. **Cross-reference and Comparison**: Understanding frequency patterns in English can inform Korean vocabulary selection strategies

2. **CEFR Mapping Framework**: The Oxford lists provide a proven framework for organizing vocabulary by difficulty level (A1-C1), which can be adapted for Korean learning materials (TOPIK levels)

3. **Methodology Reference**: The selection criteria and data structure can guide similar data collection efforts for Korean vocabulary

4. **Frequency Analysis**: Study how frequency-based learning paths are structured in established language learning resources

### Recommended Next Steps for Korean Data

Consider collecting similar data for Korean vocabulary:
- **Korean Frequency Lists**: National Institute of Korean Language (국립국어원)
- **TOPIK Vocabulary**: Words organized by TOPIK levels (1-6)
- **Sejong Corpus**: Modern Korean language corpus
- **Korean Learners Dictionary**: 한국어 학습자 사전

---

## Data Integrity

All files were downloaded on 2025-12-05 from the sources listed above.

**File Checksums (SHA-256):**
```bash
# Generate checksums with:
sha256sum frequency/*
```

To verify data integrity, you can regenerate checksums and compare with future downloads.

---

## Additional Resources

### COCA (Corpus of Contemporary American English)
- **Main Website**: https://www.english-corpora.org/coca/
- **Word Frequency Data**: https://www.wordfrequency.info/
- **Full Access**: Subscription required for 60k+ word lists

### Google Books Ngram
- **Official Data**: https://storage.googleapis.com/books/ngrams/books/datasetsv3.html
- **Processed Word List**: https://github.com/hackerb9/gwordlist
- **Interactive Viewer**: https://books.google.com/ngrams

### Oxford Learner's Dictionaries
- **Word Lists Homepage**: https://www.oxfordlearnersdictionaries.com/about/wordlists/oxford3000-5000
- **Interactive Browser**: Search and filter words online
- **Dictionary Integration**: Each word links to full dictionary entry

### GitHub Repositories
- **COCA Top 5000**: https://github.com/brucewlee/COCA-WordFrequency
- **Google Ngram Processed**: https://github.com/hackerb9/gwordlist
- **Oxford 3000/5000 CSV**: https://github.com/Berehulia/Oxford-3000-5000
- **Oxford Extended Resources**: https://github.com/winterdl/oxford-5000-vocabulary-audio-definition

---

## License and Attribution

### Important Legal Notes

1. **Academic Use**: All datasets are free for academic and educational purposes
2. **Non-Commercial**: Free for non-commercial applications
3. **Attribution Required**: Always cite the original sources when using this data
4. **Commercial Use**: Contact rights holders for commercial licensing
5. **Redistribution**: Check individual licenses before redistributing

### Proper Attribution

When using this data in publications, applications, or research, please cite:

```bibtex
@misc{coca2008,
  author = {Davies, Mark},
  title = {The Corpus of Contemporary American English (COCA)},
  year = {2008--},
  url = {https://www.english-corpora.org/coca/}
}

@misc{googlengram,
  author = {{Google Inc.}},
  title = {Google Books Ngram Corpus},
  url = {https://storage.googleapis.com/books/ngrams/books/datasetsv3.html}
}

@misc{oxford3000,
  author = {{Oxford University Press}},
  title = {The Oxford 3000 and Oxford 5000},
  url = {https://www.oxfordlearnersdictionaries.com/about/wordlists/oxford3000-5000}
}
```

---

## Contact and Updates

**Project:** Loops API - Korean Vocabulary Learning Platform

**Issue:** #22 - English Word Frequency Data Collection

**Date Collected:** 2025-12-05

For updates or questions about this data collection, please refer to the project repository or contact the project maintainers.

---

## Changelog

### 2025-12-05
- Initial data collection completed
- Downloaded COCA Top 5000 word frequency list (CSV format)
- Downloaded Google Books Ngram 246k word frequency list (TXT format)
- Downloaded Oxford 3000 with CEFR levels (CSV format)
- Downloaded Oxford 5000 with CEFR levels (CSV format)
- Created comprehensive documentation with sources, citations, and licenses
- All data files verified and ready for use in development
