from flask import Blueprint, request, jsonify
from ..controllers.certificate_controller import create_certificate, list_certificates, update_certificate, delete_certificate, import_certificates_csv, download_sample_certificate_file
from flasgger import swag_from


certificate_bp = Blueprint('certificate_bp', __name__, url_prefix='/certificate')

@certificate_bp.post('/create')
@swag_from({
    "tags": ["Certificates"],
    "summary": "Create a certificate",
    "description": "Creates a certificate, generates a verification code and PDF file.",
    "consumes": ["application/json"],
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "full_name": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "course_name": {"type": "string"},
                    "course_summary": {"type": "string"},
                    "year_of_study": {"type": "string"},
                    "issuance_date": {"type": "string", "format": "date", "description": "Date in YYYY-MM-DD format"},
                    "email": {"type": "string"},
                    "phone_number": {"type": "string"}
                },
                "required": ["first_name", "last_name", "course_name"]
            }
        }
    ],
    "responses": {
        "201": {
            "description": "Certificate created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "certificate_number": {"type": "string"},
                    "student_id": {"type": "integer"}
                }
            }
        },
        "400": {"description": "Invalid input"}
    }
})
def create_cert():
    return create_certificate()


@certificate_bp.get("/certificates")
@swag_from({
    "tags": ["Certificates"],
    "summary": "List certificates",
    "description": "Returns a paginated list of certificates.",
    "parameters": [
        {"in": "query", "name": "page", "type": "integer", "default": 1},
        {"in": "query", "name": "limit", "type": "integer", "default": 10}
    ],
    "responses": {
        "200": {"description": "List of certificates returned successfully"}
    }
})
def list_cert():
    return list_certificates()

@certificate_bp.put("/certificates/<path:code>")
@swag_from({
    "tags": ["Certificates"],
    "summary": "Update a certificate",
    "description": "Updates certificate details by certificate ID.",
    "consumes": ["application/json"],
    "parameters": [
        {"in": "path", "name": "cert_id", "type": "integer", "required": True},
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "full_name": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "course_name": {"type": "string"},
                    "course_summary": {"type": "string"},
                    "year_of_study": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        "200": {"description": "Certificate updated successfully"},
        "404": {"description": "Certificate not found"}
    }
})
def update_cert(code):
    return update_certificate(code)


@certificate_bp.delete("/certificates/<path:code>")
@swag_from({
    "tags": ["Certificates"],
    "summary": "Delete a certificate",
    "description": "Deletes a certificate by ID.",
    "parameters": [
        {"in": "path", "name": "cert_id", "type": "integer", "required": True}
    ],
    "responses": {
        "200": {"description": "Certificate deleted successfully"},
        "404": {"description": "Certificate not found"}
    }
})
def delete_cert(code):
    return delete_certificate(code)


@certificate_bp.post("/certificates/import")
@swag_from({
    "tags": ["Certificates"],
    "summary": "Import certificates via CSV or Excel",
    "description": "Uploads a CSV or Excel file containing multiple certificate records and inserts them into the database.",
    "consumes": ["multipart/form-data"],
    "parameters": [
        {
            "in": "formData", 
            "name": "file", 
            "type": "file", 
            "required": True,
            "description": "CSV or Excel file with columns: first_name, last_name, course_name, course_summary, year_of_study, issuance_date"
        }
    ],
    "responses": {
        "200": {
            "description": "File processed successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "imported": {"type": "integer"},
                    "errors": {"type": "array"},
                    "total_rows": {"type": "integer"}
                }
            }
        },
        "400": {"description": "File not provided or invalid format"},
        "500": {"description": "Server error processing file"}
    }
})
def import_csv():
    return import_certificates_csv()


# Add this to your certificate routes file (where the other certificate routes are)

@certificate_bp.get('/download-sample')
@swag_from({
    "tags": ["Certificates"],
    "summary": "Download sample certificate import file",
    "description": "Downloads a sample CSV or Excel template for certificate import",
    "parameters": [
        {
            "in": "query", 
            "name": "format", 
            "type": "string", 
            "enum": ["csv", "xlsx"],
            "default": "csv",
            "description": "File format (csv or xlsx)"
        }
    ],
    "responses": {
        "200": {
            "description": "Sample file downloaded successfully",
            "content": {
                "text/csv": {"schema": {"type": "string", "format": "binary"}},
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {"schema": {"type": "string", "format": "binary"}}
            }
        },
        "400": {"description": "Unsupported file format"}
    }
})
def download_sample_cert():
    return download_sample_certificate_file()