"""
Medicine Warehouse Inventory Management System (MWIMS)

Main terminal application entry point supporting role-based interactive CRUD operations,
authentication, medicine inventory management, and reporting.
"""

from __future__ import annotations

import sys

from controllers import (
    auth_controller,
    inventory_controller,
    medicine_controller,
    report_controller,
    warehouse_controller,
)
from initialize_db import initialize_database
from middlewares import auth_middleware
from utils.constants import ROLE_ADMIN


def display_auth_menu() -> None:
    """Display terminal authentication portal menu."""
    print("\n" + "=" * 60)
    print(" 💊 MWIMS - Authentication Portal")
    print("=" * 60)
    print(" 1. Log In")
    print(" 2. Register New Account")
    print(" 3. Exit Application")
    print("=" * 60)


def display_main_menu() -> None:
    """Display main menu with role-specific indicators."""
    current_user = auth_middleware.get_current_user()
    username = current_user["username"] if current_user else "Guest"
    role = current_user["role"] if current_user else "None"
    is_admin = (role == ROLE_ADMIN)

    print("\n" + "=" * 60)
    print(f" 💊 MWIMS Dashboard | Active User: {username} (Role: {role.upper()})")
    print("=" * 60)
    print(" --- MEDICINE INVENTORY CRUD & MOVEMENTS ---")
    print(" 1. View Dashboard & Inventory Summary")
    print(" 2. List All Medicines (Read)")
    print(" 3. Add New Medicine (Create)")
    print(" 4. Update Medicine Details (Update)")
    if is_admin:
        print(" 5. Delete Medicine Record (Delete - Admin Only)")
    else:
        print(" 5. [LOCKED] Delete Medicine Record (Requires Admin Role)")
    print(" 6. Adjust Stock Quantity (+ / -)")
    print(" 7. Relocate Medicine (Transfer Location)")

    print("\n --- ALERTS, SEARCH & REPORTS ---")
    print(" 8. Search Medicines")
    print(" 9. Low Stock & Expiry Alerts")
    print(" 10. Generate Inventory Summary Report")

    if is_admin:
        print("\n --- ADMIN MANAGEMENT ---")
        print(" 11. Manage Users (List & Deactivate Accounts)")
        print(" 12. View System Audit Activity Logs")

    print("\n --- SESSION ---")
    print(" 13. Logout & Return to Portal")
    print("=" * 60)


def handle_login() -> bool:
    """Prompt user for credentials and establish session."""
    print("\n--- USER LOGIN ---")
    identifier = input("Enter Username or Email: ").strip()
    password = input("Enter Password: ").strip()

    success, msg, user = auth_controller.login_user(identifier, password)
    if success and user:
        print(f"\n[SUCCESS] Welcome, {user['username']}! Role: {user['role'].upper()}.")
        return True
    else:
        print(f"\n[LOGIN ERROR] {msg}")
        return False


def handle_registration() -> None:
    """Register a new user account."""
    print("\n--- REGISTER NEW USER ACCOUNT ---")
    username = input("Enter Username (min 3 chars): ").strip()
    email = input("Enter Email Address: ").strip()
    password = input("Enter Password (min 6 chars): ").strip()
    role = input("Enter Role ('staff' or 'admin', default: staff): ").strip() or "staff"

    success, msg = auth_controller.register_user(username, email, password, role)
    if success:
        print(f"\n[SUCCESS] {msg} Please log in with your credentials.")
    else:
        print(f"\n[REGISTRATION ERROR] {msg}")


def handle_add_medicine() -> None:
    """Add a new medicine record (Create)."""
    print("\n--- [CREATE] ADD NEW MEDICINE RECORD ---")
    name = input("Medicine Name (e.g. Paracetamol 500mg): ").strip()
    batch = input("Batch Number (e.g. BATCH-1001): ").strip()
    category = input("Category (Antibiotic, Analgesic, Antipyretic, etc.): ").strip()
    type_name = input("Type (Tablet, Capsule, Syrup, Injection, etc.): ").strip()

    try:
        qty = int(input("Initial Quantity: ").strip())
        min_stock = int(input("Minimum Stock Level: ").strip())
    except ValueError:
        print("\n[ERROR] Quantity and Minimum Stock must be valid integers.")
        return

    expiry = input("Expiry Date (YYYY-MM-DD): ").strip()
    rack = input("Rack Location (e.g. R1): ").strip()
    shelf = input("Shelf Location (e.g. S1): ").strip()
    cabinet = input("Cabinet Location (e.g. C1): ").strip()

    success, msg, med = medicine_controller.add_medicine(
        name, batch, category, type_name, qty, min_stock, expiry, rack, shelf, cabinet
    )

    if success:
        print(f"\n[SUCCESS] {msg}")
    else:
        print(f"\n[ERROR] {msg}")


