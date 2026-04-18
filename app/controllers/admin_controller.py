from ..models.user import User
from ..extensions import db
from flask import jsonify, request
from ..utils.staff_id_generator import generate_staff_id
import os
from werkzeug.utils import secure_filename
from flask import current_app
from ..models.certificate_setting import CertificateSetting
import base64


# Helper to save uploaded file and return its URL
def _save_uploaded_file(file, folder="certificate_assets"):
    if not file:
        return None
    filename = secure_filename(file.filename)
    # Create folder if not exists
    upload_path = os.path.join(current_app.root_path, 'static', folder)
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, filename)
    file.save(file_path)
    # Return URL path (adjust if you serve static files differently)
    return f"/static/{folder}/{filename}"


def get_certificate_settings():
    settings = CertificateSetting.get_instance()
    return jsonify({
        "logo_exists": bool(settings.logo_data),
        "logo_mime": settings.logo_mime,
        "logo2_exists": bool(settings.logo2_data),
        "logo2_mime": settings.logo2_mime,
        "logo3_exists": bool(settings.logo3_data),
        "logo3_mime": settings.logo3_mime,
        "signature_exists": bool(settings.signature_data),
        "signature_mime": settings.signature_mime,
        "signature_name": settings.signature_name,            # NEW
        "signature_holder_position": settings.signature_holder_position,  # NEW
        "signature2_exists": bool(settings.signature2_data),
        "signature2_mime": settings.signature2_mime,
        "signature2_name": settings.signature2_name,          # NEW
        "signature2_holder_position": settings.signature2_holder_position,  # NEW
        "title_text": settings.title_text,
        "Certificate_duration_text": settings.Certificate_duration_text,  # NEW
        "default_course_summary": settings.default_course_summary,
        "footer_text": settings.footer_text,
        "updated_at": settings.updated_at
    })


def update_certificate_settings():
    settings = CertificateSetting.get_instance()
    
    # Handle JSON (text only)
    if request.content_type and 'application/json' in request.content_type:
        data = request.get_json()
        settings.title_text = data.get('title_text', settings.title_text)
        settings.Certificate_duration_text = data.get('Certificate_duration_text', settings.Certificate_duration_text)  # NEW
        settings.default_course_summary = data.get('default_course_summary', settings.default_course_summary)
        settings.footer_text = data.get('footer_text', settings.footer_text)
        # NEW: signature names from JSON
        settings.signature_name = data.get('signature_name', settings.signature_name)
        settings.signature_holder_position = data.get('signature_holder_position', settings.signature_holder_position)  # NEW

        settings.signature2_name = data.get('signature2_name', settings.signature2_name)
        settings.signature2_holder_position = data.get('signature2_holder_position', settings.signature2_holder_position)  # NEW
        db.session.commit()
        return jsonify({"message": "Certificate settings updated", "settings": {
            "title_text": settings.title_text,
            "Certificate_duration_text": settings.Certificate_duration_text,  # NEW
            "default_course_summary": settings.default_course_summary,
            "footer_text": settings.footer_text,
            "signature_name": settings.signature_name,
            "signature_holder_position": settings.signature_holder_position,  # NEW
            "signature2_name": settings.signature2_name,
            "signature2_holder_position": settings.signature2_holder_position  # NEW
        }})
    
    # Handle multipart/form-data for file uploads
    if 'logo' in request.files:
        logo_file = request.files['logo']
        if logo_file and logo_file.filename:
            settings.logo_data = logo_file.read()  # read bytes
            settings.logo_mime = logo_file.mimetype

    if 'logo2' in request.files:
        file = request.files['logo2']
        if file and file.filename:
            settings.logo2_data = file.read()
            settings.logo2_mime = file.mimetype
    
    if 'logo3' in request.files:
        file = request.files['logo3']
        if file and file.filename:
            settings.logo3_data = file.read()
            settings.logo3_mime = file.mimetype
    
    if 'signature' in request.files:
        sig_file = request.files['signature']
        if sig_file and sig_file.filename:
            settings.signature_data = sig_file.read()
            settings.signature_mime = sig_file.mimetype

    # New: second signature
    if 'signature2' in request.files:
        sig2_file = request.files['signature2']
        if sig2_file and sig2_file.filename:
            settings.signature2_data = sig2_file.read()
            settings.signature2_mime = sig2_file.mimetype
    
    # Text fields from form data
    settings.title_text = request.form.get('title_text', settings.title_text)
    settings.Certificate_duration_text = request.form.get('Certificate_duration_text', settings.Certificate_duration_text)  # NEW
    settings.default_course_summary = request.form.get('default_course_summary', settings.default_course_summary)
    settings.footer_text = request.form.get('footer_text', settings.footer_text)
    # NEW: signature names from form data
    settings.signature_name = request.form.get('signature_name', settings.signature_name)
    settings.signature_holder_position = request.form.get('signature_holder_position', settings.signature_holder_position)  # NEW
    settings.signature2_name = request.form.get('signature2_name', settings.signature2_name)
    settings.signature2_holder_position = request.form.get('signature2_holder_position', settings.signature2_holder_position)  # NEW

    
    db.session.commit()
    return jsonify({
        "message": "Certificate settings updated successfully",
        "logo_exists": bool(settings.logo_data),
        "logo2_exists": bool(settings.logo2_data),
        "logo3_exists": bool(settings.logo3_data),
        "signature_exists": bool(settings.signature_data),
        "signature_name": settings.signature_name,
        "signature_holder_position": settings.signature_holder_position,  # NEW
        "signature2_exists": bool(settings.signature2_data),
        "signature2_name": settings.signature2_name,
        "signature2_holder_position": settings.signature2_holder_position,  # NEW
        "certificate_duration_text": settings.Certificate_duration_text,  # NEW
        "title_text": settings.title_text,
        "default_course_summary": settings.default_course_summary,
        "footer_text": settings.footer_text
    })



