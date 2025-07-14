from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

# --- Database Setup ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Check if logo column exists in company table
        c.execute("PRAGMA table_info(company)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'company' not in [table[0] for table in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
            # Create company table if it doesn't exist
            c.execute('''CREATE TABLE company (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                status TEXT,
                comments TEXT,
                interview_type TEXT,
                priority_percentage TEXT,
                logo TEXT,
                details TEXT,
                salary TEXT,
                location TEXT
            )''')
        elif 'logo' not in columns:
            # Add logo column if it doesn't exist
            c.execute('ALTER TABLE company ADD COLUMN logo TEXT')
        elif 'details' not in columns:
            c.execute('ALTER TABLE company ADD COLUMN details TEXT')
        elif 'salary' not in columns:
            c.execute('ALTER TABLE company ADD COLUMN salary TEXT')
        elif 'location' not in columns:
            c.execute('ALTER TABLE company ADD COLUMN location TEXT')
        
        c.execute('''CREATE TABLE IF NOT EXISTS team_leader (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            color TEXT,
            password TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS recruiter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            leader_id INTEGER,
            name TEXT,
            FOREIGN KEY(leader_id) REFERENCES team_leader(id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS hiring (
            leader_id INTEGER PRIMARY KEY,
            hires INTEGER,
            FOREIGN KEY(leader_id) REFERENCES team_leader(id)
        )''')
        
        # Remove all team leaders not in Unit C (ids 1-5)
        c.execute('DELETE FROM team_leader WHERE id NOT IN (1,2,3,4,5,100)')
        c.execute('DELETE FROM recruiter WHERE leader_id NOT IN (1,2,3,4,5)')
        c.execute('DELETE FROM hiring WHERE leader_id NOT IN (1,2,3,4,5)')
        
        # Insert initial team leaders for Unit C if not present
        c.execute('SELECT COUNT(*) FROM team_leader WHERE id IN (1,2,3,4,5)')
        if c.fetchone()[0] < 5:
            leaders = [
                (1, 'Omar Essa', '01021484537', 'primary', '1020'),
                (2, 'Maryam Mamdouh', '+20 103 235 8726', 'success', '2030'),
                (3, 'Radwa Ashraf', '+20 111 042 8831', 'info', None),
                (4, 'Sara', '+20 114 657 7224', 'warning', '3040'),
                (5, 'Eman', '+20 115 922 1939', 'danger', '4050'),
            ]
            for leader in leaders:
                c.execute('INSERT OR IGNORE INTO team_leader (id, name, phone, color, password) VALUES (?, ?, ?, ?, ?)', leader)
        # Add manager Nada Adel as a special user (id=100)
        c.execute('INSERT OR IGNORE INTO team_leader (id, name, phone, color, password) VALUES (?, ?, ?, ?, ?)', (100, 'Nada Adel', '', 'primary', '1010'))
        
        # Clear and insert real companies data with logos and locations
        c.execute('DELETE FROM company')
        companies = [
            ('Alorica', 'Active', 'English Spanish Bilingual site grads only', 'online interview', '100%', 'fas fa-building', '''Alorica is Hiring for English-Speaking Accounts\nRequired English Level: B1+ to C1\nPosition: Customer Service\nWork Type: Full-time, On-site\nShifts: Rotational shifts\nBenefits: Paid training, Social and medical insurance, Transportation provided (door-to-door for females after 10 PM), Promotion opportunity after 3 months, Grads, Dropouts can apply, Egyptians only\nTraining Duration: 3 months\nTraining Location: Alorica office – Palm Strip Mall, 6th October\nAfter Training: Work continues from Alorica office – Sheikh Zayed\nLocation: 6th October City\nIf you are interested Send a Voice note introduce yourself. Follow Us on : insource''', 'Up to EGP 21,000 gross depend on the account and the english level', '6th October City'),
            ('VXI', 'On hold', 'English only', 'Hyprid interview', '', 'fas fa-phone', '', '', 'Nasr City'),
            ('Foundever', 'Active', 'English account', 'online interview', '', 'fas fa-globe', '', '', 'Cairo'),
            ('Vodafone', 'Active', 'insource staff member', 'online interview', '100%', 'fas fa-signal', '''Join Vodafone Egypt – Customer Care Opportunities for High Value Customers, Corporate, and Technical Support Accounts!\nRequirements: Excellent English & strong communication, Bachelor’s degree, Males only (with Military & Graduation certificates), Under 30 years old, No 1st/2nd-degree relatives in Vodafone Customer Care\nOffer: Salary: 14k Gross + up to 10% bonus, 10,000 EGP handset allowance every 2 years, Meal allowance, discounts, Vodafone RED line, Installments up to 15,000 EGP, Insurance + transportation (Hadayek El Maadi Metro), Rotational shifts – 8:45 hrs/day incl. 1-hr break, Great work environment + growth opportunities''', '14k Gross + up to 10% bonus', 'Hadayek El Maadi'),
            ('IGT', 'Active', 'german and french', 'Hyprid interview', '60%', 'fas fa-gamepad', '', '', 'Cairo'),
            ('Concentrix', 'On hold', 'English & German', 'site interview', '50%', 'fas fa-users', '', '', 'Cairo'),
            ('HSBC', 'Active', '', 'online interview', '80%', 'fas fa-university', '', '', 'Cairo'),
            ('Golf global', 'On hold', '', 'site interview', '90%', 'fas fa-golf-ball', '', '', 'Cairo'),
            ('Housing', 'On hold', '', 'site interview', '', 'fas fa-home', '', '', 'Maadi'),
            ('Insource', 'Active', 'Active site full time', 'site interview', '', 'fas fa-briefcase', '''We are pleased to inform you that you have been recommended to Insource Company for the position of Telesales Agent.\nFull Time Position: "DME Campaign USA"\nCriteria: B2 & above English level\nMax age: 30 years old\nEducation: Grads & Undergrads\nWorking hours: 3:00 pm till 11:00 for girls / 12:00 pm for boys, Saturdays & Sundays are off.\nBenefits: Career path & promotion schemes within 6 months. Weekly & monthly spiffs & bonuses based on performance\nLocation: Nasr city, awel abbas''', '10,000 EGP Net + Commissions up to 40k + 2000 kpis', 'Nasr City'),
            ('LTSM', 'On hold', 'DME Account', 'site interview', '', 'fas fa-chart-line', '', '', 'Cairo'),
            ('Evolve Marketing LLC', 'On hold', '', 'site interview', '', 'fas fa-rocket', '', '', 'Nasr City'),
            ('Total trip', 'On hold', 'telesales account only', 'site interview', '', 'fas fa-plane', '', '', 'Cairo'),
            ('CCS', 'On hold', '', 'online interview', '', 'fas fa-headset', '', '', 'Cairo'),
            ('ATT', 'On hold', 'Dme and solar from site', 'site interview', '', 'fas fa-solar-panel', '', '', 'Cairo'),
            ('Skills', 'On hold', '', 'site interview', '', 'fas fa-lightbulb', '', '', 'Cairo'),
            ('Ilead', 'On hold', 'need also team leader with basic salary 12k + 4 kpis ,,, quality maneger with basic salary 10k +4 kpis', 'site interview', '100%', 'fas fa-graduation-cap', '', '', 'Nasr City'),
            ('ElShaheen Investment', 'On hold', '', 'site interview', '', 'fas fa-chart-pie', '', '', 'New Cairo'),
            ('Norma', 'Active', 'Us & google ads accounts', 'site interview', '70%', 'fas fa-ad', '''We're HIRING now\n*Norma global solutions* I HIRING a telesales agents now\n- work from site\n- from 5pm to 1 am (including 1 hour break)\n- Working Days From 5 to 6 Days Based on account\n- Net salary: From 8k   + 2k kpis\n- Paid Training (5 working days)\nRequirements: English level b2\nUndergrads, gap year and dropouts are welcome to apply\nLocation: Naser city\nFollow Us on: WhatsApp Channel, Facebook, Linkedin''', 'From 8k   + 2k kpis', 'Nasr City'),
            ('propmarts', 'On hold', '', 'site interview', '', 'fas fa-store', '', '', 'Cairo'),
            ('Zodiak', 'On hold', 'DME Account ( must have experience )', 'online interview', '', 'fas fa-star', '', '', 'Cairo'),
            ('TP', 'On hold', 'ACTIVE ( english , french , german , spanish , italian , duetch)', 'site interview', '', 'fas fa-language', '', '', 'Cairo'),
            ('sutherland', 'On hold', 'grad and undergrad ( cairo only )', 'site interview', '', 'fas fa-user-graduate', '', '', 'Cairo'),
            ('Real estate Wfh', 'On hold', '', 'online interview', '', 'fas fa-house-user', '', '', 'Remote'),
            ('Zagcallers', 'Active', 'Dme , real estate', 'site interview', '100%', 'fas fa-phone-volume', '', '', 'Cairo'),
            ('EClerx', 'On hold', '', 'online interview', '', 'fas fa-laptop', '', '', 'Cairo'),
            ('Insource WFH pt', 'On hold', '', 'online interview', '', 'fas fa-laptop-house', '', '', 'Remote'),
            ('Transcom', 'On hold', '', '', '', 'fas fa-truck', '', '', 'Cairo'),
            ('Xeed', 'On hold', '', '', '', 'fas fa-seedling', '', '', 'Cairo'),
            ('Intelcia', 'On hold', '', '', '', 'fas fa-microchip', '', '', 'Cairo'),
            ('Launch pad', 'On hold', '', '', '', 'fas fa-rocket', '', '', 'Cairo'),
            ('Elevate', 'On hold', '', '', '', 'fas fa-arrow-up', '', '', 'Cairo'),
            ('ICEH', 'On hold', '', '', '', 'fas fa-ice-cream', '', '', 'Cairo'),
        ]
        c.executemany('INSERT INTO company (name, status, comments, interview_type, priority_percentage, logo, details, salary, location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', companies)
        conn.commit()

init_db()

unit_c = {
    'name': 'Unit C',
    'manager': 'Nada Adel',
}

@app.route("/")
def home():
    # Fetch performance for all Unit C leaders
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''SELECT t.id, t.name, IFNULL(h.hires, 0) as hires FROM team_leader t LEFT JOIN hiring h ON t.id = h.leader_id WHERE t.id IN (1,2,3,4,5)''')
        leaders = c.fetchall()
        analysis = [
            {
                'name': name,
                'hires': hires,
                'performance': min(hires / 10 * 100, 100)
            } for _, name, hires in leaders
        ]
        chart_labels = [name for _, name, _ in leaders]
        chart_data = [hires for _, _, hires in leaders]
    return render_template("home.html", analysis=analysis, chart_labels=chart_labels, chart_data=chart_data)

@app.route("/units")
def units():
    # Fetch team leaders and their recruiters
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, phone, color FROM team_leader')
        leaders = c.fetchall()
        team_leaders = []
        for id, name, phone, color in leaders:
            c.execute('SELECT name FROM recruiter WHERE leader_id=?', (id,))
            recruiters = [r[0] for r in c.fetchall()]
            team_leaders.append({
                'id': id,
                'name': name,
                'phone': phone,
                'color': color,
                'recruiters': recruiters
            })
    return render_template("units.html", unit_c=unit_c, team_leaders=team_leaders)

@app.route("/companies")
def companies():
    # Fetch all companies from database
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, status, comments, interview_type, priority_percentage, logo, location FROM company ORDER BY name')
        companies = c.fetchall()
        companies_data = [
            {
                'id': id,
                'name': name,
                'status': status,
                'comments': comments,
                'interview_type': interview_type,
                'priority_percentage': priority_percentage,
                'logo': logo,
                'location': location
            } for id, name, status, comments, interview_type, priority_percentage, logo, location in companies
        ]
    return render_template("companies.html", companies=companies_data)

@app.route("/company/<int:company_id>")
def company_detail(company_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, status, comments, interview_type, priority_percentage, logo, details, salary, location FROM company WHERE id=?', (company_id,))
        row = c.fetchone()
        if not row:
            return "Company not found", 404
        company = {
            'id': row[0],
            'name': row[1],
            'status': row[2],
            'comments': row[3],
            'interview_type': row[4],
            'priority_percentage': row[5],
            'logo': row[6],
            'details': row[7],
            'salary': row[8],
            'location': row[9]
        }
    return render_template("company_detail.html", company=company)

@app.route("/edit-company/<int:company_id>", methods=['GET', 'POST'])
def edit_company(company_id):
    if request.method == 'POST':
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            name = request.form.get('name')
            status = request.form.get('status')
            comments = request.form.get('comments')
            interview_type = request.form.get('interview_type')
            priority_percentage = request.form.get('priority_percentage')
            logo = request.form.get('logo')
            details = request.form.get('details')
            salary = request.form.get('salary')
            location = request.form.get('location')
            c.execute('''UPDATE company SET name=?, status=?, comments=?, interview_type=?, priority_percentage=?, logo=?, details=?, salary=?, location=? WHERE id=?''',
                     (name, status, comments, interview_type, priority_percentage, logo, details, salary, location, company_id))
            conn.commit()
            return jsonify({'success': True})
    
    # GET request - return company data
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, status, comments, interview_type, priority_percentage, logo, details, salary, location FROM company WHERE id=?', (company_id,))
        company = c.fetchone()
        if company:
            return jsonify({
                'id': company[0],
                'name': company[1],
                'status': company[2],
                'comments': company[3],
                'interview_type': company[4],
                'priority_percentage': company[5],
                'logo': company[6],
                'details': company[7],
                'salary': company[8],
                'location': company[9]
            })
        return jsonify({'error': 'Company not found'}), 404

@app.route("/add-company", methods=['POST'])
def add_company():
    """Add a new company to the database"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # Get form data
            name = request.form.get('name', '').strip()
            status = request.form.get('status', 'Active')
            comments = request.form.get('comments', '').strip()
            interview_type = request.form.get('interview_type', 'site interview')
            priority_percentage = request.form.get('priority_percentage', '').strip()
            logo = request.form.get('logo', 'fas fa-building').strip()
            details = request.form.get('details', '').strip()
            salary = request.form.get('salary', '').strip()
            location = request.form.get('location', 'Cairo').strip()
            
            # Validate required fields
            if not name:
                return jsonify({'success': False, 'message': 'Company name is required'}), 400
            
            # Insert new company
            c.execute('''
                INSERT INTO company (name, status, comments, interview_type, 
                                   priority_percentage, logo, details, salary, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, status, comments, interview_type, priority_percentage, 
                  logo, details, salary, location))
            
            # Get the new company ID
            company_id = c.lastrowid
            
            conn.commit()
            
            # Return the new company data
            return jsonify({
                'success': True,
                'message': 'Company added successfully!',
                'company': {
                    'id': company_id,
                    'name': name,
                    'status': status,
                    'comments': comments,
                    'interview_type': interview_type,
                    'priority_percentage': priority_percentage,
                    'logo': logo,
                    'details': details,
                    'salary': salary,
                    'location': location
                }
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error adding company: {str(e)}'}), 500

@app.route("/delete-company/<int:company_id>", methods=['POST'])
def delete_company(company_id):
    """Delete a company from the database"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            
            # First check if company exists
            c.execute('SELECT name FROM company WHERE id = ?', (company_id,))
            company = c.fetchone()
            
            if not company:
                return jsonify({'success': False, 'message': 'Company not found'}), 404
            
            # Delete the company
            c.execute('DELETE FROM company WHERE id = ?', (company_id,))
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': f'Company "{company[0]}" deleted successfully!'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting company: {str(e)}'}), 500

@app.route("/refresh-companies")
def refresh_companies():
    """Refresh companies data and return updated list"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('SELECT id, name, status, comments, interview_type, priority_percentage, logo, location FROM company ORDER BY name')
            companies = c.fetchall()
            companies_data = [
                {
                    'id': id,
                    'name': name,
                    'status': status,
                    'comments': comments,
                    'interview_type': interview_type,
                    'priority_percentage': priority_percentage,
                    'logo': logo,
                    'location': location
                } for id, name, status, comments, interview_type, priority_percentage, logo, location in companies
            ]
            return jsonify({'success': True, 'companies': companies_data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error refreshing companies: {str(e)}'}), 500

@app.route("/courses")
def courses():
    return render_template("courses.html")

@app.route("/sync-sheets")
def sync_sheets():
    """Manual sync route to update companies from Google Sheets"""
    try:
        from sheets_integration import sync_companies_from_sheets
        success = sync_companies_from_sheets(DB_PATH)
        
        if success:
            return jsonify({
                'success': True, 
                'message': 'Successfully synced companies from Google Sheets'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Failed to sync from Google Sheets. Check credentials and permissions.'
            }), 500
    except ImportError:
        return jsonify({
            'success': False, 
            'message': 'Google Sheets integration not available. Install gspread and configure credentials.'
        }), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error syncing: {str(e)}'}), 500

@app.route("/sync-status")
def sync_status():
    """Get current sync status"""
    try:
        from sheets_integration import setup_sheets_integration
        client = setup_sheets_integration()
        
        status = {
            'sheets_available': client is not None,
            'last_sync': 'Not available',
            'background_sync_running': False,
            'background_sync_interval': 5
        }
        
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'sheets_available': False,
            'error': str(e)
        })

@app.route("/team-leaders-dashboard")
def team_leaders_dashboard():
    # Fetch all team leaders with their hiring data
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''SELECT t.id, t.name, t.phone, t.color, IFNULL(h.hires, 0) as hires 
                     FROM team_leader t 
                     LEFT JOIN hiring h ON t.id = h.leader_id 
                     WHERE t.id IN (1,2,3,4,5)
                     ORDER BY t.id''')
        leaders_data = c.fetchall()
        
        team_leaders = []
        total_hires = 0
        max_hires = 0
        top_performer = None
        
        for id, name, phone, color, hires in leaders_data:
            performance = min(hires / 10 * 100, 100) if hires > 0 else 0
            leader = {
                'id': id,
                'name': name,
                'phone': phone,
                'color': color,
                'hires': hires,
                'performance': performance
            }
            team_leaders.append(leader)
            total_hires += hires
            
            if hires > max_hires:
                max_hires = hires
                top_performer = {'name': name, 'hires': hires}
        
        # Calculate averages
        total_leaders = len(team_leaders)
        avg_hires = total_hires / total_leaders if total_leaders > 0 else 0
        
        # Prepare chart data
        chart_labels = [leader['name'] for leader in team_leaders]
        chart_data = [leader['hires'] for leader in team_leaders]
    
    return render_template("team_leaders_dashboard.html", 
                         team_leaders=team_leaders,
                         total_leaders=total_leaders,
                         total_hires=total_hires,
                         avg_hires=avg_hires,
                         top_performer=top_performer,
                         chart_labels=chart_labels,
                         chart_data=chart_data)

@app.route("/locations-dashboard")
def locations_dashboard():
    # Fetch all companies and group by location
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, status, comments, interview_type, priority_percentage, logo, location FROM company ORDER BY name')
        companies = c.fetchall()
        locations = {}
        for id, name, status, comments, interview_type, priority_percentage, logo, location in companies:
            if not location:
                location = 'Other'
            if location not in locations:
                locations[location] = []
            locations[location].append({
                'id': id,
                'name': name,
                'status': status,
                'comments': comments,
                'interview_type': interview_type,
                'priority_percentage': priority_percentage,
                'logo': logo
            })
    return render_template("locations_dashboard.html", locations=locations)


@app.route("/team-leader/<int:leader_id>", methods=['GET', 'POST'])
def team_leader_detail(leader_id):
    if leader_id not in [1,2,3,4,5]:
        return "Team Leader not found", 404
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, name, phone, color FROM team_leader WHERE id=?', (leader_id,))
        row = c.fetchone()
        if not row:
            return "Team Leader not found", 404
        leader = {'id': row[0], 'name': row[1], 'phone': row[2], 'color': row[3]}
        # Recruiters
        c.execute('SELECT name FROM recruiter WHERE leader_id=?', (leader_id,))
        recruiters = [r[0] for r in c.fetchall()]
        # Hiring
        c.execute('SELECT hires FROM hiring WHERE leader_id=?', (leader_id,))
        hires_row = c.fetchone()
        hires = hires_row[0] if hires_row else None
        performance = min(hires / 10 * 100, 100) if hires is not None else None
        # Add recruiter
        if request.method == 'POST':
            if 'recruiter_name' in request.form:
                recruiter_name = request.form['recruiter_name'].strip()
                if recruiter_name and len(recruiters) < 10:
                    c.execute('INSERT INTO recruiter (leader_id, name) VALUES (?, ?)', (leader_id, recruiter_name))
                    conn.commit()
                    return redirect(url_for('team_leader_detail', leader_id=leader_id))
            elif 'hires' in request.form:
                try:
                    hires_val = int(request.form['hires'])
                    c.execute('INSERT OR REPLACE INTO hiring (leader_id, hires) VALUES (?, ?)', (leader_id, hires_val))
                    conn.commit()
                    return redirect(url_for('team_leader_detail', leader_id=leader_id))
                except Exception:
                    pass
        # Refresh recruiters after possible add
        c.execute('SELECT name FROM recruiter WHERE leader_id=?', (leader_id,))
        recruiters = [r[0] for r in c.fetchall()]
    return render_template("team_leader_detail.html", leader=leader, unit=unit_c, recruiters=recruiters, performance=performance, hires=hires, max_recruiters=15)

if __name__ == "__main__":
    app.run(debug=True)
