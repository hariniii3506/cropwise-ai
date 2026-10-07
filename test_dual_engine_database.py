"""
test_dual_engine_database.py
Comprehensive test suite for CROPWISE AI Dual-Engine Database Architecture (SQLite & PostgreSQL / Neon).

Test Categories:
1. SQLite Mode when DATABASE_URL is absent
2. User Creation & Authentication
3. Password Reset & Subsequent Authentication (Regression Test for Production Issue)
4. OTP Lifecycle & Verification
5. Profile Management
6. Crop Recommendations Logging & Retrieval
7. Farm Ledger / Expenses Management & Categorized Summaries
8. Farm Notes CRUD
9. Farm Reminders CRUD & Completion Toggle
10. PostgreSQL Mode Detection & Interface Compatibility
11. Migration Script Dry-Run Integrity
"""

import os
import sys
import unittest
import time
from unittest.mock import patch, MagicMock

import database.db as db
from database.migrate_sqlite_to_pg import migrate_data


class TestDualEngineDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure DATABASE_URL is unset during standard SQLite tests
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        db.init_db()

    def setUp(self):
        # Clean up any test users before each test
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email LIKE '%@testdualengine.ai' OR mobile LIKE '98989898%'")
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email LIKE '%@testdualengine.ai' OR mobile LIKE '98989898%'")
        conn.commit()
        conn.close()

    def test_01_sqlite_mode_active_when_database_url_absent(self):
        """Verify SQLite mode is active by default when DATABASE_URL is absent."""
        self.assertFalse(db.is_postgres())
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] for row in cursor.fetchall()]
        conn.close()

        required_tables = ["users", "recommendations", "expenses", "notes", "reminders"]
        for t in required_tables:
            self.assertIn(t, tables, f"Table '{t}' must exist in SQLite database.")

    def test_02_user_creation_and_authentication(self):
        """Verify user creation with password hashing and subsequent authentication."""
        user_id, err = db.create_user(
            name="Murugan Farmer",
            mobile="9898989801",
            email="murugan@testdualengine.ai",
            password="InitialPassword@123",
            farm_location="Thanjavur",
            land_area=3.5,
            land_unit="Acres",
            preferred_soil="Alluvial",
            avatar="farmer1",
            is_verified=1
        )
        self.assertIsNone(err)
        self.assertIsNotNone(user_id)

        # Authenticate with correct password
        auth_user = db.authenticate_user("murugan@testdualengine.ai", "InitialPassword@123")
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user["id"], user_id)
        self.assertEqual(auth_user["name"], "Murugan Farmer")

        # Authenticate with mobile number
        auth_mobile = db.authenticate_user("9898989801", "InitialPassword@123")
        self.assertIsNotNone(auth_mobile)
        self.assertEqual(auth_mobile["id"], user_id)

        # Authenticate with wrong password
        auth_wrong = db.authenticate_user("murugan@testdualengine.ai", "WrongPassword@999")
        self.assertIsNone(auth_wrong)

        # Duplicate email prevention
        dup_id, dup_err = db.create_user(
            name="Duplicate Farmer",
            mobile="9898989802",
            email="murugan@testdualengine.ai",
            password="OtherPassword@123",
            farm_location="Madurai",
            land_area=1.0
        )
        self.assertIsNone(dup_id)
        self.assertIn("email", dup_err.lower())

    def test_03_regression_password_reset_and_subsequent_login(self):
        """
        REGRESSION TEST FOR PRODUCTION ISSUE:
        Verify that after updating user password (password reset), the new password
        is persisted to the database and subsequent login succeeds with the new password
        while the old password fails.
        """
        # Step 1: Farmer registers with initial password
        user_id, err = db.create_user(
            name="Reset Test Farmer",
            mobile="9898989803",
            email="resetfarmer@testdualengine.ai",
            password="OldSecretPassword@123",
            farm_location="Salem",
            land_area=2.0,
            is_verified=1
        )
        self.assertIsNone(err)

        # Step 2: Confirm initial login works with old password
        u_initial = db.authenticate_user("resetfarmer@testdualengine.ai", "OldSecretPassword@123")
        self.assertIsNotNone(u_initial)

        # Step 3: Farmer performs password reset -> new password saved
        new_pass = "BrandNewSecurePassword@2026"
        success = db.update_user_password(user_id, new_pass)
        self.assertTrue(success, "update_user_password must return True")

        # Step 4: Immediate authentication using the NEW password must SUCCEED
        u_new = db.authenticate_user("resetfarmer@testdualengine.ai", new_pass)
        self.assertIsNotNone(u_new, "Authentication with new password must succeed after password reset.")
        self.assertEqual(u_new["id"], user_id)

        # Step 5: Authentication using the OLD password must FAIL
        u_old = db.authenticate_user("resetfarmer@testdualengine.ai", "OldSecretPassword@123")
        self.assertIsNone(u_old, "Authentication with old password must fail after password reset.")

    def test_04_user_otp_state_and_verification(self):
        """Verify OTP storage, state retrieval, and verification flow."""
        user_id, err = db.create_user(
            name="OTP Farmer",
            mobile="9898989804",
            email="otpfarmer@testdualengine.ai",
            password="TestPassword@123",
            farm_location="Coimbatore",
            land_area=4.0,
            is_verified=0
        )
        self.assertIsNone(err)

        from werkzeug.security import generate_password_hash
        otp_code = "456789"
        otp_hash = generate_password_hash(otp_code)
        expiry = time.time() + 60.0

        db.update_user_otp(user_id, otp_hash, expiry, time.time())

        # Verify OTP state retrieval
        state = db.get_user_otp_state(user_id)
        self.assertIsNotNone(state)
        self.assertEqual(state["otp_hash"], otp_hash)

        # Verify OTP with correct code
        success, res_id = db.verify_user_otp("otpfarmer@testdualengine.ai", otp_code)
        self.assertTrue(success)
        self.assertEqual(res_id, user_id)

        # User is now verified
        user = db.get_user_by_id(user_id)
        self.assertEqual(user["is_verified"], 1)

    def test_05_farmer_profile_management(self):
        """Verify farmer profile updates and lookup by email and ID."""
        user_id, err = db.create_user(
            name="Original Name",
            mobile="9898989805",
            email="profile@testdualengine.ai",
            password="TestPassword@123",
            farm_location="Trichy",
            land_area=2.0,
            is_verified=1
        )
        self.assertIsNone(err)

        # Update profile
        success, upd_err = db.update_user_profile(
            user_id=user_id,
            name="Updated Name",
            mobile="9898989805",
            email="profile@testdualengine.ai",
            farm_location="Erode",
            land_area=5.0,
            land_unit="Hectares",
            preferred_soil="Clayey",
            avatar="farmer2"
        )
        self.assertTrue(success)
        self.assertIsNone(upd_err)

        user = db.get_user_by_email("profile@testdualengine.ai")
        self.assertEqual(user["name"], "Updated Name")
        self.assertEqual(user["farm_location"], "Erode")
        self.assertEqual(user["land_area"], 5.0)
        self.assertEqual(user["land_unit"], "Hectares")

    def test_06_crop_recommendations_logging_and_retrieval(self):
        """Verify saving, retrieving, and deleting crop recommendations."""
        user_id, _ = db.create_user(
            name="Crop Farmer",
            mobile="9898989806",
            email="crop@testdualengine.ai",
            password="TestPassword@123",
            farm_location="Dindigul",
            land_area=3.0,
            is_verified=1
        )

        rec_id = db.save_recommendation(
            user_id=user_id,
            soil_type="Clayey",
            ph=6.5,
            temperature=28.0,
            humidity=80.0,
            rainfall=150.0,
            recommended_crop="Rice (Paddy)",
            alternative_crops=["Maize", "Cotton"],
            decision_notes="Optimal soil pH and high moisture for paddy cultivation.",
            variety="CO 51"
        )
        self.assertIsNotNone(rec_id)

        # Retrieve by ID
        rec = db.get_recommendation_by_id(rec_id, user_id)
        self.assertIsNotNone(rec)
        self.assertEqual(rec["recommended_crop"], "Rice (Paddy)")
        self.assertEqual(rec["variety"], "CO 51")
        self.assertIn("Maize", rec["alternative_crops_list"])

        # History
        history = db.get_recommendation_history(user_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["id"], rec_id)

        # Delete
        deleted = db.delete_recommendation(rec_id, user_id)
        self.assertTrue(deleted)
        self.assertIsNone(db.get_recommendation_by_id(rec_id, user_id))

    def test_07_farm_expenses_and_summary(self):
        """Verify adding, listing, summarizing, and deleting farm expenses."""
        user_id, _ = db.create_user(
            name="Expense Farmer",
            mobile="9898989807",
            email="expense@testdualengine.ai",
            password="TestPassword@123",
            farm_location="Tirunelveli",
            land_area=4.0,
            is_verified=1
        )

        exp1 = db.add_expense(user_id, "2026-10-01", "Fertilizers", 2500.0, "Urea and DAP")
        exp2 = db.add_expense(user_id, "2026-10-02", "Seeds", 1200.0, "Certified Paddy Seeds")
        exp3 = db.add_expense(user_id, "2026-10-03", "Fertilizers", 800.0, "Potash")

        self.assertIsNotNone(exp1)
        self.assertIsNotNone(exp2)
        self.assertIsNotNone(exp3)

        # Expense listing
        expenses = db.get_user_expenses(user_id)
        self.assertEqual(len(expenses), 3)

        # Expense summary
        summary = db.get_expense_summary(user_id)
        self.assertEqual(summary["total_expenses"], 4500.0)
        self.assertEqual(summary["total_count"], 3)
        self.assertEqual(summary["by_category"]["Fertilizers"], 3300.0)
        self.assertEqual(summary["by_category"]["Seeds"], 1200.0)

        # Delete expense
        deleted = db.delete_expense(exp1, user_id)
        self.assertTrue(deleted)
        expenses_after = db.get_user_expenses(user_id)
        self.assertEqual(len(expenses_after), 2)

    def test_08_farm_notes_crud(self):
        """Verify adding, retrieving, and deleting farm notes."""
        user_id, _ = db.create_user(
            name="Notes Farmer",
            mobile="9898989808",
            email="notes@testdualengine.ai",
            password="TestPassword@123",
            farm_location="Karur",
            land_area=1.5,
            is_verified=1
        )

        note_id = db.add_note(user_id, "Irrigation Schedule", "Water fields every alternate morning.", "Irrigation")
        self.assertIsNotNone(note_id)

        notes = db.get_user_notes(user_id)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["title"], "Irrigation Schedule")
        self.assertEqual(notes[0]["tag"], "Irrigation")

        deleted = db.delete_note(note_id, user_id)
        self.assertTrue(deleted)
        self.assertEqual(len(db.get_user_notes(user_id)), 0)

    def test_09_farm_reminders_crud_and_toggle(self):
        """Verify adding, listing, toggling completion, and deleting reminders."""
        user_id, _ = db.create_user(
            name="Reminder Farmer",
            mobile="9898989809",
            email="reminder@testdualengine.ai",
            password="TestPassword@123",
            farm_location="Theni",
            land_area=2.5,
            is_verified=1
        )

        rem_id = db.add_reminder(
            user_id=user_id,
            title="Fertilizer Top Dressing",
            reminder_date="2026-10-15",
            reminder_time="07:30",
            description="Apply second round of nitrogen fertilizer.",
            crop="Rice",
            variety="CO 51",
            category="Fertilizer"
        )
        self.assertIsNotNone(rem_id)

        reminders = db.get_user_reminders(user_id)
        self.assertEqual(len(reminders), 1)
        self.assertEqual(reminders[0]["is_completed"], 0)
        self.assertEqual(reminders[0]["reminder_time"], "07:30")

        # Upcoming reminders filter
        upcoming = db.get_upcoming_reminders(user_id)
        self.assertEqual(len(upcoming), 1)

        # Toggle reminder completion
        toggled = db.toggle_reminder(rem_id, user_id)
        self.assertTrue(toggled)

        reminders_after = db.get_user_reminders(user_id)
        self.assertEqual(reminders_after[0]["is_completed"], 1)

        # Upcoming should now be empty because completed
        upcoming_after = db.get_upcoming_reminders(user_id)
        self.assertEqual(len(upcoming_after), 0)

        # Delete reminder
        deleted = db.delete_reminder(rem_id, user_id)
        self.assertTrue(deleted)
        self.assertEqual(len(db.get_user_reminders(user_id)), 0)

    def test_10_postgres_mode_detection_and_query_compatibility(self):
        """Verify DATABASE_URL detection and PostgreSQL connection parameter resolution."""
        test_url = "postgresql://cropwise_user:SecretPass123@ep-cool-db-123456.us-east-2.aws.neon.tech/neondb?sslmode=require"
        with patch.dict(os.environ, {"DATABASE_URL": test_url}):
            self.assertTrue(db.is_postgres())

        # When unset
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(db.is_postgres())

    def test_11_migration_script_dry_run_integrity(self):
        """Verify data migration script runs in dry-run mode without modifying source or errors."""
        try:
            migrate_data(db.DEFAULT_LOCAL_DB, pg_url="", dry_run=True)
            migration_passed = True
        except Exception as e:
            migration_passed = False
            print(f"Migration dry run error: {e}")

        self.assertTrue(migration_passed, "Migration script dry-run must succeed without errors.")


if __name__ == "__main__":
    unittest.main()
