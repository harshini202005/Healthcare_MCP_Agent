"""
Booking management tools for Healthcare MCP Server
Uses Supabase for persistent storage of appointments
"""

import random
from datetime import datetime
import json
import os
from typing import Optional, Tuple
from backend.database import get_db

BOOKINGS_FILE = "bookings.json"  # Kept for backward compatibility/fallback


def load_bookings():
    """Load existing bookings from JSON file (legacy)"""
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r") as f:
            return json.load(f)
    return []


def save_booking(booking_data):
    """Save booking to JSON file (legacy)"""
    bookings = load_bookings()
    bookings.append(booking_data)

    with open(BOOKINGS_FILE, "w") as f:
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
        hour, minute = map(int, time_str.split(":"))

        # Check if minutes are in 15-minute intervals (00, 15, 30, 45)
        if minute % 15 != 0:
            return (
                False,
                f"Time must be in 15-minute intervals (00, 15, 30, 45). Got: {minute}",
            )

        # Validate hour (0-23)
        if hour < 0 or hour > 23:
            return False, f"Hour must be between 00 and 23. Got: {hour}"

        return True, None
    except Exception as e:
        return False, f"Invalid time format. Expected HH:MM. Got: {time_str}"


def validate_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """Validate date format (YYYY-MM-DD) and ensure it is not in the past."""
    try:
        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return False, f"Invalid date format. Expected YYYY-MM-DD. Got: {date_str}"

    today = datetime.now().date()
    if appointment_date < today:
        return (
            False,
            f"Cannot book an appointment in the past. Provided date: {date_str}, today is: {today.isoformat()}",
        )

    return True, None


def validate_business_hours(time_str: str) -> Tuple[bool, Optional[str]]:
    """Validate that the appointment is within business hours (08:00 – 17:45)."""
    try:
        hour, minute = map(int, time_str.split(":"))
    except Exception:
        return False, f"Invalid time format. Expected HH:MM. Got: {time_str}"

    total_minutes = hour * 60 + minute
    if total_minutes < 8 * 60:
        return False, "Appointments are available from 08:00 AM. Please choose a later time."
    if total_minutes > 17 * 60 + 45:
        return False, "Appointments are available until 05:45 PM. Please choose an earlier time."

    return True, None


def check_conflicts(
    date: str, time: str, specialty: str, doctor_id: Optional[str] = None
) -> Optional[dict]:
    """
    Check if there's a conflict at the same date, time and specialty/doctor.

    Args:
        date: Appointment date (YYYY-MM-DD)
        time: Appointment time (HH:MM)
        specialty: Medical specialty
        doctor_id: Specific doctor ID (optional)

    Returns:
        Existing booking dict if conflict exists, None otherwise
    """
    db = get_db()

    if doctor_id:
        # Check if specific doctor has conflict
        return db.check_doctor_conflict(doctor_id, date, time)
    else:
        # Check if any doctor in this specialty is available
        available = db.get_available_doctors(specialty, date, time)
        if not available:
            return {"specialty": specialty, "date": date, "time": time}
        return None


