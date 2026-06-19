from ..models.certificate import Certificate
from ..models.verification_log import VerificationLog
from ..models.certificate_setting import CertificateSetting  # NEW
from ..extensions import db
from flask import request
from datetime import datetime
import base64  # For encoding binary images

def verify_certificate(code):
    try:
        # 1. Find the certificate
        cert = Certificate.query.filter_by(verification_code=code).first()

        ip = request.remote_addr
        status = "VALID" if cert else "INVALID"

        # Log attempt
        log = VerificationLog(
            certificate_id=cert.id if cert else None,
            verified_at=datetime.utcnow(),
            ip_address=ip,
            status=status
        )
        db.session.add(log)
        db.session.commit()

        if not cert:
            return {
                "status": "INVALID",
                "message": "Certificate not found"
            }

        # 2. Load the template for this certificate's course
        #    (creates a default template if none exists for that course)
        settings = CertificateSetting.get_or_create_for_course(cert.course_name)

        # 3. Prepare template data (text and images as base64)
        template_data = {
            "title_text": settings.title_text,
            "Certificate_duration_text": settings.Certificate_duration_text,
            "default_course_summary": settings.default_course_summary,
            "footer_text": settings.footer_text,
            "signature_name": settings.signature_name,
            "signature_holder_position": settings.signature_holder_position,
            "signature2_name": settings.signature2_name,
            "signature2_holder_position": settings.signature2_holder_position,
            # Encode images as base64 (or None if not present)
            "logo": base64.b64encode(settings.logo_data).decode('utf-8') if settings.logo_data else None,
            "logo_mime": settings.logo_mime,
            "logo2": base64.b64encode(settings.logo2_data).decode('utf-8') if settings.logo2_data else None,
            "logo2_mime": settings.logo2_mime,
            "logo3": base64.b64encode(settings.logo3_data).decode('utf-8') if settings.logo3_data else None,
            "logo3_mime": settings.logo3_mime,
            "signature": base64.b64encode(settings.signature_data).decode('utf-8') if settings.signature_data else None,
            "signature_mime": settings.signature_mime,
            "signature2": base64.b64encode(settings.signature2_data).decode('utf-8') if settings.signature2_data else None,
            "signature2_mime": settings.signature2_mime,
        }

        # 4. Return certificate details + template
        return {
            "status": "VALID",
            "certificate": {
                "student_name": f"{cert.student_first_name} {cert.student_last_name}",
                "course_name": cert.course_name,
                "verification_code": cert.verification_code,
                "issued_at": cert.issued_at.strftime("%Y-%m-%d") if cert.issued_at else None,
                "qr_code_url": cert.qr_code_url,
                "year_of_study": cert.year_of_study,
                "course_summary": cert.course_summary
            },
            "template": template_data   # <-- New field with all template content
        }

    except Exception as e:
        db.session.rollback()
        print(f"Verification error: {str(e)}")
        return {
            "status": "ERROR",
            "message": f"Verification failed: {str(e)}"
        }, 500












# from ..models.certificate import Certificate
# from ..models.verification_log import VerificationLog
# from ..extensions import db
# from flask import request
# from datetime import datetime



# def verify_certificate(code):
#     try:
#         # FIX: Remove is_active filter since it doesn't exist in your model
#         cert = Certificate.query.filter_by(
#             verification_code=code
#             # Remove: is_active=True - this field doesn't exist in your Certificate model
#         ).first()

#         ip = request.remote_addr
#         status = "VALID" if cert else "INVALID"

#         # Log attempt
#         log = VerificationLog(
#             certificate_id=cert.id if cert else None,
#             verified_at=datetime.utcnow(),
#             ip_address=ip,
#             status=status
#         )
#         db.session.add(log)
#         db.session.commit()

#         if not cert:
#             return {
#                 "status": "INVALID",
#                 "message": "Certificate not found"
#             }

#         return {
#             "status": "VALID",
#             "certificate": {
#                 "student_name": f"{cert.student_first_name} {cert.student_last_name}",
#                 "course_name": cert.course_name,
#                 "verification_code": cert.verification_code,
#                 "issued_at": cert.issued_at.strftime("%Y-%m-%d") if cert.issued_at else None,
#                 "qr_code_url": cert.qr_code_url,
#                 "year_of_study": cert.year_of_study,
#                 "course_summary": cert.course_summary
#             }
#         }

#     except Exception as e:
#         db.session.rollback()
#         # Print the error for debugging
#         print(f"Verification error: {str(e)}")
#         return {
#             "status": "ERROR",
#             "message": f"Verification failed: {str(e)}"
#         }, 500
    

