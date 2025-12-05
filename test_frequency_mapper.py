"""
Quick test for FrequencyMapper without database connection
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from scripts.map_frequency import FrequencyMapper

# Test loading data
mapper = FrequencyMapper()

print("Testing COCA data loading...")
mapper.load_frequency_data("coca")
print(f"Loaded {len(mapper.frequency_map)} words")
print(f"Source: {mapper.source_name}\n")

# Test edge cases
test_words = [
    # Basic cases
    "the",              # Most common word
    "hello",            # Common word
    "contract",         # Less common
    "algorithm",        # Technical word (only in Google)
    "xyzabc123",        # Non-existent word

    # Case sensitivity
    "THE",              # Uppercase
    "Hello",            # Mixed case
    "ALGORITHM",        # All caps

    # Multi-word phrases
    "make up",          # Phrasal verb (should match "make")
    "get together",     # Phrasal verb (should match "get")
    "take care of",     # Multi-word phrase (should match "take")

    # Special characters
    "hello!",           # With punctuation (should strip)
    "  contract  ",     # With spaces (should strip)
    "",                 # Empty string

    # Rare words
    "antidisestablishmentarianism",  # Very long rare word
    "pneumonoultramicroscopicsilicovolcanoconiosis",  # Longest English word
]
print("Testing word matching:")
for word in test_words:
    rank = mapper.get_rank(word)
    status = "[Found]" if rank != 999999 else "[Not found]"
    word_display = repr(word) if len(word) < 20 else repr(word[:17] + "...")
    print(f"  {word_display:30s} -> rank {rank:6d} {status}")

print("\nTesting Google Ngram...")
mapper.load_frequency_data("google")
print(f"Loaded {len(mapper.frequency_map)} words\n")

print("Testing word matching:")
for word in test_words:
    rank = mapper.get_rank(word)
    status = "[Found]" if rank != 999999 else "[Not found]"
    word_display = repr(word) if len(word) < 20 else repr(word[:17] + "...")
    print(f"  {word_display:30s} -> rank {rank:6d} {status}")

print("\nTesting ALL sources (COCA + Google)...")
mapper.load_frequency_data("all")
print(f"Loaded {len(mapper.frequency_map)} words\n")

print("Testing word matching:")
for word in test_words:
    rank = mapper.get_rank(word)
    status = "[Found]" if rank != 999999 else "[Not found]"
    word_display = repr(word) if len(word) < 20 else repr(word[:17] + "...")
    print(f"  {word_display:30s} -> rank {rank:6d} {status}")

print("\n[OK] All tests passed!")