def handle_update_medicine() -> None:
    """Update medicine fields (Update)."""
    print("\n--- [UPDATE] EDIT MEDICINE DETAILS ---")
    med_id = input("Enter Medicine ObjectId string to update: ").strip()

    ok, msg, existing = medicine_controller.get_medicine_by_id(med_id)
    if not ok or not existing:
        print(f"\n[ERROR] {msg}")
        return

    print(f"Editing Medicine: {existing.get('medicine_name')} (Batch: {existing.get('batch_number')})")
    print("Leave fields blank to keep existing values.")

    new_name = input(f"New Name [{existing.get('medicine_name')}]: ").strip()
    new_category = input(f"New Category [{existing.get('category')}]: ").strip()
    new_type = input(f"New Type [{existing.get('type')}]: ").strip()

    new_qty_str = input(f"New Quantity [{existing.get('quantity')}]: ").strip()
    new_min_str = input(f"New Minimum Stock [{existing.get('minimum_stock')}]: ").strip()
    new_expiry = input("New Expiry Date YYYY-MM-DD (Leave blank to keep): ").strip()

    update_payload = {}
    if new_name:
        update_payload["medicine_name"] = new_name
    if new_category:
        update_payload["category"] = new_category
    if new_type:
        update_payload["type"] = new_type
    if new_qty_str:
        try:
            update_payload["quantity"] = int(new_qty_str)
        except ValueError:
            print("[WARNING] Invalid quantity ignored.")
    if new_min_str:
        try:
            update_payload["minimum_stock"] = int(new_min_str)
        except ValueError:
            print("[WARNING] Invalid minimum stock ignored.")
    if new_expiry:
        update_payload["expiry_date"] = new_expiry

    if not update_payload:
        print("\nNo fields modified.")
        return

    success, msg = medicine_controller.update_medicine(med_id, update_payload)
    if success:
        print(f"\n[SUCCESS] {msg}")
    else:
        print(f"\n[ERROR] {msg}")


