import mysql.connector
global cnx


cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="******",
    database="lifewellchatbot"
)


from datetime import datetime, timedelta

def get_check_availability(doctor_name, date_time, specialization):
    try:
        cursor = cnx.cursor()

        doctor_id = None
        specialization_id = None
        start_time = None
        end_time = None

        if doctor_name or specialization:
            query_doctor = ("SELECT DoctorID, Specialization, StartTime, EndTime FROM Doctors "
                            "WHERE CONCAT(FirstName, ' ', LastName) = %s OR Specialization = %s")

            cursor.execute(query_doctor, (doctor_name, specialization))
            doctor_result = cursor.fetchone()

            if doctor_result and len(doctor_result) == 4:
                doctor_id, specialization_id, start_time, end_time = doctor_result
            else:
                return {"available": False, "available_slots": []}
        else:
            return {"available": False, "available_slots": []}

        date_time_str = date_time[0]['date_time']

        dt_object = datetime.fromisoformat(date_time_str)

        appointment_time = dt_object.time()

        start_time = (datetime.min + start_time).time()
        end_time = (datetime.min + end_time).time()

        if start_time <= appointment_time <= end_time:
            return {
                "available": True,
                "specialization": specialization_id
            }
        else:
            start_time_str = start_time.strftime('%I:%M %p')
            end_time_str = end_time.strftime('%I:%M %p')

            return {
                "available": False,
                "available_slots": [f'{start_time_str} to {end_time_str}'],
                "specialization": specialization_id
            }

    except Exception as e:
        print(f"Error checking doctor availability: {e}")
        return {"available": False, "available_slots": []}

    finally:
        cursor.close()

def get_book_appointment(patient_name, patient_age, contact_number, doctor_name,specialization, date_time):
    try:
        cursor = cnx.cursor()

        doctor_id = None
        specialization_id = None
        start_time = None
        end_time = None

        if doctor_name or specialization:
            query_doctor = (
                "SELECT DoctorID, Specialization FROM Doctors "
                "WHERE (CONCAT(FirstName, ' ', LastName) = %s OR Specialization = %s)"
            )

            cursor.execute(query_doctor, (doctor_name or specialization, doctor_name or specialization))
            doctor_result = cursor.fetchone()

            if doctor_result:
                doctor_id, specialization_id = doctor_result

        if doctor_id:
            insert_patient_query = ("INSERT INTO Patients (FullName, Age, ContactNumber) "
                                    "VALUES (%s, %s, %s)")

            cursor.execute(insert_patient_query, (patient_name, patient_age, contact_number))
            cnx.commit()

            patient_id = cursor.lastrowid

            insert_appointment_query = ("INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime) "
                                        "VALUES (%s, %s, %s, %s)")

            cursor.execute(insert_appointment_query, (patient_id, doctor_id, date_time.date(), date_time.time()))
            cnx.commit()

            appointment_id = cursor.lastrowid

            doctor_name_query = "SELECT CONCAT(FirstName, ' ', LastName) FROM Doctors WHERE DoctorID = %s"
            cursor.execute(doctor_name_query, (doctor_id,))
            doctor_name_result = cursor.fetchone()
            doctor_name = doctor_name_result[0] if doctor_name_result else None

            specialization_query = "SELECT Specialization FROM Doctors WHERE DoctorID = %s"
            cursor.execute(specialization_query, (doctor_id,))
            specialization_result = cursor.fetchone()
            specialization = specialization_result[0] if specialization_result else None

            start_time_query = "SELECT AppointmentTime FROM Appointments WHERE AppointmentID = %s"
            cursor.execute(start_time_query, (appointment_id,))
            start_time_result = cursor.fetchone()
            start_time = start_time_result[0]
            base_date = datetime(2022, 1, 1)  # Use an arbitrary date as a base
            full_datetime = base_date + start_time

            formatted_time = full_datetime.strftime('%I:%M %p')

            date_query = "SELECT AppointmentDate FROM Appointments WHERE AppointmentID = %s"
            cursor.execute(date_query, (appointment_id,))
            date_result = cursor.fetchone()
            date = date_result[0].strftime('%Y-%m-%d')

            return {
                "confirm": True,
                "appointment_id": appointment_id,
                "doctor_name": doctor_name,
                "specialization": specialization,
                "start_time": formatted_time,
                "date": date
            }

        else:
            return {"confirm": False, "message": "Doctor not found."}

    except Exception as e:
        print(f"Error booking appointment: {e}")
        return "Error booking appointment. Please try again."

    finally:
        cursor.close()

def get_appointment_details(appointment_id):
    try:
        cursor = cnx.cursor(dictionary=True)

        query = '''
            SELECT Doctors.FirstName, Doctors.LastName, Appointments.AppointmentDate,
            Appointments.AppointmentTime, Appointments.Status 
            FROM Appointments 
            JOIN Doctors ON Appointments.DoctorID = Doctors.DoctorID 
            WHERE Appointments.AppointmentID = %s
        '''

        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()

        return result

    except Exception as e:
        print(f"Error in get_appointment_details: {e}")
        return None

    finally:
        cursor.close()

def get_cancel_appointment(appointment_id):
    try:
        with cnx.cursor() as cursor:
            query_check_appointment = "SELECT * FROM Appointments WHERE AppointmentID = %s"
            cursor.execute(query_check_appointment, (appointment_id,))
            existing_appointment = cursor.fetchone()

            if existing_appointment:
                appointment_status = existing_appointment[5]  # Assuming Status is at index 5

                if appointment_status == 'Consulted':
                    return {"success": False, "message": "Cannot cancel a consulted appointment."}

                query_cancel_appointment = "DELETE FROM Appointments WHERE AppointmentID = %s"
                cursor.execute(query_cancel_appointment, (appointment_id,))

                cnx.commit()

                return {"success": True}

            else:
                return {"success": False, "message": "Appointment not found."}

    except Exception as e:
        print(f"Error cancelling appointment: {e}")
        return {"success": False, "message": f"An error occurred during the cancellation process: {str(e)}"}

def get_result_consultation(appointment_id):
    try:
        cursor = cnx.cursor(dictionary=True)

        query = '''
            SELECT Doctors.FirstName, Doctors.LastName, Appointments.AppointmentDate,
            Appointments.AppointmentTime, Consultation.Diagnosis, Consultation.Medicines, Consultation.Remarks
            FROM Appointments 
            JOIN Doctors ON Appointments.DoctorID = Doctors.DoctorID 
            JOIN Consultation ON Appointments.AppointmentID = Consultation.AppointmentID
            WHERE Appointments.AppointmentID = %s
        '''

        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()

        return result

    except Exception as e:
        print(f"Error in get_result_consultation: {e}")
        return None

    finally:
        cursor.close()
