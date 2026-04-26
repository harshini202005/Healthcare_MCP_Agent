"""
Database layer for Healthcare MCP Server
Uses Supabase (PostgreSQL) for storing doctors, schedules, and appointments
"""

import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance
    
    def _init_client(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        
        # Use service_role key for admin operations if available, otherwise anon key
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY (or SUPABASE_SERVICE_KEY) must be set in environment. "
                "Get them from https://supabase.com/dashboard/project/_/settings/api"
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    # ============ Doctor Operations ============
    
    def get_doctors(self, specialty: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all doctors or filter by specialty"""
        query = self.client.table("doctors").select("*")
        
        if specialty:
            query = query.eq("specialty", specialty.lower())
        
        response = query.execute()
        return response.data if response.data else []
    
    def get_doctor_by_id(self, doctor_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific doctor by ID"""
        response = self.client.table("doctors").select("*").eq("id", doctor_id).single().execute()
        return response.data if hasattr(response, 'data') else None
    
    def get_doctor_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find a doctor by name (partial match)"""
        # Remove common prefixes and normalize
        normalized_name = name.lower().replace('dr.', '').replace('dr ', '').strip()
        
        # Try exact match first
        response = self.client.table("doctors").select("*").ilike("name", f"%{normalized_name}%").execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        # Try with "Dr. " prefix
        if not normalized_name.startswith('dr'):
            response = self.client.table("doctors").select("*").ilike("name", f"%Dr. {normalized_name}%").execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
        
        return None
    
    def search_doctors(self, search_term: str) -> List[Dict[str, Any]]:
        """Search doctors by name, specialty, or ID"""
        results = []
        
        # Try ID match
        if search_term.startswith('doc_'):
            doctor = self.get_doctor_by_id(search_term)
            if doctor:
                results.append(doctor)
                return results
        
        # Try name match
        normalized = search_term.lower().replace('dr.', '').replace('dr ', '').strip()
        response = self.client.table("doctors").select("*").ilike("name", f"%{normalized}%").execute()
        if response.data:
            results.extend(response.data)
        
        # Try specialty match
        if not results:
            response = self.client.table("doctors").select("*").ilike("specialty", f"%{normalized}%").execute()
            if response.data:
                results.extend(response.data)
        
        return results
    
    def seed_doctors(self):
        """Seed initial doctor data (run once) - requires service_role key"""
        doctors = [
            {"id": "doc_001", "name": "Dr. Sarah Johnson", "specialty": "cardiology", "email": "sarah.j@healthcare.com", "years_experience": 12},
            {"id": "doc_002", "name": "Dr. Michael Chen", "specialty": "cardiology", "email": "michael.c@healthcare.com", "years_experience": 8},
            {"id": "doc_003", "name": "Dr. Emily Davis", "specialty": "dermatology", "email": "emily.d@healthcare.com", "years_experience": 15},
            {"id": "doc_004", "name": "Dr. James Wilson", "specialty": "orthopedics", "email": "james.w@healthcare.com", "years_experience": 10},
            {"id": "doc_005", "name": "Dr. Priya Patel", "specialty": "pediatrics", "email": "priya.p@healthcare.com", "years_experience": 7},
            {"id": "doc_006", "name": "Dr. Robert Brown", "specialty": "general practice", "email": "robert.b@healthcare.com", "years_experience": 20},
            {"id": "doc_007", "name": "Dr. Lisa Anderson", "specialty": "neurology", "email": "lisa.a@healthcare.com", "years_experience": 14},
            {"id": "doc_008", "name": "Dr. David Kim", "specialty": "general practice", "email": "david.k@healthcare.com", "years_experience": 9},
        ]
        
        seeded = 0
        for doctor in doctors:
            try:
                self.client.table("doctors").upsert(doctor).execute()
                seeded += 1
            except Exception as e:
                print(f"   ⚠️  {doctor['name']}: {str(e)[:60]}")
        
        return seeded
    
    # ============ Schedule Operations ============
    
    def get_doctor_schedule(self, doctor_id: str) -> List[Dict[str, Any]]:
        """Get weekly schedule for a doctor"""
        response = self.client.table("doctor_schedules") \
            .select("*") \
            .eq("doctor_id", doctor_id) \
            .order("day_of_week") \
            .execute()
        return response.data if response.data else []
    
    def get_default_schedules(self) -> List[Dict[str, Any]]:
        """Get default schedules for seeding"""
        schedules = []
        default_times = [
            {"day_of_week": 0, "start_time": "09:00", "end_time": "17:00"},  # Monday
            {"day_of_week": 1, "start_time": "09:00", "end_time": "17:00"},  # Tuesday
            {"day_of_week": 2, "start_time": "09:00", "end_time": "17:00"},  # Wednesday
            {"day_of_week": 3, "start_time": "09:00", "end_time": "17:00"},  # Thursday
            {"day_of_week": 4, "start_time": "09:00", "end_time": "17:00"},  # Friday
        ]
        
        doctor_ids = ["doc_001", "doc_002", "doc_003", "doc_004", "doc_005", "doc_006", "doc_007", "doc_008"]
        
        for doctor_id in doctor_ids:
            for schedule in default_times:
                schedules.append({
                    "doctor_id": doctor_id,
                    "day_of_week": schedule["day_of_week"],
                    "start_time": schedule["start_time"],
                    "end_time": schedule["end_time"],
                    "is_available": True
                })
        
        return schedules
    
    def seed_schedules(self):
        """Seed default schedules for all doctors - requires service_role key"""
        schedules = self.get_default_schedules()
        
        seeded = 0
        for schedule in schedules:
            try:
                self.client.table("doctor_schedules").upsert(schedule).execute()
                seeded += 1
            except Exception as e:
                error_msg = str(e)
                if "violates row-level security" in error_msg:
                    pass  # Silently skip RLS errors
                else:
                    print(f"   ⚠️  Schedule error: {error_msg[:60]}")
        
        return seeded
    
    # ============ Appointment Operations ============
    
    def get_appointments(self, doctor_id: Optional[str] = None, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get appointments, optionally filtered by doctor and/or date"""
        query = self.client.table("appointments").select("*")
        
        if doctor_id:
            query = query.eq("doctor_id", doctor_id)
        if date:
            query = query.eq("appointment_date", date)
        
        response = query.order("appointment_time").execute()
        return response.data if response.data else []
    
    def check_doctor_conflict(self, doctor_id: str, date: str, time: str) -> Optional[Dict[str, Any]]:
        """Check if doctor already has an appointment at this time"""
        try:
            response = self.client.table("appointments") \
                .select("*") \
                .eq("doctor_id", doctor_id) \
                .eq("appointment_date", date) \
                .eq("appointment_time", time) \
                .neq("status", "cancelled") \
                .limit(1) \
                .execute()
            
            if response and response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            # If any error (including no rows found), return None (no conflict)
            return None
    
    def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new appointment"""
        response = self.client.table("appointments").insert(appointment_data).execute()
        return response.data[0] if response.data else appointment_data
    
    def get_available_doctors(self, specialty: str, date: str, time: str) -> List[Dict[str, Any]]:
        """Get available doctors for a specific date/time who don't have conflicts"""
        # Get all doctors of this specialty
        doctors = self.get_doctors(specialty)
        
        if not doctors:
            return []
        
        available_doctors = []
        
        for doctor in doctors:
            # Check if doctor already has appointment at this time
            conflict = self.check_doctor_conflict(doctor['id'], date, time)
            
            # Check if it's during their working hours
            weekday = datetime.strptime(date, "%Y-%m-%d").weekday()  # 0=Monday
            
            schedules = self.client.table("doctor_schedules") \
                .select("*") \
                .eq("doctor_id", doctor['id']) \
                .eq("day_of_week", weekday) \
                .eq("is_available", True) \
                .execute()
            
            if not conflict and schedules.data:
                # Check time is within working hours
                for schedule in schedules.data:
                    start = schedule['start_time']
                    end = schedule['end_time']
                    
                    if start <= time <= end:
                        available_doctors.append(doctor)
                        break
        
        return available_doctors


# Global database instance
db = Database()


def get_db() -> Database:
    """Get database instance"""
    return db