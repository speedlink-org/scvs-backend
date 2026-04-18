from flask import Response, request, jsonify
from sqlalchemy.orm import joinedload
from ..extensions import db
from ..models.certificate import Certificate
from ..models.student import Student
from ..utils.certificate_number import generate_certificate_number
from ..utils.qr_generator import generate_certificate_qr
import csv
from io import StringIO
import pandas as pd
from io import BytesIO, StringIO
from datetime import datetime
import re
from ..utils.google_drive_simple import drive_service 
import os

# Helper function to extract Google Drive file ID
def extract_file_id_from_url(url):
    """Extract file ID from Google Drive URL"""
    if not url:
        return None
    
    patterns = [
        r'id=([\w-]+)',  # For uc?export=view&id=...
        r'/d/([\w-]+)',   # For /d/file_id/view
        r'/file/d/([\w-]+)'  # For /file/d/file_id
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


# ===================================
# CREATE CERTIFICATE
# ===================================

def create_certificate():
    data = request.get_json()

    # New: accept full_name or first_name+last_name
    full_name = data.get("full_name")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    
    # Validate: either full_name or (first_name and last_name) must be provided
    if not full_name and (not first_name or not last_name):
        return jsonify({"error": "Either full_name or both first_name and last_name are required"}), 400

    # If full_name is given, split into first/last (simple)
    if full_name:
        # Split on first space: e.g., "John Doe" -> first="John", last="Doe"
        parts = full_name.strip().split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        # Also keep the original full_name for storage
    else:
        # Build full_name from first and last
        full_name = f"{first_name} {last_name}".strip()

    course_name = data.get("course_name")
    course_summary = data.get("course_summary")
    year_of_study = data.get("year_of_study")
    issuance_date_str = data.get("issuance_date")
    
    # Parse issuance_date (same as before)
    if issuance_date_str:
        try:
            issuance_date = datetime.strptime(issuance_date_str, '%Y-%m-%d').date()
        except ValueError:
            try:
                issuance_date = datetime.strptime(issuance_date_str, '%d/%m/%Y').date()
            except ValueError:
                issuance_date = datetime.now().date()
    else:
        issuance_date = datetime.now().date()

    # Find or create student using email or full_name
    student = None
    if email:
        student = Student.query.filter_by(email=email).first()
    if not student and full_name:
        # Try to find by full_name (case-insensitive)
        student = Student.query.filter(
            db.func.lower(Student.full_name) == db.func.lower(full_name)
        ).first()
    if not student and first_name and last_name:
        student = Student.query.filter_by(first_name=first_name, last_name=last_name).first()
    
    # Create student if not exists
    if not student:
        # Generate a default email if none provided
        if not email:
            email = f"{first_name.lower()}.{last_name.lower()}@Speedlinkng.com"
        student = Student(
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            email=email,
            phone_number=data.get("phone_number"),
            course_name=course_name,
            year_of_study=year_of_study
        )
        db.session.add(student)
        db.session.flush()

    # Generate certificate number and QR
    certificate_number = generate_certificate_number(course_name, issuance_date)
    qr_url = generate_certificate_qr(full_name, course_name, certificate_number, issuance_date)

    cert = Certificate(
        student_id=student.id,
        student_first_name=first_name,
        student_last_name=last_name,
        student_full_name=full_name,   # NEW
        course_name=course_name,
        course_summary=course_summary,
        year_of_study=year_of_study,
        verification_code=certificate_number,
        qr_code_url=qr_url,
        issued_at=issuance_date,
    )

    db.session.add(cert)
    db.session.commit()

    return jsonify({
        "message": "Certificate created successfully",
        "certificate_number": certificate_number,
        "student_id": student.id,
        "student_full_name": full_name,
        "qr_code_url": qr_url
    }), 201


# def create_certificate():
#     data = request.get_json()

#     first_name = data.get("first_name")
#     last_name = data.get("last_name")
#     course_name = data.get("course_name")
#     course_summary = data.get("course_summary")
#     year_of_study = data.get("year_of_study")
#     issuance_date_str = data.get("issuance_date")  # This comes as string from frontend
    
#     # Convert issuance_date string to date object
#     if issuance_date_str:
#         try:
#             # Handle different date formats (YYYY-MM-DD, DD/MM/YYYY, etc.)
#             issuance_date = datetime.strptime(issuance_date_str, '%Y-%m-%d').date()
#         except ValueError:
#             try:
#                 issuance_date = datetime.strptime(issuance_date_str, '%d/%m/%Y').date()
#             except ValueError:
#                 # If parsing fails, use current date
#                 issuance_date = datetime.now().date()
#     else:
#         # If no date provided, use current date
#         issuance_date = datetime.now().date()

#     # NEW: Find or create student
#     student = Student.query.filter_by(
#         first_name=first_name,
#         last_name=last_name,
#         email=data.get("email")  # You might want to add email to your form
#     ).first()
    
#     # If student doesn't exist, create one
#     if not student:
#         student = Student(
#             first_name=first_name,
#             last_name=last_name,
#             email=data.get("email", f"{first_name}.{last_name}@Speedlinkng.com"),  # Default email
#             phone_number=data.get("phone_number"),
#             course_name=course_name,
#             year_of_study=year_of_study
#         )
#         db.session.add(student)
#         db.session.flush()  # This gets the student ID without committing

#     # Generate cert number
#     certificate_number = generate_certificate_number(course_name, issuance_date)

#     # Generate QR - now passing date object instead of string
#     full_name = first_name + " " + last_name
#     qr_url = generate_certificate_qr(
#         f"{first_name} {last_name}",
#         course_name,
#         certificate_number,
#         issuance_date  # Now this is a date object, not a string
#     )

#     cert = Certificate(
#         student_id=student.id,  # NEW: Add student_id
#         student_first_name=first_name,  # Keep for backward compatibility
#         student_last_name=last_name,    # Keep for backward compatibility
#         course_name=course_name,
#         course_summary=course_summary,
#         year_of_study=year_of_study,
#         verification_code=certificate_number,
#         # qr_code_url=qr_path,
#         qr_code_url=qr_url,

#         issued_at=issuance_date,  # Use the date object here too
#     )

#     db.session.add(cert)
#     db.session.commit()

#     return jsonify({
#         "message": "Certificate created successfully",
#         "certificate_number": certificate_number,
#         "student_id": student.id,  # NEW: Return student ID
#         "qr_code_url": qr_url
#     }), 201


# ===================================
# PAGINATED LIST (Optimized, no N+1)
# ===================================
def list_certificates():
    certs = Certificate.query.all()
    result = []
    for cert in certs:
        result.append({
            "id": cert.id,
            "student_id": cert.student_id,
            "student_full_name": cert.student_full_name or f"{cert.student_first_name} {cert.student_last_name}",
            "student_first_name": cert.student_first_name,
            "student_last_name": cert.student_last_name,
            "course_name": cert.course_name,
            "verification_code": cert.verification_code,
            "issued_at": cert.issued_at,
        })
    return jsonify(result)

# def list_certificates():
#     # Remove pagination
#     query = Certificate.query.options(
#         joinedload(Certificate.student)
#     ).order_by(Certificate.created_at.desc())

#     # Get all certificates
#     all_certificates = query.all()

#     return jsonify({
#         "certificates": [
#             {
#                 "id": c.id,
#                 "student_id": c.student_id,
#                 "student_name": f"{c.student_first_name} {c.student_last_name}",
#                 "course_name": c.course_name,
#                 "verification_code": c.verification_code,
#                 "issued_at": c.issued_at.strftime("%a, %d %b %Y") if c.issued_at else None,
#                 "qr_code_url": c.qr_code_url,
#                 "student_email": c.student.email if c.student else None,
#                 "year_of_study": c.year_of_study,
#                 "course_summary": c.course_summary
#             }
#             for c in all_certificates
#         ],
#         "count": len(all_certificates)
#     })

# ===================================
# EDIT CERTIFICATE
# ===================================

# ===================================
# EDIT CERTIFICATE (UPDATES ALL FIELDS, NO QR REGENERATION)
# ===================================
def update_certificate(code):
    # Find certificate by verification code
    cert = Certificate.query.filter_by(verification_code=code).first()
    
    if not cert:
        return jsonify({"error": "Certificate not found"}), 404
    
    data = request.get_json()
    
    # Track what changes were made
    changes = {}
    
    # Store old values for comparison
    old_values = {
        "verification_code": cert.verification_code,
        "student_first_name": cert.student_first_name,
        "student_last_name": cert.student_last_name,
        "student_full_name": cert.student_full_name,
        "course_name": cert.course_name,
        "course_summary": cert.course_summary,
        "year_of_study": cert.year_of_study
    }
    
    # 1. Update verification_code if provided
    new_verification_code = data.get("verification_code")
    if new_verification_code and new_verification_code != cert.verification_code:
        # Check if new code already exists for another certificate
        existing = Certificate.query.filter_by(verification_code=new_verification_code).first()
        if existing and existing.id != cert.id:
            return jsonify({
                "error": f"Verification code '{new_verification_code}' already exists for another certificate"
            }), 400
        
        changes["verification_code"] = {
            "from": cert.verification_code,
            "to": new_verification_code
        }
        cert.verification_code = new_verification_code
    
    # Handle name updates: support full_name or first_name/last_name
    new_full_name = data.get("full_name")
    new_first_name = data.get("first_name")
    new_last_name = data.get("last_name")
    
    # If full_name is provided, split it and override first/last
    if new_full_name and new_full_name.strip():
        # Split on first space
        parts = new_full_name.strip().split(' ', 1)
        derived_first = parts[0]
        derived_last = parts[1] if len(parts) > 1 else ""
        # Update first and last if they changed
        if derived_first != cert.student_first_name:
            changes["first_name"] = {
                "from": cert.student_first_name,
                "to": derived_first
            }
            cert.student_first_name = derived_first
        if derived_last != cert.student_last_name:
            changes["last_name"] = {
                "from": cert.student_last_name,
                "to": derived_last
            }
            cert.student_last_name = derived_last
        # Also update the certificate's full_name
        if new_full_name != cert.student_full_name:
            changes["full_name"] = {
                "from": cert.student_full_name,
                "to": new_full_name
            }
            cert.student_full_name = new_full_name
    else:
        # Otherwise, update first_name and last_name individually if provided
        if new_first_name and new_first_name != cert.student_first_name:
            changes["first_name"] = {
                "from": cert.student_first_name,
                "to": new_first_name
            }
            cert.student_first_name = new_first_name
        if new_last_name and new_last_name != cert.student_last_name:
            changes["last_name"] = {
                "from": cert.student_last_name,
                "to": new_last_name
            }
            cert.student_last_name = new_last_name
        # If either first or last changed, recompute full_name
        if new_first_name or new_last_name:
            new_computed_full = f"{cert.student_first_name} {cert.student_last_name}".strip()
            if new_computed_full != cert.student_full_name:
                changes["full_name"] = {
                    "from": cert.student_full_name,
                    "to": new_computed_full
                }
                cert.student_full_name = new_computed_full
    
    # 4. Update course name if provided
    new_course_name = data.get("course_name")
    if new_course_name and new_course_name != cert.course_name:
        changes["course_name"] = {
            "from": cert.course_name,
            "to": new_course_name
        }
        cert.course_name = new_course_name
    
    # 5. Update course summary if provided
    new_course_summary = data.get("course_summary")
    if new_course_summary is not None and new_course_summary != cert.course_summary:
        changes["course_summary"] = {
            "from": cert.course_summary,
            "to": new_course_summary
        }
        cert.course_summary = new_course_summary
    
    # 6. Update year of study if provided
    new_year_of_study = data.get("year_of_study")
    if new_year_of_study and new_year_of_study != cert.year_of_study:
        changes["year_of_study"] = {
            "from": cert.year_of_study,
            "to": new_year_of_study
        }
        cert.year_of_study = new_year_of_study
    
    # 7. Update associated Student record if it exists
    student = cert.student  # relationship from Certificate to Student
    if student:
        student_updated = False
        # Update student's first/last/full name to match the certificate
        if cert.student_first_name != student.first_name:
            student.first_name = cert.student_first_name
            student_updated = True
        if cert.student_last_name != student.last_name:
            student.last_name = cert.student_last_name
            student_updated = True
        if cert.student_full_name != student.full_name:
            student.full_name = cert.student_full_name
            student_updated = True
        # Also update other fields if needed (course_name, year_of_study)
        if new_course_name and new_course_name != student.course_name:
            student.course_name = new_course_name
            student_updated = True
        if new_year_of_study and new_year_of_study != student.year_of_study:
            student.year_of_study = new_year_of_study
            student_updated = True
        
        if student_updated:
            db.session.add(student)
            changes["student_record"] = "Updated to match certificate"
    
    # SKIP QR CODE REGENERATION (as per original)
    # ... (keep the commented block)
    
    db.session.commit()
    
    # Prepare response
    response_data = {
        "success": True,
        "message": "Certificate updated successfully",
        "certificate_id": cert.id,
        "verification_code": cert.verification_code,
        "student_full_name": cert.student_full_name,
        "changes": changes if changes else "No changes made"
    }
    
    if cert.qr_code_url:
        response_data["qr_code_url"] = cert.qr_code_url
        response_data["note"] = "QR code not regenerated during update"
    
    return jsonify(response_data)


# # ===================================
# # EDIT CERTIFICATE (UPDATES ALL FIELDS, NO QR)
# # ===================================
# def update_certificate(code):
#     # Find certificate by verification code
#     cert = Certificate.query.filter_by(verification_code=code).first()
    
#     if not cert:
#         return jsonify({"error": "Certificate not found"}), 404
    
#     data = request.get_json()
    
#     # Track what changes were made
#     changes = {}
    
#     # Store old values for comparison
#     old_values = {
#         "verification_code": cert.verification_code,
#         "student_first_name": cert.student_first_name,
#         "student_last_name": cert.student_last_name,
#         "course_name": cert.course_name,
#         "course_summary": cert.course_summary,
#         "year_of_study": cert.year_of_study
#     }
    
#     # 1. Update verification_code if provided
#     new_verification_code = data.get("verification_code")
#     if new_verification_code and new_verification_code != cert.verification_code:
#         # Check if new code already exists for another certificate
#         existing = Certificate.query.filter_by(verification_code=new_verification_code).first()
#         if existing and existing.id != cert.id:
#             return jsonify({
#                 "error": f"Verification code '{new_verification_code}' already exists for another certificate"
#             }), 400
        
#         changes["verification_code"] = {
#             "from": cert.verification_code,
#             "to": new_verification_code
#         }
#         cert.verification_code = new_verification_code
    
#     # 2. Update student first name if provided
#     new_first_name = data.get("first_name")
#     if new_first_name and new_first_name != cert.student_first_name:
#         changes["first_name"] = {
#             "from": cert.student_first_name,
#             "to": new_first_name
#         }
#         cert.student_first_name = new_first_name
    
#     # 3. Update student last name if provided
#     new_last_name = data.get("last_name")
#     if new_last_name and new_last_name != cert.student_last_name:
#         changes["last_name"] = {
#             "from": cert.student_last_name,
#             "to": new_last_name
#         }
#         cert.student_last_name = new_last_name
    
#     # 4. Update course name if provided
#     new_course_name = data.get("course_name")
#     if new_course_name and new_course_name != cert.course_name:
#         changes["course_name"] = {
#             "from": cert.course_name,
#             "to": new_course_name
#         }
#         cert.course_name = new_course_name
    
#     # 5. Update course summary if provided
#     new_course_summary = data.get("course_summary")
#     if new_course_summary is not None and new_course_summary != cert.course_summary:
#         changes["course_summary"] = {
#             "from": cert.course_summary,
#             "to": new_course_summary
#         }
#         cert.course_summary = new_course_summary
    
#     # 6. Update year of study if provided
#     new_year_of_study = data.get("year_of_study")
#     if new_year_of_study and new_year_of_study != cert.year_of_study:
#         changes["year_of_study"] = {
#             "from": cert.year_of_study,
#             "to": new_year_of_study
#         }
#         cert.year_of_study = new_year_of_study
    
#     # 7. Update student email (if you have this field)
#     # Note: This depends on your model structure
#     # If email is in Certificate model:
#     # new_email = data.get("email")
#     # if new_email and new_email != cert.email:
#     #     changes["email"] = {"from": cert.email, "to": new_email}
#     #     cert.email = new_email
    
#     # SKIP QR CODE REGENERATION - Comment out or remove this block entirely
#     # if (cert.student_first_name != old_values["student_first_name"] or 
#     #     cert.student_last_name != old_values["student_last_name"] or 
#     #     cert.course_name != old_values["course_name"] or
#     #     cert.verification_code != old_values["verification_code"]):
#     #     
#     #     # Delete old QR code from Google Drive
#     #     if cert.qr_code_url and 'google.com' in cert.qr_code_url:
#     #         drive_service.delete_file_by_url(cert.qr_code_url)
#     #     
#     #     # Generate new QR code
#     #     new_qr_url = generate_certificate_qr(
#     #         f"{cert.student_first_name} {cert.student_last_name}",
#     #         cert.course_name,
#     #         cert.verification_code,
#     #         cert.issued_at
#     #     )
#     #     cert.qr_code_url = new_qr_url
    
#     db.session.commit()
    
#     # Prepare response
#     response_data = {
#         "success": True,
#         "message": "Certificate updated successfully",
#         "certificate_id": cert.id,
#         "verification_code": cert.verification_code,
#         "changes": changes if changes else "No changes made"
#     }
    
#     # Only add QR URL if it exists and wasn't regenerated
#     if cert.qr_code_url:
#         response_data["qr_code_url"] = cert.qr_code_url
#         response_data["note"] = "QR code not regenerated during update"
    
#     return jsonify(response_data)

# ===================================
# DELETE CERTIFICATE
# ===================================
def delete_certificate(code):
    cert = Certificate.query.get_or_404(code)

    # Delete QR code from Google Drive
    if cert.qr_code_url and 'google.com' in cert.qr_code_url:
        drive_service.delete_file_by_url(cert.qr_code_url)

    db.session.delete(cert)
    db.session.commit()

    return jsonify({"message": "Certificate deleted successfully"})

def import_certificates_csv():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "File is required"}), 400

    default_course = request.form.get("default_course", "").strip()
    if not default_course:
        return jsonify({"error": "Please provide a 'default_course' parameter"}), 400

    default_year = request.form.get("default_year", "2026").strip()

    filename = file.filename.lower()
    created_count = 0
    errors = []
    rows = []   # will hold the parsed data
    detected_columns = {}

    # ---------- Helper to find column ----------
    def find_column(patterns, default=None):
        available = list(rows[0].keys()) if rows else []
        for col in available:
            col_lower = col.lower().strip()
            for pat in patterns:
                if pat in col_lower:
                    return col
        return default

    try:
        # ---------- Read file (CSV or Excel) ----------
        if filename.endswith('.csv'):
            # Save temporarily to handle encoding
            filepath = os.path.join("tmp", file.filename)
            os.makedirs("tmp", exist_ok=True)
            file.save(filepath)

            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
            data = None
            for enc in encodings:
                try:
                    with open(filepath, 'r', encoding=enc) as f:
                        data = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            if data is None:
                return jsonify({"error": "Could not decode CSV file"}), 400

            # Detect delimiter
            delimiter = ',' if ',' in data[:1000] else '\t' if '\t' in data[:1000] else ';'
            stream = StringIO(data)
            reader = csv.DictReader(stream, delimiter=delimiter)
            rows = list(reader)
            os.remove(filepath)

        elif filename.endswith(('.xlsx', '.xls')):
            import pandas as pd
            df = pd.read_excel(file)
            rows = df.replace({pd.NA: None, float('nan'): None}).to_dict('records')
        else:
            return jsonify({"error": "Unsupported file format. Use CSV or Excel."}), 400

        if not rows:
            return jsonify({"error": "No data found in file"}), 400

        # ---------- Detect column names ----------
        name_col = find_column(['name', 'full', 'student', 'names'], rows[0].keys()[0] if rows else None)
        phone_col = find_column(['phone', 'mobile', 'contact', 'phoneno'], None)
        cert_col = find_column(['certificate', 'cert', 'code', 'number', 'certificate code'], None)

        detected_columns = {
            "name_column": name_col,
            "phone_column": phone_col,
            "certificate_column": cert_col,
            "used_default_course": default_course,
            "used_default_year": default_year
        }

        if not name_col:
            return jsonify({"error": "No name column found", "detected_columns": detected_columns}), 400
        if not cert_col:
            return jsonify({"error": "No certificate code column found", "detected_columns": detected_columns}), 400

        # ---------- Process each row ----------
        for idx, row in enumerate(rows, start=1):
            try:
                full_name = str(row.get(name_col, '')).strip()
                if not full_name:
                    errors.append(f"Row {idx}: empty name")
                    continue

                cert_num = str(row.get(cert_col, '')).strip()
                if not cert_num:
                    # Generate a new certificate number if not provided
                    cert_num = generate_certificate_number(default_course, datetime.now().date())
                else:
                    # Check for duplicate
                    existing = Certificate.query.filter_by(verification_code=cert_num).first()
                    if existing:
                        errors.append(f"Row {idx}: Certificate number '{cert_num}' already exists for {existing.student_full_name}")
                        continue

                # Split full name into first/last
                parts = full_name.split(maxsplit=1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ""

                # Phone (optional)
                phone = str(row.get(phone_col, '')).strip() if phone_col else None
                if phone in ('', 'None'): phone = None

                # Find or create student
                student = Student.query.filter(
                    (Student.full_name == full_name) |
                    (Student.first_name == first_name and Student.last_name == last_name)
                ).first()

                if not student:
                    # Generate unique email
                    base_email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@speedlinkng.com"
                    email = base_email
                    counter = 1
                    while Student.query.filter_by(email=email).first():
                        email = f"{base_email.split('@')[0]}{counter}@speedlinkng.com"
                        counter += 1

                    student = Student(
                        first_name=first_name,
                        last_name=last_name,
                        full_name=full_name,
                        email=email,
                        phone_number=phone,
                        course_name=default_course,
                        year_of_study=default_year
                    )
                    db.session.add(student)
                    db.session.flush()  # get student.id

                    # Generate student_id (if you have that function)
                    try:
                        from ..utils.student_id_generator import generate_student_id
                        student.student_id = generate_student_id(default_year, default_course)
                    except ImportError:
                        # Fallback: generate a simple ID
                        student.student_id = f"STU/{default_year}/{student.id:04d}"

                # Create certificate (no QR code)
                cert = Certificate(
                    student_id=student.id,
                    student_first_name=first_name,
                    student_last_name=last_name,
                    student_full_name=full_name,
                    course_name=default_course,
                    course_summary=f"Certificate for {default_course}",
                    year_of_study=default_year,
                    verification_code=cert_num,
                    qr_code_url=None,          # Not generating QR anymore
                    issued_at=datetime.now().date()
                )
                db.session.add(cert)
                created_count += 1

            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
                continue

        db.session.commit()
        return jsonify({
            "message": f"Imported {created_count} certificates",
            "errors": errors,
            "detected_columns": detected_columns
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500



# def import_certificates_csv():
#     file = request.files.get("file")

#     if not file:
#         return jsonify({"error": "File is required"}), 400

#     filename = file.filename.lower()
#     created_count = 0
#     errors = []

#     try:
#         # Handle CSV files
#         if filename.endswith('.csv'):
#             file_content = file.read()
#             encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
#             decoded_content = None
            
#             for encoding in encodings:
#                 try:
#                     decoded_content = file_content.decode(encoding)
#                     break
#                 except UnicodeDecodeError:
#                     continue
            
#             if decoded_content is None:
#                 return jsonify({"error": "Unable to decode CSV file. Try saving as UTF-8."}), 400
            
#             stream = StringIO(decoded_content)
            
#             # Try different delimiters
#             sample = decoded_content[:1000]
#             delimiter = ',' if ',' in sample else '\t' if '\t' in sample else ';'
            
#             csv_reader = csv.DictReader(stream, delimiter=delimiter)
#             rows = list(csv_reader)

#         # Handle Excel files
#         elif filename.endswith(('.xlsx', '.xls')):
#             df = pd.read_excel(file)
#             rows = df.replace({pd.NA: None, float('nan'): None}).to_dict('records')
        
#         else:
#             return jsonify({"error": "Unsupported file format."}), 400

#         if not rows:
#             return jsonify({"error": "No data found in file"}), 400

#         # Auto-detect column mapping
#         first_row = rows[0]
#         available_columns = list(first_row.keys())
        
#         print(f"Available columns: {available_columns}")
#         print(f"First row: {first_row}")

#         # Auto-detect name column
#         name_column = None
#         for col in available_columns:
#             col_lower = col.lower().strip()
#             if any(keyword in col_lower for keyword in ['name', 'student', 'full']):
#                 name_column = col
#                 break
#         if not name_column and available_columns:
#             name_column = available_columns[0]

#         # Auto-detect course column
#         course_column = None
#         for col in available_columns:
#             col_lower = col.lower().strip()
#             if any(keyword in col_lower for keyword in ['department', 'course', 'program', 'dept']):
#                 course_column = col
#                 break
#         if not course_column and len(available_columns) > 1:
#             course_column = available_columns[1]

#         # Auto-detect certificate column
#         cert_column = None
#         for col in available_columns:
#             col_lower = col.lower().strip()
#             if any(keyword in col_lower for keyword in ['certificate', 'cert', 'number', 'no', 'code']):
#                 cert_column = col
#                 break
#         if not cert_column and len(available_columns) > 2:
#             cert_column = available_columns[2]

#         print(f"Detected columns - Name: {name_column}, Course: {course_column}, Cert: {cert_column}")

#         # Process rows
#         for index, row in enumerate(rows, 1):
#             try:
#                 full_name = str(row.get(name_column, '')).strip() if name_column else ''
#                 course_name = str(row.get(course_column, '')).strip() if course_column else ''
#                 cert_num = str(row.get(cert_column, '')).strip() if cert_column else ''

#                 if not full_name:
#                     errors.append(f"Row {index}: No name found in column '{name_column}'")
#                     continue
#                 if not course_name:
#                     errors.append(f"Row {index}: No course found in column '{course_column}'")
#                     continue

#                 # Parse name
#                 name_parts = full_name.split()
#                 first_name = name_parts[0] if name_parts else "Unknown"
#                 last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else "Student"

#                 # Generate certificate number if not provided
#                 if not cert_num:
#                     cert_num = generate_certificate_number(course_name)
#                 else:
#                     # FIX: Check if certificate with this number already exists
#                     existing_cert = Certificate.query.filter_by(verification_code=cert_num).first()
#                     if existing_cert:
#                         errors.append(f"Row {index}: Certificate number '{cert_num}' already exists for student '{existing_cert.student_first_name} {existing_cert.student_last_name}'. Skipping.")
#                         continue

#                 # Generate QR
#                 qr_path = generate_certificate_qr(
#                     full_name,
#                     course_name,
#                     cert_num,
#                     datetime.now().date()
#                 )

#                 # Find or create student
#                 student = Student.query.filter_by(
#                     first_name=first_name,
#                     last_name=last_name,
#                     course_name=course_name
#                 ).first()

#                 if not student:
#                     # Create a unique email
#                     base_email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@speedlinkng.com"
#                     email = base_email
#                     counter = 1
                    
#                     # Ensure unique email
#                     while Student.query.filter_by(email=email).first():
#                         email = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}{counter}@speedlinkng.com"
#                         counter += 1
                    
#                     student = Student(
#                         first_name=first_name,
#                         last_name=last_name,
#                         email=email,
#                         course_name=course_name,
#                         year_of_study="2025"
#                     )
#                     db.session.add(student)
#                     db.session.flush()

#                 # FIX: Double-check certificate doesn't exist (in case of race condition)
#                 existing_cert_final = Certificate.query.filter_by(verification_code=cert_num).first()
#                 if existing_cert_final:
#                     errors.append(f"Row {index}: Certificate number '{cert_num}' already exists. Skipping.")
#                     continue

#                 # Create certificate
#                 cert = Certificate(
#                     student_id=student.id,
#                     student_first_name=first_name,
#                     student_last_name=last_name,
#                     course_name=course_name,
#                     course_summary=f"Certificate for {course_name}",
#                     year_of_study="2025",
#                     verification_code=cert_num,
#                     qr_code_url=qr_path,
#                     issued_at=datetime.now().date()
#                 )

#                 db.session.add(cert)
#                 created_count += 1

#             except Exception as e:
#                 errors.append(f"Row {index}: {str(e)}")
#                 continue

#         db.session.commit()

#         return jsonify({
#             "message": "File processed successfully",
#             "imported": created_count,
#             "errors": errors,
#             "total_rows": len(rows),
#             "detected_columns": {
#                 "name_column": name_column,
#                 "course_column": course_column, 
#                 "cert_column": cert_column
#             }
#         })

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": f"Failed to process file: {str(e)}"}), 500


# Add this to your certificate_controller.py file

# ===================================
# DOWNLOAD SAMPLE CERTIFICATE FILE
# ===================================
def download_sample_certificate_file():
    """Generate and download a sample CSV/Excel template for certificate import"""
    
    file_format = request.args.get('format', 'csv').lower()
    
    # Sample data for certificate import
    sample_data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+2348012345678",
            "course_name": "Web Development",
            "course_summary": "Completed full stack web development course",
            "year_of_study": "2024",
            "issuance_date": "2024-12-15"
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone_number": "+2348123456789",
            "course_name": "Data Science",
            "course_summary": "Successfully completed data science bootcamp",
            "year_of_study": "2024",
            "issuance_date": "2024-11-20"
        },
        {
            "first_name": "Michael",
            "last_name": "Johnson",
            "email": "michael.j@example.com",
            "phone_number": "+2348234567890",
            "course_name": "UI/UX Design",
            "course_summary": "Mastered user interface and user experience design",
            "year_of_study": "2025",
            "issuance_date": "2025-01-10"
        }
    ]
    
    # filename = f"certificate_import_template.{file_format}"
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"certificate_import_template_{timestamp}.{file_format}"
    
    if file_format == 'csv':
        # Create CSV
        output = StringIO()
        if sample_data:
            fieldnames = sample_data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)
        
        # Create response
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv'
            }
        )
        return response
        
    elif file_format in ['xlsx', 'excel']:
        # Create Excel file
        df = pd.DataFrame(sample_data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Certificates', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Certificates']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Create response
        response = Response(
            output.read(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
        )
        return response
    
    else:
        return jsonify({"error": "Unsupported file format. Use 'csv' or 'xlsx'"}), 400
