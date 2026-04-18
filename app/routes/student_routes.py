from flask import Blueprint
from ..controllers.student_controller import (
    list_students, create_student, update_student, delete_student, import_students_csv, download_sample_student_file
)
from flasgger import swag_from

student_bp = Blueprint("student_bp", __name__, url_prefix="/students")

@student_bp.get("/list")
@swag_from({
    "tags": ["Student Management"],
    "summary": "List students",
    "description": "Returns a paginated list of students with certification status.",
    "parameters": [
        {"in": "query", "name": "page", "type": "integer", "default": 1},
        {"in": "query", "name": "limit", "type": "integer", "default": 10}
    ],
    "responses": {
        "200": {"description": "List of students returned successfully"}
    }
})
def list_students_route():
    return list_students()


@student_bp.post("/create")
@swag_from({
    "tags": ["Student Management"],
    "summary": "Create a student",
    "description": "Creates a student record.",
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
                    "email": {"type": "string"},
                    "phone_number": {"type": "string"},
                    "course_name": {"type": "string"},
                    "year_of_study": {"type": "string"},
                    "program_start_date": {"type": "string"},
                    "program_end_date": {"type": "string"},
                    "photo_url": {"type": "string"}
                },
                "required": ["first_name", "last_name", "email", "course_name"]
            }
        }
    ],
    "responses": {
        "200": {"description": "Student created successfully"},
        "400": {"description": "Validation error"}
    }
})
def create_student_route():
    return create_student()


@student_bp.put("/<int:student_id>/edit")
@swag_from({
    "tags": ["Student Management"],
    "summary": "Update a student",
    "description": "Updates a student record by ID.",
    "consumes": ["application/json"],
    "parameters": [
        {"in": "path", "name": "student_id", "type": "integer", "required": True},
        {"in": "body", "name": "body", "required": True, "schema": {"type": "object"}}
    ],
    "responses": {
        "200": {"description": "Student updated successfully"},
        "404": {"description": "Student not found"}
    }
})
def update_student_route(student_id):
    return update_student(student_id)


@student_bp.delete("/<int:student_id>/delete")
@swag_from({
    "tags": ["Student Management"],
    "summary": "Delete a student",
    "description": "Deletes a student record by ID.",
    "parameters": [
        {"in": "path", "name": "student_id", "type": "integer", "required": True}
    ],
    "responses": {
        "200": {"description": "Student deleted successfully"},
        "404": {"description": "Student not found"}
    }
})
def delete_student_route(student_id):
    return delete_student(student_id)


@student_bp.post("/import")
@swag_from({
    "tags": ["Student Management"],
    "summary": "Import students",
    "description": "Import students in bulk via a CSV file.",
    "consumes": ["multipart/form-data"],
    "parameters": [
        {"in": "formData", "name": "file", "type": "file", "required": True}
    ],
    "responses": {
        "200": {"description": "Students imported successfully"},
        "400": {"description": "Invalid file"}
    }
})
def import_students_route():
    return import_students_csv()



# Then add this new route at the end of the file (or anywhere appropriate):

@student_bp.get("/download-sample")
@swag_from({
    "tags": ["Student Management"],
    "summary": "Download sample import file",
    "description": "Downloads a sample CSV or Excel template for student import. Use this to see the expected format.",
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
                "text/csv": {
                    "schema": {
                        "type": "string", 
                        "format": "binary"
                    }
                },
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                    "schema": {
                        "type": "string", 
                        "format": "binary"
                    }
                }
            }
        },
        "400": {
            "description": "Unsupported file format"
        },
        "500": {
            "description": "Server error (e.g., missing pandas for Excel export)"
        }
    }
})
def download_sample():
    return download_sample_student_file()