def book(
    user_id: str,
    date: str,
    time: str,
    specialty: Optional[str] = None,
    reason: Optional[str] = None,
    doctor_id: Optional[str] = None,
) -> dict:
    """
    Book a medical appointment with conflict checking and 15-minute interval validation.
    Now stores appointments in Supabase database.

    Args:
        user_id: Unique identifier for the patient
        date: Appointment date (YYYY-MM-DD format)
        time: Appointment time in 15-minute intervals (HH:MM format)
        specialty: Medical specialty (e.g., 'Cardiology', 'Dermatology')
        reason: Reason for visit
        doctor_id: Preferred doctor ID (optional - auto-assigned if not provided)

    Returns:
        Confirmation details or error if validation fails or conflict exists
    """
    print(f"\n🔧 TOOL CALLED: book_appointment")
    print(f"   Patient: {user_id}")
    print(f"   Date: {date}")
    print(f"   Time: {time}")
    print(f"   Specialty: {specialty}")
    print(f"   Reason: {reason}")
    print(f"   Preferred Doctor: {doctor_id or 'Auto-assign'}")

    # Set default specialty
    if not specialty:
        specialty = "General Practice"

    # Validate date format
    date_valid, date_error = validate_date(date)
    if not date_valid:
        print(f"   ❌ Invalid date: {date_error}")
        return {
            "error": True,
            "message": date_error,
            "suggestion": "Please provide date in YYYY-MM-DD format (e.g., 2026-01-19)",
        }

    # Validate time format and 15-minute interval
    time_valid, time_error = validate_15_min_interval(time)
    if not time_valid:
        print(f"   ❌ Invalid time: {time_error}")
        return {
            "error": True,
            "message": time_error,
            "suggestion": "Available times: 08:00, 08:15, 08:30 … 17:30, 17:45",
        }

    # Validate business hours
    hours_valid, hours_error = validate_business_hours(time)
    if not hours_valid:
        print(f"   ❌ Outside business hours: {hours_error}")
        return {
            "error": True,
            "message": hours_error,
            "suggestion": "Clinic hours: Monday–Friday, 08:00 AM – 05:45 PM",
        }

    db = get_db()

    # If doctor_id provided, verify they exist and specialize in this area
    if doctor_id:
        doctor = db.get_doctor_by_id(doctor_id)
        if not doctor:
            return {
                "error": True,
                "message": f"Doctor not found: {doctor_id}",
                "suggestion": "Use get_doctors to find valid doctor IDs",
            }

        # Check if doctor specializes in requested specialty
        if doctor["specialty"].lower() != specialty.lower():
            return {
                "error": True,
                "message": f"Dr. {doctor['name']} specializes in {doctor['specialty']}, not {specialty}",
                "suggestion": f"Choose a {specialty} specialist or change specialty to {doctor['specialty']}",
            }

        # Check if doctor is available at this time
        conflict = db.check_doctor_conflict(doctor_id, date, time)
        if conflict:
            return {
                "error": True,
                "message": f"Dr. {doctor['name']} is already booked at {time} on {date}",
                "suggestion": "Use get_available_slots to find open times with this doctor",
            }

        assigned_doctor = doctor
    else:
        # Auto-assign an available doctor
        available_doctors = db.get_available_doctors(specialty, date, time)

        if not available_doctors:
            return {
                "error": True,
                "message": f"No {specialty} doctors available at {time} on {date}",
                "suggestion": "Use get_available_slots to find open appointment times",
            }

        # Pick first available doctor (could implement load balancing here)
        assigned_doctor = available_doctors[0]
        doctor_id = assigned_doctor["id"]

    # Generate confirmation number
    confirmation_number = f"APT-{random.randint(10000, 99999)}"

    # Create booking data
    booking_data = {
        "confirmation_number": confirmation_number,
        "patient_id": user_id,
        "doctor_id": doctor_id,
        "appointment_date": date,
        "appointment_time": time,
        "specialty": specialty,
        "reason": reason,
        "status": "confirmed",
    }

    # Save to Supabase
    try:
        db.create_appointment(booking_data)
        print(f"   ✅ Appointment saved to database")
    except Exception as e:
        print(f"   ⚠️  Database save failed, falling back to JSON: {e}")
        booking_data["booked_at"] = datetime.now().isoformat()
        save_booking(booking_data)

    print(f"   ✅ Appointment booked successfully")
    print(f"   Confirmation: {confirmation_number}")
    print(f"   Assigned Doctor: Dr. {assigned_doctor['name']}")

    return {
        "message": f"Appointment successfully booked with Dr. {assigned_doctor['name']}!",
        "confirmation_number": confirmation_number,
        "details": {
            "Patient ID": user_id,
            "Doctor": assigned_doctor["name"],
            "Doctor ID": doctor_id,
            "Date": date,
            "Time": time,
            "Specialty": specialty,
            "Reason": reason or "General checkup",
            "Status": "Confirmed",
        },
        "instructions": [
            "📝 Please arrive 15 minutes early",
            "🪪 Bring your insurance card and ID",
            "📞 To cancel or reschedule, contact us 24 hours in advance",
        ],
    }


def get_appointment(confirmation_number: str) -> dict:
    """
    Retrieve appointment details by confirmation number

    Args:
        confirmation_number: The confirmation number from booking

    Returns:
        Appointment details or error if not found
    """
    print(f"\n🔧 TOOL CALLED: get_appointment")
    print(f"   Confirmation: {confirmation_number}")

    db = get_db()

    try:
        response = (
            db.client.table("appointments")
            .select("*, doctors(*)")
            .eq("confirmation_number", confirmation_number)
            .single()
            .execute()
        )

        if not response.data:
            return {
                "error": True,
                "message": f"Appointment not found: {confirmation_number}",
                "suggestion": "Check your confirmation number and try again",
            }

        appt = response.data

        return {
            "message": "Appointment found",
            "appointment": {
                "confirmation_number": appt["confirmation_number"],
                "status": appt["status"],
                "patient_id": appt["patient_id"],
                "date": appt["appointment_date"],
                "time": appt["appointment_time"],
                "specialty": appt["specialty"],
                "reason": appt.get("reason", "Not specified"),
                "doctor": {
                    "name": appt.get("doctors", {}).get("name", "Unknown"),
                    "specialty": appt.get("doctors", {}).get("specialty", "Unknown"),
                },
                "booked_at": appt.get("booked_at"),
            },
        }

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"error": True, "message": f"Failed to retrieve appointment: {str(e)}"}


def cancel_appointment(confirmation_number: str, reason: Optional[str] = None) -> dict:
    """
    Cancel an existing appointment

    Args:
        confirmation_number: The confirmation number
        reason: Optional cancellation reason

    Returns:
        Cancellation confirmation
    """
    print(f"\n🔧 TOOL CALLED: cancel_appointment")
    print(f"   Confirmation: {confirmation_number}")

    db = get_db()

    try:
        # First get the appointment
        response = (
            db.client.table("appointments")
            .select("*")
            .eq("confirmation_number", confirmation_number)
            .single()
            .execute()
        )

        if not response.data:
            return {
                "error": True,
                "message": f"Appointment not found: {confirmation_number}",
            }

        # Update status to cancelled
        db.client.table("appointments").update(
            {"status": "cancelled", "notes": reason or "Cancelled by patient"}
        ).eq("confirmation_number", confirmation_number).execute()

        print(f"   ✅ Appointment cancelled")

        return {
            "message": "Appointment successfully cancelled",
            "confirmation_number": confirmation_number,
            "refund_policy": "Refund will be processed within 5-7 business days",
        }

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"error": True, "message": f"Failed to cancel appointment: {str(e)}"}