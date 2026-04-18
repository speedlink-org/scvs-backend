from ..models.student import Student
from datetime import datetime

def generate_student_id(year_of_study=None, course_name=None):
    """
    Generate a unique student ID like: STU/25B/DM/0001
    Format: STU/{YearCode}/{CourseCode}/{Sequence}
    """
    # Year code: last two digits of year of study (or current year)
    if year_of_study:
        # Assuming year_of_study like "2025" or "25B"
        year_str = str(year_of_study)[-2:]
    else:
        year_str = datetime.now().strftime("%y")
    
    # Course code: first two letters uppercase (e.g., "DM" for "Data Management")
    course_code = "XX"
    if course_name:
        words = course_name.split()
        if len(words) >= 2:
            course_code = (words[0][0] + words[1][0]).upper()
        else:
            course_code = course_name[:2].upper()
    
    # Prefix: STU
    prefix = "STU"
    
    # Find the next sequence number for this year+course combination
    pattern = f"{prefix}/{year_str}{course_code}/%"
    last_student = Student.query.filter(Student.student_id.like(pattern)).order_by(Student.student_id.desc()).first()
    
    if last_student:
        last_seq = int(last_student.student_id.split('/')[-1])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    
    return f"{prefix}/{year_str}{course_code}/{new_seq:04d}"