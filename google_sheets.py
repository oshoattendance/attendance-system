import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# ============ CONFIGURATION ============
SPREADSHEET_ID = "1ATCZyx93BwgKwXZLp4zdg-lR0IIPfgWR_i-2aQPVJyE"

SERVICE_ACCOUNT_FILE = "secrets/service_account.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ============ CUSTOM HEADER MAPPING ============
# Left side = Google Sheet me dikhega (aap change kar sakte ho)
# Right side = Python code use karta hai (ye mat badlo)

EMPLOYEE_HEADERS = {
    'display': ['Employee ID', 'Full Name', 'Email Address', 'Mobile Number', 'Department', 'Role', 'Registration Date'],
    'code': ['emp_id', 'name', 'email', 'phone', 'department', 'role', 'created_at']
}

ATTENDANCE_HEADERS = {
    'display': ['Employee ID', 'Employee Name', 'Date', 'Punch In Time', 'Punch Out Time', 'Total Working Hours', 'Status', 'Location', 'Photo'],
    'code': ['emp_id', 'employee_name', 'date', 'punch_in', 'punch_out', 'total_hours', 'status', 'location', 'photo']
}

LEAVE_HEADERS = {
    'display': ['Employee ID', 'Employee Name', 'Leave Type', 'From Date', 'To Date', 'Total Days', 'Reason', 'Status', 'Applied On'],
    'code': ['emp_id', 'employee_name', 'leave_type', 'from_date', 'to_date', 'total_days', 'reason', 'status', 'applied_on']
}

# ============ CLIENT SETUP ============
def get_client():
    try:
        credentials = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        print(f"❌ Google Sheet client error: {e}")
        return None

def get_sheet(tab_name):
    try:
        client = get_client()
        if client is None:
            return None
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        return spreadsheet.worksheet(tab_name)
    except Exception as e:
        print(f"❌ Sheet '{tab_name}' error: {e}")
        return None

# ============ SETUP HEADERS ============
def setup_headers():
    """Google Sheet me custom headers set karo"""
    try:
        client = get_client()
        if client is None:
            return False
        
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        # Employees headers
        emp_sheet = spreadsheet.worksheet("Employees")
        emp_sheet.update('A1', [EMPLOYEE_HEADERS['display']])
        
        # Bold + Color format
        emp_sheet.format('A1:G1', {
            'textFormat': {'bold': True, 'fontSize': 12, 'foregroundColorStyle': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}},
            'backgroundColor': {'red': 0.31, 'green': 0.27, 'blue': 0.88},
            'horizontalAlignment': 'CENTER',
            'verticalAlignment': 'MIDDLE'
        })
        
        # Attendance headers
        att_sheet = spreadsheet.worksheet("Attendance")
        att_sheet.update('A1', [ATTENDANCE_HEADERS['display']])
        
        att_sheet.format('A1:I1', {
            'textFormat': {'bold': True, 'fontSize': 12, 'foregroundColorStyle': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}},
            'backgroundColor': {'red': 0.02, 'green': 0.59, 'blue': 0.41},
            'horizontalAlignment': 'CENTER',
            'verticalAlignment': 'MIDDLE'
        })
        
        # Leave headers
        leave_sheet = spreadsheet.worksheet("Leave_Requests")
        leave_sheet.update('A1', [LEAVE_HEADERS['display']])
        
        leave_sheet.format('A1:I1', {
            'textFormat': {'bold': True, 'fontSize': 12, 'foregroundColorStyle': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}},
            'backgroundColor': {'red': 0.96, 'green': 0.62, 'blue': 0.04},
            'horizontalAlignment': 'CENTER',
            'verticalAlignment': 'MIDDLE'
        })
        
        print("✅ All headers set with beautiful formatting!")
        return True
        
    except Exception as e:
        print(f"❌ Header setup error: {e}")
        return False

