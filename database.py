import sqlite3
import os

def init_db():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            department TEXT,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'employee',
            status TEXT DEFAULT 'active',
            basic_salary REAL DEFAULT 0,
            per_day_salary REAL DEFAULT 0,
            profile_photo TEXT,
            bio TEXT,
            address TEXT,
            emergency_contact TEXT,
            blood_group TEXT,
            date_of_birth TEXT,
            joining_date TEXT,
            designation TEXT,
            theme TEXT DEFAULT 'default',
            show_timer INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            date TEXT NOT NULL,
            punch_in TEXT,
            punch_out TEXT,
            total_hours TEXT,
            status TEXT DEFAULT 'present',
            punch_in_photo TEXT,
            punch_out_photo TEXT,
            punch_in_location TEXT,
            punch_out_location TEXT,
            ip_address TEXT,
            late_dot INTEGER DEFAULT 0,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            leave_type TEXT DEFAULT 'Casual',
            from_date TEXT,
            to_date TEXT,
            total_days INTEGER DEFAULT 1,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS short_leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            duration_hours REAL DEFAULT 1,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'open',
            admin_reply TEXT,
            replied_on TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resignations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            resignation_date TEXT,
            last_working_date TEXT,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            admin_remarks TEXT,
            applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            title TEXT NOT NULL,
            message TEXT,
            type TEXT DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            for_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT DEFAULT 'Osho Industries Limited',
            company_logo TEXT,
            office_time_in TEXT DEFAULT '10:30',
            office_time_out TEXT DEFAULT '18:30',
            grace_period_min INTEGER DEFAULT 10,
            late_dot_end_min INTEGER DEFAULT 30,
            half_day_after TEXT DEFAULT '11:00',
            dots_per_leave INTEGER DEFAULT 4,
            short_leave_per_month INTEGER DEFAULT 1,
            short_leave_hours REAL DEFAULT 1,
            smtp_email TEXT DEFAULT '',
            smtp_password TEXT DEFAULT '',
            smtp_server TEXT DEFAULT 'smtp.gmail.com',
            smtp_port INTEGER DEFAULT 587,
            casual_leaves INTEGER DEFAULT 12,
            sick_leaves INTEGER DEFAULT 10,
            earned_leaves INTEGER DEFAULT 15,
            late_deduction REAL DEFAULT 50,
            absent_deduction REAL DEFAULT 0,
            overtime_rate REAL DEFAULT 100,
            default_theme TEXT DEFAULT 'red'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holidays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'National',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            month TEXT NOT NULL,
            basic_salary REAL DEFAULT 0,
            working_days INTEGER DEFAULT 0,
            present_days INTEGER DEFAULT 0,
            late_days INTEGER DEFAULT 0,
            leave_days INTEGER DEFAULT 0,
            absent_days INTEGER DEFAULT 0,
            half_days INTEGER DEFAULT 0,
            late_dots INTEGER DEFAULT 0,
            late_deduction REAL DEFAULT 0,
            absent_deduction REAL DEFAULT 0,
            overtime_hours REAL DEFAULT 0,
            overtime_amount REAL DEFAULT 0,
            gross_salary REAL DEFAULT 0,
            net_salary REAL DEFAULT 0,
            generated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        )
    ''')

    # Default admin
    try:
        cursor.execute('''
            INSERT INTO employees (emp_id, name, email, department, password, role, basic_salary, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('ADMIN001', 'Admin', 'admin@company.com', 'Management', 'admin123', 'admin', 50000, 'active'))
    except:
        pass

    # Default settings with Osho Industries
    try:
        cursor.execute('''
            INSERT INTO settings (
                company_name, office_time_in, office_time_out,
                grace_period_min, late_dot_end_min, half_day_after, dots_per_leave,
                short_leave_per_month, short_leave_hours, default_theme
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Osho Industries Limited', '10:30', '18:30', 10, 30, '11:00', 4, 1, 1, 'red'))
    except:
        pass

    # Update existing settings to Osho Industries
    try:
        cursor.execute("UPDATE settings SET company_name = 'Osho Industries Limited' WHERE id = 1 AND company_name = 'My Company'")
    except:
        pass

    # Safe migrations
    migrations = [
        'ALTER TABLE employees ADD COLUMN status TEXT DEFAULT "active"',
        'ALTER TABLE employees ADD COLUMN basic_salary REAL DEFAULT 0',
        'ALTER TABLE employees ADD COLUMN per_day_salary REAL DEFAULT 0',
        'ALTER TABLE employees ADD COLUMN profile_photo TEXT',
        'ALTER TABLE employees ADD COLUMN bio TEXT',
        'ALTER TABLE employees ADD COLUMN address TEXT',
        'ALTER TABLE employees ADD COLUMN emergency_contact TEXT',
        'ALTER TABLE employees ADD COLUMN blood_group TEXT',
        'ALTER TABLE employees ADD COLUMN date_of_birth TEXT',
        'ALTER TABLE employees ADD COLUMN joining_date TEXT',
        'ALTER TABLE employees ADD COLUMN designation TEXT',
        'ALTER TABLE employees ADD COLUMN theme TEXT DEFAULT "default"',
        'ALTER TABLE employees ADD COLUMN show_timer INTEGER DEFAULT 1',
        'ALTER TABLE attendance ADD COLUMN late_dot INTEGER DEFAULT 0',
        'ALTER TABLE settings ADD COLUMN grace_period_min INTEGER DEFAULT 10',
        'ALTER TABLE settings ADD COLUMN late_dot_end_min INTEGER DEFAULT 30',
        'ALTER TABLE settings ADD COLUMN half_day_after TEXT DEFAULT "11:00"',
        'ALTER TABLE settings ADD COLUMN dots_per_leave INTEGER DEFAULT 4',
        'ALTER TABLE settings ADD COLUMN short_leave_per_month INTEGER DEFAULT 1',
        'ALTER TABLE settings ADD COLUMN short_leave_hours REAL DEFAULT 1',
        'ALTER TABLE settings ADD COLUMN late_deduction REAL DEFAULT 50',
        'ALTER TABLE settings ADD COLUMN absent_deduction REAL DEFAULT 0',
        'ALTER TABLE settings ADD COLUMN overtime_rate REAL DEFAULT 100',
        'ALTER TABLE settings ADD COLUMN default_theme TEXT DEFAULT "red"',
        'ALTER TABLE settings ADD COLUMN company_logo TEXT',
    ]

    for sql in migrations:
        try:
            cursor.execute(sql)
        except:
            pass

    # Default holidays
    default_holidays = [
        ('2026-01-26', 'Republic Day', 'National'),
        ('2026-03-10', 'Holi', 'National'),
        ('2026-04-14', 'Ambedkar Jayanti', 'National'),
        ('2026-05-01', 'May Day', 'National'),
        ('2026-08-15', 'Independence Day', 'National'),
        ('2026-10-02', 'Gandhi Jayanti', 'National'),
        ('2026-10-20', 'Dussehra', 'National'),
        ('2026-11-09', 'Diwali', 'National'),
        ('2026-12-25', 'Christmas', 'National'),
    ]
    for date, name, htype in default_holidays:
        try:
            cursor.execute('INSERT INTO holidays (date, name, type) VALUES (?, ?, ?)', (date, name, htype))
        except:
            pass

    conn.commit()
    conn.close()
    os.makedirs('static/photos', exist_ok=True)
    os.makedirs('static/profiles', exist_ok=True)
    os.makedirs('static/uploads', exist_ok=True)
    print("✅ Database ready - Osho Industries Limited!")

if __name__ == '__main__':
    init_db()