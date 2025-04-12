from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import random
import string
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def generate_school_year(start_date, end_date):
    school_year = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday to Friday
            school_year.append(current_date)
        current_date += timedelta(days=1)
    return school_year

start_date = datetime.strptime("01/06/24", "%d/%m/%y")
end_date = datetime.strptime("31/05/25", "%d/%m/%y")

school_year = generate_school_year(start_date, end_date)

weekly_timetable = {
    "Subrata Ghosh": {
        "monday": [0, 0, 0, 1, 0, 1, 1, 0, 1],
        "tuesday": [1, 1, 1, 0, 0, 0, 1, 1, 0],
        "wednesday": [0, 1, 1, 1, 1, 1, 0, 1, 1],
        "thursday": [0, 0, 0, 1, 1, 1, 1, 1, 1],
        "friday": [1, 0, 1, 0, 1, 1, 1, 1, 1]
    },
    "Susmita Mukherjee": {
        "monday": [1, 0, 0, 0, 0, 0, 0, 1, 1],
        "tuesday": [0, 0, 1, 0, 0, 0, 0, 0, 1],
        "wednesday": [0, 1, 1, 0, 0, 0, 0, 1, 1],
        "thursday": [0, 0, 0, 0, 0, 0, 0, 1, 1],
        "friday": [0, 0, 0, 1, 0, 0, 1, 1, 1]
    },
    "Swati Chamaria": {
        "monday": [0, 0, 1, 1, 1, 0, 0, 0, 0],
        "tuesday": [1, 1, 1, 1, 1, 0, 0, 0, 0],
        "wednesday": [1, 1, 1, 1, 0, 0, 1, 0, 0],
        "thursday": [0, 1, 1, 0, 0, 0, 1, 0, 0],
        "friday": [0, 1, 1, 1, 0, 0, 1, 1, 1]
    },
    "Suryasubha Banerjee": {
        "monday": [0, 0, 0, 0, 0, 1, 1, 1, 0],
        "tuesday": [0, 0, 1, 1, 1, 0, 1, 1, 0],
        "wednesday": [0, 0, 1, 0, 1, 1, 0, 0, 0],
        "thursday": [1, 0, 0, 1, 1, 1, 0, 0, 0],
        "friday": [0, 0, 0, 0, 0, 0, 0, 1, 1]
    },
    "Runa Ghosh Auddy": {
        "monday": [1, 1, 0, 1, 1, 0, 0, 0, 0],
        "tuesday": [1, 1, 1, 0, 0, 0, 0, 0, 1],
        "wednesday": [1, 1, 0, 1, 0, 0, 0, 0, 0],
        "thursday": [0, 1, 1, 0, 0, 0, 0, 0, 0],
        "friday": [0, 0, 0, 1, 0, 0, 1, 1, 1]
    },    
}

def initialize_yearly_timetable(timetable):
    yearly_timetable = {}
    for teacher, weekly_schedule in timetable.items():
        yearly_timetable[teacher] = {}
        for date in school_year:
            day_name = date.strftime("%A").lower()
            if day_name in weekly_schedule:
                yearly_timetable[teacher][date] = weekly_schedule[day_name][:]
            else:
                yearly_timetable[teacher][date] = [1] * 9
    return yearly_timetable

yearly_student_schedule = initialize_yearly_timetable(weekly_timetable)

bookings = {}

def get_free_teachers_by_period_on_date(date, period):
    period_index = period - 1
    free_teachers = []
    for teacher_name, teacher_schedule in yearly_student_schedule.items():
        if date in teacher_schedule and teacher_schedule[date][period_index] == 0:
            free_teachers.append(teacher_name)
    return free_teachers

def book_period(registration_number, teacher_name, date, period):
    if teacher_name in yearly_student_schedule and date in yearly_student_schedule[teacher_name]:
        period_index = period - 1
        if yearly_student_schedule[teacher_name][date][period_index] == 0:
            yearly_student_schedule[teacher_name][date][period_index] = 2
            if registration_number not in bookings:
                bookings[registration_number] = {}
            booking_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            bookings[registration_number][booking_code] = (teacher_name, date, period)
            return {"message": f"You have booked a lesson with {teacher_name} in period {period} on {date.strftime('%d/%m/%y')}.", "booking_code": booking_code}
        else:
            return {"error": f"Cannot book period {period} on {date.strftime('%d/%m/%y')} for {teacher_name} as it is not a free period."}
    else:
        return {"error": f"Invalid teacher name or date."}

def cancel_period(registration_number, booking_code):
    if registration_number in bookings and booking_code in bookings[registration_number]:
        teacher_name, date, period = bookings[registration_number].pop(booking_code)
        period_index = period - 1
        yearly_student_schedule[teacher_name][date][period_index] = 0
        return {"message": f"You have cancelled the lesson with {teacher_name} in period {period} on {date.strftime('%d/%m/%y')}."}
    else:
        return {"error": "Invalid booking code or no lessons booked with this registration number."}

from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_free_teachers', methods=['POST'])
def get_free_teachers():
    data = request.get_json()
    date = datetime.strptime(data['date'], "%Y-%m-%d")
    period = int(data['period'])
    free_teachers = get_free_teachers_by_period_on_date(date, period)
    return jsonify(free_teachers)

@app.route('/book_period', methods=['POST'])
def book_period_route():
    data = request.get_json()
    registration_number = data['registration_number']
    teacher_name = data['teacher_name']
    date = datetime.strptime(data['date'], "%Y-%m-%d")
    period = int(data['period'])
    result = book_period(registration_number, teacher_name, date, period)
    return jsonify(result)

@app.route('/get_bookings', methods=['POST'])
def get_bookings():
    data = request.get_json()
    registration_number = data['registration_number']
    if registration_number in bookings:
        result = [
            {
                "booking_code": code,
                "teacher_name": booking[0],
                "date": booking[1].strftime('%d/%m/%Y'),
                "period": booking[2]
            }
            for code, booking in bookings[registration_number].items()
        ]
        return jsonify(result)
    else:
        return jsonify([])

@app.route('/cancel_period', methods=['POST'])
def cancel_period_route():
    data = request.get_json()
    registration_number = data['registration_number']
    booking_code = data['booking_code']
    result = cancel_period(registration_number, booking_code)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
