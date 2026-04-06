import random
from datetime import datetime
import json
import os
from typing import Optional, Tuple

BOOKINGS_FILE = "bookings.json"

def load_bookings():
    """Load existing bookings from JSON file"""
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_booking(booking_data):
    """Save booking to JSON file"""
    bookings = load_bookings()
    bookings.append(booking_data)
    
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f, indent=2)
    
    return booking_data

def validate_15_min_interval(time_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that the time is in 15-minute intervals.
    
    Args:
        time_str: Time string in HH:MM format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        hour, minute = map(int, time_str.split(':'))
        
        # Check if minutes are in 15-minute intervals (00, 15, 30, 45)
        if minute % 15 != 0:
            return False, f"Time must be in 15-minute intervals (00, 15, 30, 45). Got: {minute}"
        
        # Validate hour (0-23)
        if hour < 0 or hour > 23:
            return False, f"Hour must be between 00 and 23. Got: {hour}"
        
        return True, None
    except Exception as e:
        return False, f"Invalid time format. Expected HH:MM. Got: {time_str}"

def validate_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, f"Invalid date format. Expected YYYY-MM-DD. Got: {date_str}"

def check_conflicts(date: str, time: str, specialty: str) -> Optional[dict]:
    """
    Check if there's a conflict at the same date, time and specialty.
    
    Args:
        date: Appointment date (YYYY-MM-DD)
        time: Appointment time (HH:MM)
        specialty: Medical specialty
        
    Returns:
        Existing booking dict if conflict exists, None otherwise
    """
    bookings = load_bookings()
    specialty = specialty or "General Practice"
    
    for booking in bookings:
        if (booking.get('appointment_date') == date and 
            booking.get('appointment_time') == time and 
            booking.get('specialty') == specialty):
            return booking
    return None

def book(user_id: str, date: str, time: str, specialty: Optional[str] = None, reason: Optional[str] = None) -> dict:
    """
    Book a medical appointment with conflict checking and 15-minute interval validation.
    
    Args:
        user_id: Unique identifier for the patient
        date: Appointment date (YYYY-MM-DD format)
        time: Appointment time in 15-minute intervals (HH:MM format)
        specialty: Medical specialty (e.g., 'Cardiology', 'Dermatology')
        reason: Reason for visit
    
    Returns:
        Confirmation details or error if validation fails or conflict exists
    """
    print(f"\n🔧 TOOL CALLED: book_appointment")
    print(f"   Patient: {user_id}")
    print(f"   Date: {date}")
    print(f"   Time: {time}")
    print(f"   Specialty: {specialty}")
    print(f"   Reason: {reason}")
    
    # Validate date format
    date_valid, date_error = validate_date(date)
    if not date_valid:
        print(f"   ❌ Invalid date: {date_error}")
        return {
            "error": True,
            "message": date_error,
            "suggestion": "Please provide date in YYYY-MM-DD format (e.g., 2026-01-19)"
        }
    
    # Validate time format and 15-minute interval
    time_valid, time_error = validate_15_min_interval(time)
    if not time_valid:
        print(f"   ❌ Invalid time: {time_error}")
        return {
            "error": True,
            "message": time_error,
            "suggestion": "Available times: 09:00, 09:15, 09:30, 09:45, 10:00, etc."
        }
    
    # Set default specialty
    if not specialty:
        specialty = "General Practice"
    
    # Check for conflicts
    existing = check_conflicts(date, time, specialty)
    if existing:
        conflict_msg = f"Time slot {date} at {time} is already booked for {specialty}"
        print(f"   ⚠️ Conflict detected: {conflict_msg}")
        return {
            "error": True,
            "message": conflict_msg,
            "existing_appointment": existing,
            "suggestion": "Please choose a different time or specialty."
        }
    
    # Generate confirmation number
    confirmation_number = f"APT-{random.randint(10000, 99999)}"
    
    # Create booking data
    booking_data = {
        "confirmation_number": confirmation_number,
        "patient_id": user_id,
        "appointment_date": date,
        "appointment_time": time,
        "specialty": specialty,
        "reason": reason,
        "status": "confirmed",
        "booked_at": datetime.now().isoformat()
    }
    
    # Save the booking
    save_booking(booking_data)
    
    print(f"   ✅ Appointment booked successfully")
    print(f"   Confirmation: {confirmation_number}")
    
    return {
        "message": f"Appointment successfully booked!",
        "confirmation_number": confirmation_number,
        "details": {
            "Patient ID": user_id,
            "Date": date,
            "Time": time,
            "Specialty": specialty,
            "Reason": reason or "General checkup",
            "Status": "Confirmed"
        },
        "instructions": [
            "📝 Please arrive 15 minutes early",
            "🪪 Bring your insurance card and ID",
            "📞 To cancel or reschedule, contact us 24 hours in advance"
        ]
    }
