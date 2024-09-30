import hashlib


def hash_account_number(account_number):
    """
    Hashes the account number using a cryptographic hash function.
    """
    return hashlib.sha256(account_number.encode('utf-8')).hexdigest()