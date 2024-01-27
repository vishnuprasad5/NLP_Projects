from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import dbmanagement

app = FastAPI()

@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    if intent == 'check.appointment - Checking':
        return check_appointment(parameters)
    if intent == 'new.appointment - Availability check':
        return check_availability(parameters)
    if intent == 'new.appointment - Booking':
        return book_appointment(output_contexts)
    if intent == 'cancel.appointment - cancel':
        return cancel_appointment(parameters)
    if intent == 'consultation.result - results':
        return result_consultation(parameters)


def check_availability(parameters: dict):
    doctor_name = parameters.get("doctors")
    date_time = parameters.get("date-time")
    specialization = parameters.get("specialization")

    availability_result = dbmanagement.get_check_availability(doctor_name, date_time, specialization)

    response_dict = {}

    if availability_result["available"]:
        response_dict["fulfillmentText"] = "Thank you for providing the details. The doctor is available at the requested time. " \
                                           "To proceed with the appointment booking, I kindly request some information from you. " \
                                           "Could you please provide the following details: " \
                                           "1. Full Name, 2. Age, 3. Contact Number. " \
                                           "Feel free to share any additional information or preferences that might be relevant " \
                                           "to ensure a smooth booking process. Your cooperation is much appreciated."
    else:
        response_dict["fulfillmentText"] = "I appreciate your request, but it seems the doctor is not available " \
                                           "at the requested time. " \
                                           "However, here are some alternative available time slots:\n" + "\n".join(
            availability_result["available_slots"])

    if availability_result.get("specialization"):
        response_dict["specialization"] = availability_result['specialization']

    json_response = JSONResponse(content=response_dict)

    return json_response


def book_appointment(output_contexts: list):
    try:
        for context in output_contexts:
            if 'newappointment-followup' in context['name']:
                context_parameters = context['parameters']
                patient_name = context_parameters['person']['name']
                patient_age = context_parameters['age'][0]['amount']
                phone_number = context_parameters['phone-number']

                date_time_str = context_parameters['date-time'][0]['date_time']
                appointment_datetime = datetime.fromisoformat(date_time_str)

                doctor_name = context_parameters.get('doctors')
                specialization = context_parameters.get('specialization')

                booking_result = dbmanagement.get_book_appointment(patient_name, patient_age, phone_number,
                                                                   doctor_name, specialization, appointment_datetime)

                if booking_result["confirm"]:
                    fulfillment_text = (
                        f"Booking successful! Your appointment ID is {booking_result['appointment_id']}. "
                        f"You are scheduled to meet {booking_result['doctor_name']} ({booking_result['specialization']}) "
                        f"on {booking_result['date']} at {booking_result['start_time']}."
                    )
                else:
                    fulfillment_text = "Booking failed. Please try again."

            return JSONResponse(content={
                    "fulfillmentText": fulfillment_text
                })

        return "Appointment context not found."

    except Exception as e:
        print(f"Error booking appointment: {e}")
        return "Error booking appointment. Please try again."

def check_appointment(parameters: dict):
    try:
        appointment_id = parameters["Appointmentid"]
        appointment_details = dbmanagement.get_appointment_details(appointment_id)
        appointment_id = int(parameters["Appointmentid"])

        if appointment_details:
            appointment_date = appointment_details['AppointmentDate']
            appointment_time = appointment_details['AppointmentTime']
            doctor_name = f"{appointment_details['FirstName']} {appointment_details['LastName']}"

            appointment_time = (datetime.min + appointment_time).time()

            formatted_date = appointment_date.strftime('%A, %B %d, %Y')
            formatted_time = appointment_time.strftime('%I:%M %p')

            fulfillment_text = (
                f"Appointment details for AppointmentID {appointment_id}:\n"
                f"Doctor: {doctor_name}\n"
                f"Date: {formatted_date}\n"
                f"Day: {appointment_date.strftime('%A')}\n"
                f"Time: {formatted_time}\n"
                f"Status: {appointment_details['Status']}"
            )

        else:
            fulfillment_text = f"No appointment found with AppointmentID: {appointment_id}"

    except KeyError:
        fulfillment_text = "Missing 'Appointmentid' parameter"
    except Exception as e:
        print(f"Error in check_appointment: {e}")
        fulfillment_text = "An error occurred while processing the request"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })

def cancel_appointment(parameters: dict):
    try:
        appointment_id = parameters.get("Appointmentid")

        if appointment_id is None:
            raise KeyError("Appointmentid")

        cancellation_result = dbmanagement.get_cancel_appointment(appointment_id)

        if cancellation_result["success"]:
            fulfillment_text = f"Appointment with ID {int(appointment_id)} has been canceled successfully."
        else:
            fulfillment_text = f"Failed to cancel appointment. {cancellation_result['message']}"

    except KeyError:
        fulfillment_text = "Error"
    except Exception as e:
        print(f"Error in cancel_appointment: {e}")
        fulfillment_text = "An error occurred while processing the cancellation request"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def result_consultation(parameters: dict):
    try:
        appointment_id = parameters.get("Appointmentid")

        if appointment_id is None:
            raise KeyError("Appointmentid")

        consultation_result = dbmanagement.get_result_consultation(appointment_id)

        if consultation_result:
            appointment_time = consultation_result.get('AppointmentTime')

            if appointment_time is not None:
                appointment_time = (datetime.min + appointment_time).time()
                formatted_time = appointment_time.strftime('%I:%M %p')
            else:
                formatted_time = "N/A"

            fulfillment_text = (
                f"Diagnosis for Appointment ID {int(appointment_id)} is: {consultation_result.get('Diagnosis', 'N/A')}. "
                f"Medicines prescribed: {consultation_result.get('Medicines', 'N/A')}. "
                f"Remarks: {consultation_result.get('Remarks', 'N/A')}. "
                f"Consultation held on {consultation_result.get('AppointmentDate', 'N/A')} at "
                f"{formatted_time}."
            )
        else:
            fulfillment_text = f"No consultation found for Appointment ID {int(appointment_id)}."

    except KeyError:
        fulfillment_text = "Error: Missing Appointment ID"
    except Exception as e:
        fulfillment_text = f"An error occurred while processing the consultation result: {str(e)}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })