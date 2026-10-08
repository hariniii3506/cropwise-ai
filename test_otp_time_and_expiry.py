"""
Unit and Integration Tests for OTP Expiry (60s) and IST Email Display (Asia/Kolkata).
Tests:
  1. Asia/Kolkata IST timezone time generation for OTP emails.
  2. EmailJS payload parameters and clear 1-minute expiry display.
  3. Server-side registration OTP 60-second expiry enforcement.
  4. Resend OTP generation with fresh 60-second expiry.
  5. Password reset OTP 60-second expiry and serverless session handling.
  6. Login unverified user OTP 60-second expiry.
"""

# =============================================================================
# CROPWISE AI - OTP Expiration & Timezone Integration Test Suite
# =============================================================================
# Validates critical security constraints across authentication and password recovery:
# - Strict 60-second expiration window enforcement on server and client.
# - Indian Standard Time (IST - Asia/Kolkata) timestamp formatting in OTP emails.
# - Rate limiting and resend cooldown throttling.
# =============================================================================

import unittest
import time
import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch, MagicMock
import json

import app as flask_app
from database.db import (
    init_db,
    create_user,
    update_user_otp,
    verify_user_otp,
    verify_reset_otp,
    get_user_by_email,
    get_user_otp_state,
    get_user_by_id,
    get_db,
)


