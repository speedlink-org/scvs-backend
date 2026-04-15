from flask import Blueprint, request, jsonify
from ..controllers.admin_controller import list_admins, update_admin, delete_admin, get_certificate_settings, update_certificate_settings
from flasgger import swag_from
from ..models.certificate_setting import CertificateSetting
from flask import Response

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')


# -------------------------
# GET CERTIFICATE SETTINGS
# -------------------------
@admin_bp.get("/certificate-settings")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "Get current certificate template settings",
    "responses": {
        "200": {"description": "Settings retrieved successfully"}
    }
})
def get_certificate_settings_route():
    return get_certificate_settings()

# -------------------------
# UPDATE CERTIFICATE SETTINGS (PATCH)
# -------------------------
@admin_bp.patch("/certificate-settings")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "Partially update certificate template settings",
    "description": "Accepts multipart/form-data (files) or application/json.",
    "consumes": ["multipart/form-data", "application/json"],
    "parameters": [
        {
            "in": "formData",
            "name": "logo",
            "type": "file",
            "description": "Logo image file"
        },
        {
            "in": "formData",
            "name": "signature",
            "type": "file",
            "description": "Signature image file (e.g., Training coordinator file)"
        },
         {
            "in": "formData",
            "name": "signature2",
            "type": "file",
            "description": "Second signature image file (e.g., managing consultant)"
        },
        {
            "in": "formData",
            "name": "signature_name",
            "type": "string",
            "description": "Name of the first signatory (e.g., Training Coordinator)"
        },
        {
            "in": "formData",
            "name": "signature2_name",
            "type": "string",
            "description": "Name of the second signatory (e.g., Managing Consultant)"
        },
        {
            "in": "formData",
            "name": "title_text",
            "type": "string",
            "description": "Certificate title"
        },
        {
            "in": "formData",
            "name": "default_course_summary",
            "type": "string",
            "description": "Default write-up / course summary"
        },
        {
            "in": "formData",
            "name": "footer_text",
            "type": "string",
            "description": "Footer text"
        }
    ],
    "responses": {
        "200": {"description": "Settings updated"},
        "400": {"description": "Invalid input"}
    }
})
def update_certificate_settings_route():
    return update_certificate_settings()


# image display routes (logo / signatures)

@admin_bp.get("/certificate-settings/logo")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "Get certificate logo image",
    "description": "Returns the uploaded logo image (binary). Returns 404 if no logo has been uploaded.",
    "responses": {
        "200": {
            "description": "Logo image",
            "content": {
                "image/jpeg": {"schema": {"type": "string", "format": "binary"}},
                "image/png": {"schema": {"type": "string", "format": "binary"}},
                "image/gif": {"schema": {"type": "string", "format": "binary"}}
            }
        },
        "404": {"description": "Logo not found"}
    }
})
def get_logo():
    settings = CertificateSetting.get_instance()
    if settings.logo_data:
        return Response(settings.logo_data, mimetype=settings.logo_mime)
    return "", 404

@admin_bp.get("/certificate-settings/signature")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "Get first signature image",
    "description": "Returns the uploaded first signature image (binary). Returns 404 if not uploaded.",
    "responses": {
        "200": {
            "description": "Signature image",
            "content": {
                "image/jpeg": {"schema": {"type": "string", "format": "binary"}},
                "image/png": {"schema": {"type": "string", "format": "binary"}},
                "image/gif": {"schema": {"type": "string", "format": "binary"}}
            }
        },
        "404": {"description": "Signature not found"}
    }
})
def get_signature():
    settings = CertificateSetting.get_instance()
    if settings.signature_data:
        return Response(settings.signature_data, mimetype=settings.signature_mime)
    return "", 404

@admin_bp.get("/certificate-settings/signature2")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "Get second signature image",
    "description": "Returns the uploaded second signature image (binary). Returns 404 if not uploaded.",
    "responses": {
        "200": {
            "description": "Second signature image",
            "content": {
                "image/jpeg": {"schema": {"type": "string", "format": "binary"}},
                "image/png": {"schema": {"type": "string", "format": "binary"}},
                "image/gif": {"schema": {"type": "string", "format": "binary"}}
            }
        },
        "404": {"description": "Signature not found"}
    }
})
def get_signature2():
    settings = CertificateSetting.get_instance()
    if settings.signature2_data:
        return Response(settings.signature2_data, mimetype=settings.signature2_mime)
    return "", 404


# -------------------------
# LIST ADMINS
# -------------------------
@admin_bp.get("/list")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "List admins",
    "description": "Returns a paginated list of admins.",
    "parameters": [
        {"in": "query", "name": "page", "type": "integer", "default": 1},
        {"in": "query", "name": "limit", "type": "integer", "default": 10}
    ],
    "responses": {
        "200": {"description": "List of admins returned successfully"}
    }
})
def list_admins_route():
    return list_admins()


# -------------------------
# UPDATE ADMIN
# -------------------------
@admin_bp.put("/<int:admin_id>/edit")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "Update an admin",
    "description": "Updates admin details by admin ID.",
    "consumes": ["application/json"],
    "parameters": [
        {"in": "path", "name": "admin_id", "type": "integer", "required": True},
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "responsibility": {"type": "string"},
                    "year_of_employment": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "Admin updated successfully"},
        "404": {"description": "Admin not found"}
    }
})
def update_admin_route(admin_id):
    return update_admin(admin_id)


# -------------------------
# DELETE ADMIN
# -------------------------
@admin_bp.delete("/<int:admin_id>/delete")
@swag_from({
    "tags": ["Admin Management"],
    "summary": "Delete an admin",
    "description": "Deletes an admin by ID.",
    "parameters": [
        {"in": "path", "name": "admin_id", "type": "integer", "required": True}
    ],
    "responses": {
        "200": {"description": "Admin deleted successfully"},
        "404": {"description": "Admin not found"}
    }
})
def delete_admin_route(admin_id):
    return delete_admin(admin_id)
