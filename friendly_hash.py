"""
This module contains some helper functions for hashing strings and checking if a hash exists in a list of previous hashes.
"""

import hashlib

def hash(s: str) -> int:
    """
    Hash a string and return the first 12 digits of the resulting SHA1 hash.
    """
    return int(hashlib.sha1(s.encode("utf-8")).hexdigest(), 16) % (10 ** 12)

def hash_exists(content: str, previous_hashes: list[int]) -> bool:
    """
    Check if the hash of the content exists in the list of previous hashes.
    """
    return hash(content) in previous_hashes
