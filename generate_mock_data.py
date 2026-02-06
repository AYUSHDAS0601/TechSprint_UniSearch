import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def create_pdf(filename, text_content):
    doc = fitz.open()
    page = doc.new_page()
    
    # Simple formatting
    p = fitz.Point(50, 72)
    page.insert_text(p, text_content, fontsize=12)
    
    output_path = DATA_DIR / filename
    doc.save(str(output_path))
    print(f"Created PDF: {output_path}")

def create_image(filename, text_content):
    img = Image.new('RGB', (800, 600), color='white')
    d = ImageDraw.Draw(img)
    
    # Attempt to load a default font, otherwise default
    try:
        font = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 20)
    except:
        font = ImageFont.load_default()

    d.text((50, 50), text_content, fill=(0, 0, 0)) #, font=font)
    
    output_path = DATA_DIR / filename
    img.save(output_path)
    print(f"Created Image: {output_path}")

# 1. Exam Schedule (PDF)
schedule_text = """
UNIVERSITY FALL SEMESTER EXAM SCHEDULE 2024
Department of Computer Science

Date        | Course Code | Subject                | Time
---------------------------------------------------------------
Oct 15, 2024| CS101       | Intro to Programming   | 10:00 AM
Oct 18, 2024| CS202       | Data Structures (Lab)  | 02:00 PM
Oct 20, 2024| MA101       | Linear Algebra         | 10:00 AM
Oct 25, 2024| CS305       | Database Systems       | 02:00 PM

Note: Students must bring their ID cards. 
CS202 Lab Exam will be held in the Main Computer Center.
"""
create_pdf("exam_schedule.pdf", schedule_text)

# 2. Scholarship Notice (Image - simulates scanned notice)
scholarship_text = """
NOTICE: OBC SCHOLARSHIP 2024-25

Applications are invited for the State Merit Scholarship 
for OBC students.

Eligibility:
1. Annual family income must be less than 2 Lakhs.
2. Minimum 75% marks in the previous semester.
3. Must be a resident of the state.

Deadline: November 30th, 2024
Submit forms at the Administrative Block, Room 104.
"""
create_image("obc_scholarship.png", scholarship_text)

# 3. Bus Route (PDF)
bus_text = """
CAMPUS BUS SERVICES - ROUTE INFORMATION

Route A: City Center -> Campus
Stop 1: City Center Mall (7:00 AM)
Stop 2: Railway Station (7:15 AM)
Stop 3: Hostel Block A (7:45 AM)
Stop 4: Main Gate (8:00 AM)

Route B: Campus -> City Center
Leaves Main Gate at 5:00 PM and 6:30 PM.

Emergency Contact: Transport Officer (555-0192)
"""
create_pdf("bus_route.pdf", bus_text)

# 4. Syllabus (PDF)
syllabus_text = """
SYLLABUS: CS101 JAVA PROGRAMMING LAB

Module 1: Basic Syntax, Variables, Data Types
Module 2: Object Oriented Programming (Classes, Objects)
Module 3: Inheritance and Polymorphism
Module 4: Exception Handling
Module 5: File I/O and Collections Framework

Reference Books:
- Head First Java
- Effective Java by Joshua Bloch
"""
create_pdf("java_syllabus.pdf", syllabus_text)

print("\nMock data generation complete!")