# -------------------------
# LIST ADMINS (Paginated)
# -------------------------
def list_admins():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    query = User.query.filter_by(role='admin').order_by(User.created_at.desc())
    paginated = query.paginate(page=page, per_page=limit, error_out=False)

    admins = [
        {
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
            "phone_number": u.phone_number,
            "responsibility": u.responsibility,
            "year_of_employment": u.year_of_employment,
            "staff_id": u.staff_id,
            "created_at": u.created_at
        } for u in paginated.items
    ]

    return jsonify({
        "total": paginated.total,
        "page": page,
        "limit": limit,
        "admins": admins
    })


# -------------------------
# UPDATE ADMIN
# -------------------------
def update_admin(admin_id):
    admin = User.query.filter_by(id=admin_id, role='admin').first()
    if not admin:
        return {"message": "Admin not found"}, 404

    data = request.json
    admin.first_name = data.get('first_name', admin.first_name)
    admin.last_name = data.get('last_name', admin.last_name)
    admin.email = data.get('email', admin.email)
    admin.phone_number = data.get('phone_number', admin.phone_number)
    admin.responsibility = data.get('responsibility', admin.responsibility)
    admin.year_of_employment = data.get('year_of_employment', admin.year_of_employment)

    # regenerate staff_id if year changed
    if 'year_of_employment' in data:
        admin.staff_id = generate_staff_id(role='admin', year_of_employment=admin.year_of_employment)

    db.session.commit()

    return {
        "message": "Admin updated successfully",
        "admin": {
            "id": admin.id,
            "first_name": admin.first_name,
            "last_name": admin.last_name,
            "email": admin.email,
            "phone_number": admin.phone_number,
            "responsibility": admin.responsibility,
            "year_of_employment": admin.year_of_employment,
            "staff_id": admin.staff_id,
            "created_at": admin.created_at
        }
    }


# -------------------------
# DELETE ADMIN
# -------------------------
def delete_admin(admin_id):
    admin = User.query.filter_by(id=admin_id, role='admin').first()
    if not admin:
        return {"message": "Admin not found"}, 404

    db.session.delete(admin)
    db.session.commit()

    return {"message": "Admin deleted successfully"}