# ============ EMPLOYEE SYNC ============
def sync_employee(emp_id, name, email, phone, department, role):
    try:
        sheet = get_sheet("Employees")
        if sheet is None:
            return False
        
        all_values = sheet.get_all_values()
        
        row_to_update = None
        for idx, row in enumerate(all_values):
            if idx == 0:
                continue
            if len(row) > 0 and str(row[0]).strip() == str(emp_id).strip():
                row_to_update = idx + 1
                break
        
        row_data = [
            emp_id, name, email or '', phone or '',
            department, role,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
        
        if row_to_update:
            sheet.update(f'A{row_to_update}:G{row_to_update}', [row_data])
            print(f"✅ Employee {emp_id} updated in Google Sheet")
        else:
            sheet.append_row(row_data)
            print(f"✅ Employee {emp_id} added to Google Sheet")
        
        return True
        
    except Exception as e:
        print(f"❌ Employee sync error: {e}")
        return False

# ============ ATTENDANCE SYNC ============
def sync_attendance(emp_id, employee_name, date, punch_in, punch_out,
                    total_hours, status, location='', photo=''):
    try:
        sheet = get_sheet("Attendance")
        if sheet is None:
            return False
        
        all_values = sheet.get_all_values()
        
        row_to_update = None
        for idx, row in enumerate(all_values):
            if idx == 0:
                continue
            if len(row) >= 3 and str(row[0]).strip() == str(emp_id).strip() and str(row[2]).strip() == str(date).strip():
                row_to_update = idx + 1
                break
        
        row_data = [
            emp_id, employee_name, date,
            punch_in or '', punch_out or '',
            total_hours or '', status,
            location or '', photo or ''
        ]
        
        if row_to_update:
            sheet.update(f'A{row_to_update}:I{row_to_update}', [row_data])
            print(f"✅ Attendance updated for {emp_id} on {date}")
        else:
            sheet.append_row(row_data)
            print(f"✅ Attendance added for {emp_id} on {date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Attendance sync error: {e}")
        return False

# ============ LEAVE SYNC ============
def sync_leave(emp_id, employee_name, leave_type, from_date, to_date,
               total_days, reason, status, applied_on):
    try:
        sheet = get_sheet("Leave_Requests")
        if sheet is None:
            return False
        
        all_values = sheet.get_all_values()
        
        row_to_update = None
        for idx, row in enumerate(all_values):
            if idx == 0:
                continue
            if len(row) >= 4 and str(row[0]).strip() == str(emp_id).strip() and str(row[3]).strip() == str(from_date).strip():
                row_to_update = idx + 1
                break
        
        row_data = [
            emp_id, employee_name, leave_type,
            from_date, to_date, total_days,
            reason, status, applied_on
        ]
        
        if row_to_update:
            sheet.update(f'A{row_to_update}:I{row_to_update}', [row_data])
            print(f"✅ Leave updated for {emp_id}")
        else:
            sheet.append_row(row_data)
            print(f"✅ Leave added for {emp_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Leave sync error: {e}")
        return False

# ============ FULL SYNC FROM DATABASE ============
def sync_all_from_db():
    import sqlite3
    
    results = {
        'employees': 0,
        'attendance': 0,
        'leaves': 0,
        'errors': []
    }
    
    try:
        conn = sqlite3.connect('attendance.db')
        conn.row_factory = sqlite3.Row
        
        # Clear existing data (except headers)
        try:
            emp_sheet = get_sheet("Employees")
            att_sheet = get_sheet("Attendance")
            leave_sheet = get_sheet("Leave_Requests")
            
            if emp_sheet:
                emp_sheet.batch_clear(["A2:Z10000"])
            if att_sheet:
                att_sheet.batch_clear(["A2:Z10000"])
            if leave_sheet:
                leave_sheet.batch_clear(["A2:Z10000"])
        except:
            pass
        
        # Sync Employees
        print("🔄 Syncing Employees...")
        employees = conn.execute('SELECT * FROM employees ORDER BY emp_id').fetchall()
        emp_rows = []
        for emp in employees:
            emp_rows.append([
                emp['emp_id'],
                emp['name'],
                emp['email'] or '',
                emp['phone'] or '',
                emp['department'],
                emp['role'],
                emp['created_at'] if 'created_at' in emp.keys() else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        if emp_rows and emp_sheet:
            emp_sheet.append_rows(emp_rows)
            results['employees'] = len(emp_rows)
            print(f"✅ {len(emp_rows)} employees synced")
        
        # Sync Attendance
        print("🔄 Syncing Attendance...")
        attendance = conn.execute('''
            SELECT a.*, e.name as employee_name
            FROM attendance a
            JOIN employees e ON a.emp_id = e.emp_id
            ORDER BY a.date DESC
        ''').fetchall()
        
        att_rows = []
        for att in attendance:
            att_rows.append([
                att['emp_id'],
                att['employee_name'],
                att['date'],
                att['punch_in'] or '',
                att['punch_out'] or '',
                att['total_hours'] or '',
                att['status'],
                att['punch_in_location'] or '',
                att['punch_in_photo'] or ''
            ])
        
        if att_rows and att_sheet:
            att_sheet.append_rows(att_rows)
            results['attendance'] = len(att_rows)
            print(f"✅ {len(att_rows)} attendance records synced")
        
        # Sync Leaves
        print("🔄 Syncing Leaves...")
        leaves = conn.execute('''
            SELECT l.*, e.name as employee_name
            FROM leave_requests l
            JOIN employees e ON l.emp_id = e.emp_id
            ORDER BY l.applied_on DESC
        ''').fetchall()
        
        leave_rows = []
        for leave in leaves:
            leave_rows.append([
                leave['emp_id'],
                leave['employee_name'],
                leave['leave_type'] if 'leave_type' in leave.keys() else 'Casual',
                leave['from_date'] if 'from_date' in leave.keys() else '',
                leave['to_date'] if 'to_date' in leave.keys() else '',
                leave['total_days'] if 'total_days' in leave.keys() else 1,
                leave['reason'],
                leave['status'],
                leave['applied_on']
            ])
        
        if leave_rows and leave_sheet:
            leave_sheet.append_rows(leave_rows)
            results['leaves'] = len(leave_rows)
            print(f"✅ {len(leave_rows)} leave records synced")
        
        conn.close()
        
        # Setup beautiful headers
        setup_headers()
        
        print("\n" + "=" * 50)
        print("🎉 FULL SYNC COMPLETED!")
        print("=" * 50)
        print(f"📊 Employees: {results['employees']}")
        print(f"📊 Attendance: {results['attendance']}")
        print(f"📊 Leaves: {results['leaves']}")
        
    except Exception as e:
        results['errors'].append(str(e))
        print(f"❌ Full sync error: {e}")
    
    return results

# ============ CHANGE HEADERS ============
def change_header(tab_name, new_headers):
    """
    Google Sheet ke headers change karo
    
    Usage:
    change_header('Employees', ['कर्मचारी ID', 'नाम', 'ईमेल', 'फोन', 'विभाग', 'पद', 'तारीख'])
    """
    try:
        sheet = get_sheet(tab_name)
        if sheet is None:
            return False
        
        sheet.update('A1', [new_headers])
        
        # Format headers
        last_col = chr(64 + len(new_headers))
        sheet.format(f'A1:{last_col}1', {
            'textFormat': {'bold': True, 'fontSize': 12, 'foregroundColorStyle': {'rgbColor': {'red': 1, 'green': 1, 'blue': 1}}},
            'backgroundColor': {'red': 0.31, 'green': 0.27, 'blue': 0.88},
            'horizontalAlignment': 'CENTER'
        })
        
        print(f"✅ Headers updated for {tab_name}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============ TEST ============
if __name__ == '__main__':
    print("🔄 Setting up custom headers...\n")
    setup_headers()
    print("\n🔄 Syncing all data...\n")
    sync_all_from_db()