"""
Tests for Password Hashing
"""

import pytest
from app.auth.password import hash_password, verify_password


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password(self):
        """Test that password gets hashed"""
        password = "SecurePassword123"
        hashed = hash_password(password)

        # Hash should be different from plain password
        assert hashed != password
        # Hash should be reasonably long (bcrypt hashes are ~60 chars)
        assert len(hashed) > 50

    def test_verify_password_correct(self):
        """Test verifying correct password"""
        password = "TestPassword456"
        hashed = hash_password(password)

        # Correct password should verify
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password"""
        password = "CorrectPassword"
        wrong_password = "WrongPassword"
        hashed = hash_password(password)

        # Wrong password should not verify
        assert verify_password(wrong_password, hashed) is False

    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        password = "SamePassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different (due to salt)
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