def handle_delete_medicine() -> None:
    """Delete a medicine record (Delete - Admin Only)."""
    current_user = auth_middleware.get_current_user()
    if not current_user or current_user.get("role") != ROLE_ADMIN:
        print("\n[PERMISSION DENIED] Deleting medicine records requires Administrator role.")
        return

    print("\n--- [DELETE] REMOVE MEDICINE RECORD (ADMIN ONLY) ---")
    med_id = input("Enter Medicine ObjectId string to DELETE: ").strip()

    confirm = input(f"Are you sure you want to permanently delete medicine ID '{med_id}'? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("\nDelete operation cancelled.")
        return

    success, msg = medicine_controller.delete_medicine(med_id)
    if success:
        print(f"\n[SUCCESS] {msg}")
    else:
        print(f"\n[ERROR] {msg}")


def handle_adjust_stock() -> None:
    """Adjust quantity delta of a medicine."""
    print("\n--- ADJUST STOCK QUANTITY ---")
    med_id = input("Enter Medicine ObjectId string: ").strip()
    try:
        delta = int(input("Enter quantity adjustment delta (+ to add stock, - to reduce): ").strip())
    except ValueError:
        print("\n[ERROR] Delta must be an integer.")
        return

    success, msg, updated = inventory_controller.adjust_stock(med_id, delta)
    if success:
        print(f"\n[SUCCESS] {msg}")
    else:
        print(f"\n[ERROR] {msg}")


def handle_relocate_medicine() -> None:
    """Relocate medicine to new warehouse storage coordinates."""
    print("\n--- RELOCATE WAREHOUSE STORAGE LOCATION ---")
    med_id = input("Enter Medicine ObjectId string: ").strip()
    new_rack = input("Enter New Rack ID: ").strip()
    new_shelf = input("Enter New Shelf ID: ").strip()
    new_cabinet = input("Enter New Cabinet ID: ").strip()

    success, msg = warehouse_controller.transfer_medicine_location(med_id, new_rack, new_shelf, new_cabinet)
    if success:
        print(f"\n[SUCCESS] {msg}")
    else:
        print(f"\n[ERROR] {msg}")


def handle_admin_user_management() -> None:
    """Manage users (Admin Only)."""
    current_user = auth_middleware.get_current_user()
    if not current_user or current_user.get("role") != ROLE_ADMIN:
        print("\n[PERMISSION DENIED] User management requires Administrator role.")
        return

    print("\n--- [ADMIN ONLY] USER MANAGEMENT ---")
    ok, msg, users = auth_controller.get_all_users()
    if not ok:
        print(f"[ERROR] {msg}")
        return

    print(f"\nRegistered Users ({len(users)} accounts):")
    for u in users:
        status = "Active" if u.get("is_active") else "Deactivated"
        print(f"  ID: {u.get('_id')} | Username: {u.get('username')} | Email: {u.get('email')} | Role: {u.get('role').upper()} | Status: {status}")

    print("\nOptions: (1) Deactivate User Account, (2) Back to Main Menu")
    opt = input("Choice: ").strip()
    if opt == "1":
        target_id = input("Enter User ObjectId to deactivate: ").strip()
        ok_deact, msg_deact = auth_controller.deactivate_user(target_id)
        if ok_deact:
            print(f"\n[SUCCESS] {msg_deact}")
        else:
            print(f"\n[ERROR] {msg_deact}")


def handle_admin_view_logs() -> None:
    """View audit activity logs (Admin Only)."""
    current_user = auth_middleware.get_current_user()
    if not current_user or current_user.get("role") != ROLE_ADMIN:
        print("\n[PERMISSION DENIED] Audit log viewing requires Administrator role.")
        return

    print("\n--- [ADMIN ONLY] AUDIT ACTIVITY LOGS ---")
    ok, msg, logs = report_controller.get_activity_logs(limit=25)
    if not ok:
        print(f"[ERROR] {msg}")
        return

    print(f"\nRecent System Activity Logs ({len(logs)} entries):")
    for log in logs:
        print(f"  [{log.get('timestamp')}] User: '{log.get('username')}' | Action: {log.get('action')} | Details: {log.get('details')}")


def run_app() -> None:
    """Main CLI application control loop."""
    print("Initializing MWIMS Backend Services...")
    initialize_database()

    while True:
        if not auth_middleware.is_authenticated():
            display_auth_menu()
            try:
                auth_choice = input("Select an option (1-3): ").strip()
                if auth_choice == "1":
                    handle_login()
                elif auth_choice == "2":
                    handle_registration()
                elif auth_choice == "3":
                    print("\nExiting MWIMS. Goodbye!")
                    sys.exit(0)
                else:
                    print("\nInvalid choice. Please enter 1, 2, or 3.")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting application...")
                sys.exit(0)
        else:
            display_main_menu()
            try:
                choice = input("Select an option (1-13): ").strip()

                if choice == "1":
                    ok, msg, summary = inventory_controller.get_inventory_dashboard_metrics()
                    print("\n--- INVENTORY DASHBOARD SUMMARY ---")
                    for key, val in summary.items():
                        print(f"  {key.replace('_', ' ').title()}: {val}")

                elif choice == "2":
                    ok, msg, medicines = medicine_controller.get_all_medicines()
                    print(f"\n--- ALL MEDICINES ({len(medicines)} items) ---")
                    for m in medicines:
                        print(
                            f"  ID: {m.get('_id')} | Batch: [{m.get('batch_number')}] "
                            f"{m.get('medicine_name')} ({m.get('type')}) - Qty: {m.get('quantity')} "
                            f"| Location: R:{m.get('rack')} S:{m.get('shelf')} C:{m.get('cabinet')}"
                        )

                elif choice == "3":
                    handle_add_medicine()

                elif choice == "4":
                    handle_update_medicine()

                elif choice == "5":
                    handle_delete_medicine()

                elif choice == "6":
                    handle_adjust_stock()

                elif choice == "7":
                    handle_relocate_medicine()

                elif choice == "8":
                    keyword = input("Enter search keyword (name or batch): ").strip()
                    ok, msg, results = medicine_controller.get_all_medicines()
                    filtered = [
                        m for m in results
                        if keyword.lower() in m.get("medicine_name", "").lower()
                        or keyword.lower() in m.get("batch_number", "").lower()
                    ]
                    print(f"\n--- SEARCH RESULTS ({len(filtered)} items) ---")
                    for m in filtered:
                        print(f"  ID: {m.get('_id')} | Batch: [{m.get('batch_number')}] {m.get('medicine_name')} - Qty: {m.get('quantity')}")

                elif choice == "9":
                    ok1, _, low_stock = inventory_controller.get_low_stock_alerts()
                    ok2, _, expiring = inventory_controller.get_expiry_alerts()
                    print(f"\n--- ALERTS ---")
                    print(f"  Low Stock Alerts ({len(low_stock)} items):")
                    for item in low_stock:
                        print(f"    - {item.get('medicine_name')} (Current: {item.get('quantity')}, Deficit: {item.get('deficit')})")
                    print(f"  Expiry Alerts ({len(expiring)} items):")
                    for item in expiring:
                        print(f"    - {item.get('medicine_name')} (Status: {item.get('expiry_status')}, Days Left: {item.get('days_remaining')})")

                elif choice == "10":
                    ok, msg, report = report_controller.generate_inventory_report()
                    print(f"\n--- {report.get('title')} ---")
                    print(f"Total Unique Items: {report.get('summary', {}).get('total_unique_medicines')}")
                    print(f"Total Stock Quantity: {report.get('summary', {}).get('total_stock_quantity')}")

                elif choice == "11":
                    handle_admin_user_management()

                elif choice == "12":
                    handle_admin_view_logs()

                elif choice == "13":
                    auth_controller.logout_user()
                    print("\nLogged out successfully. Returning to Authentication Portal.")

                else:
                    print("\nInvalid choice. Please enter a number from 1 to 13.")

            except (KeyboardInterrupt, EOFError):
                print("\nExiting application...")
                sys.exit(0)


if __name__ == "__main__":
    run_app()