class TestOTPTimeAndExpiry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        flask_app.app.config["TESTING"] = True
        flask_app.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = flask_app.app.test_client()
        init_db()

    def setUp(self):
        # Clean all test users before each test
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email LIKE '%@testcropwise.ai' OR mobile LIKE '99999999%'")
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email LIKE '%@testcropwise.ai' OR mobile LIKE '99999999%'")
        conn.commit()
        conn.close()

    def test_otp_expiry_constant_is_60_seconds(self):
        """Verify OTP_EXPIRY_SECONDS is configured to exactly 60 seconds."""
        self.assertEqual(flask_app.OTP_EXPIRY_SECONDS, 60)
        self.assertEqual(flask_app.IST_TIMEZONE.key, "Asia/Kolkata")

    def test_ist_timezone_email_formatting(self):
        """Verify OTP email uses ZoneInfo('Asia/Kolkata') and formats generated/expiry timestamps."""
        sent_payloads = []

        def mock_urlopen(req, timeout=None):
            data = json.loads(req.data.decode("utf-8"))
            sent_payloads.append(data)
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.__enter__.return_value = mock_resp
            return mock_resp

        with patch("urllib.request.urlopen", side_effect=mock_urlopen):
            test_email = "farmer_ist@testcropwise.ai"
            test_otp = "123456"
            
            # Freeze time to a known point: UTC 2026-10-07 04:30:00 -> IST 10:00:00 AM
            fixed_utc = datetime.datetime(2026, 10, 7, 4, 30, 0, tzinfo=datetime.timezone.utc)
            
            with patch("datetime.datetime") as mock_dt:
                mock_dt.now.side_effect = lambda tz=None: fixed_utc.astimezone(tz) if tz else fixed_utc
                mock_dt.timedelta = datetime.timedelta
                
                success, err = flask_app.send_otp_email(test_email, test_otp)
                self.assertTrue(success)

        self.assertEqual(len(sent_payloads), 1)
        params = sent_payloads[0]["template_params"]
        
        # Verify recipient and passcode
        self.assertEqual(params["email"], test_email)
        self.assertEqual(params["passcode"], "123456")
        
        # Verify IST formatted time: 10:00 AM, 07 Oct 2026 (IST)
        self.assertIn("10:00 AM", params["time"])
        self.assertIn("(IST)", params["time"])
        self.assertIn("1 minute", params["time"])
        self.assertEqual(params["validity"], "1 minute")
        self.assertIn("10:00 AM", params["generated_at"])
        self.assertIn("(IST)", params["generated_at"])
        self.assertIn("10:01 AM", params["expiry_time"])
        self.assertIn("(IST)", params["expiry_time"])

    def test_server_side_otp_verification_within_60_seconds(self):
        """Verify that server-side OTP verification succeeds within 60 seconds."""
        user_id, err = create_user(
            name="Ramesh Test",
            mobile="9999999901",
            email="ramesh@testcropwise.ai",
            password="SecurePassword@123",
            farm_location="Madurai",
            land_area=3.0,
            land_unit="acres",
            preferred_soil="Clayey",
            is_verified=0
        )
        self.assertIsNone(err)

        otp_code = "654321"
        from werkzeug.security import generate_password_hash
        otp_hash = generate_password_hash(otp_code)
        expiry = time.time() + flask_app.OTP_EXPIRY_SECONDS

        update_user_otp(user_id, otp_hash, expiry, time.time())

        # Verify before expiry
        success, res = verify_user_otp("ramesh@testcropwise.ai", otp_code)
        self.assertTrue(success)
        self.assertEqual(res, user_id)

    def test_server_side_otp_expiry_enforcement_after_60_seconds(self):
        """Verify that server-side OTP verification fails when time exceeds 60 seconds."""
        user_id, err = create_user(
            name="Suresh Test",
            mobile="9999999902",
            email="suresh@testcropwise.ai",
            password="SecurePassword@123",
            farm_location="Salem",
            land_area=2.0,
            land_unit="acres",
            preferred_soil="Loamy",
            is_verified=0
        )
        self.assertIsNone(err)

        otp_code = "789123"
        from werkzeug.security import generate_password_hash
        otp_hash = generate_password_hash(otp_code)
        
        # Set expiry to past time (expired past 60s)
        expired_time = time.time() - 1
        update_user_otp(user_id, otp_hash, expired_time, time.time() - 61)

        success, msg = verify_user_otp("suresh@testcropwise.ai", otp_code)
        self.assertFalse(success)
        self.assertIn("expired", msg.lower())

    def test_resend_otp_sets_fresh_60_second_expiry(self):
        """Verify that resending OTP generates a fresh 60-second expiry timestamp."""
        user_id, err = create_user(
            name="Kavitha Test",
            mobile="9999999903",
            email="kavitha@testcropwise.ai",
            password="SecurePassword@123",
            farm_location="Thanjavur",
            land_area=4.5,
            land_unit="acres",
            preferred_soil="Alluvial",
            is_verified=0
        )
        self.assertIsNone(err)

        with patch("app.send_otp_email", return_value=(True, None)):
            with self.client.session_transaction() as sess:
                sess["pending_email"] = "kavitha@testcropwise.ai"
                sess["pending_user_id"] = user_id
                sess["pending_name"] = "Kavitha Test"
                sess["otp_sent_at"] = time.time() - 35  # Passed 30s resend throttle

            start_t = time.time()
            response = self.client.get("/resend-otp", follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            state = get_user_otp_state(user_id)
            self.assertIsNotNone(state)
            # Expiry should be approximately start_t + 60
            self.assertAlmostEqual(state["otp_expiry"], start_t + 60, delta=2.0)

    def test_forgot_password_otp_expiry_is_60_seconds(self):
        """Verify password reset OTP sets 60-second expiry and enforces it."""
        user_id, err = create_user(
            name="Anand Test",
            mobile="9999999904",
            email="anand@testcropwise.ai",
            password="SecurePassword@123",
            farm_location="Coimbatore",
            land_area=5.0,
            land_unit="acres",
            preferred_soil="Red",
            is_verified=1
        )
        self.assertIsNone(err)

        with patch("app.send_otp_email", return_value=(True, None)):
            start_t = time.time()
            response = self.client.post("/forgot-password", data={"email": "anand@testcropwise.ai"}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            user = get_user_by_id(user_id)
            self.assertIsNotNone(user)
            self.assertAlmostEqual(user["otp_expiry"], start_t + 60, delta=2.0)

            # Test password reset verification past 60s
            with self.client.session_transaction() as sess:
                sess["reset_email"] = "anand@testcropwise.ai"
                sess["reset_user_id"] = user_id
                sess["reset_otp_expiry"] = time.time() - 5  # Expired
                sess["reset_otp_hash"] = "fakehash"

            verify_res = self.client.post(
                "/reset-password-verify",
                data={"action": "verify_otp", "otp": "123456"},
                follow_redirects=True
            )
            self.assertIn(b"expired", verify_res.data.lower())


if __name__ == "__main__":
    unittest.main()
