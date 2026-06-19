# # utils/qr_generator.py
# import qrcode
# import json
# import io
# from datetime import datetime
# from .google_drive import drive_service

# def generate_certificate_qr(student_name, course_name, certificate_number, issued_at):
#     """Generate QR code and upload to Google Drive"""
    
#     # Format date
#     if hasattr(issued_at, 'isoformat'):
#         issued_at_str = issued_at.isoformat()
#     elif isinstance(issued_at, str):
#         issued_at_str = issued_at
#     else:
#         issued_at_str = datetime.now().date().isoformat()

#     # Create QR data
#     qr_data = {
#         "student_name": student_name,
#         "course_name": course_name,
#         "certificate_number": certificate_number,
#         "issued_at": issued_at_str,
#         "verify_url": f"https://speedlinktraining.com/verify/{certificate_number}"
#     }
    
#     json_str = json.dumps(qr_data)
    
#     # Generate QR code
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(json_str)
#     qr.make(fit=True)
    
#     # Create image
#     img = qr.make_image(fill_color="black", back_color="white")
    
#     # Convert to bytes
#     img_bytes = io.BytesIO()
#     img.save(img_bytes, format='PNG')
#     img_bytes = img_bytes.getvalue()
    
#     # Generate filename
#     filename = f"{certificate_number.replace('/', '_')}.png"
    
#     try:
#         # Upload to Google Drive
#         drive_url = drive_service.upload_file(img_bytes, filename)
#         return drive_url
#     except Exception as e:
#         # If not authenticated, raise an error
#         raise Exception(f"Google Drive not authenticated. Please authenticate first: {str(e)}")


