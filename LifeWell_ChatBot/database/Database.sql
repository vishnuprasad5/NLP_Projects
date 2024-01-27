CREATE DATABASE LIFEWELLCHATBOT ;

USE LIFEWELLCHATBOT ;

-- Doctors Table

CREATE TABLE Doctors (
    DoctorID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Specialization VARCHAR(255) NOT NULL,
    LicenseNumber VARCHAR(255) NOT NULL,
    ExperienceYears INT,
    StartTime TIME,
    EndTime TIME,
    ConsultationFee INT 
    ) AUTO_INCREMENT = 101 ;

INSERT INTO Doctors (FirstName, LastName, Specialization, LicenseNumber, ExperienceYears, StartTime, EndTime, ConsultationFee) VALUES
    ('Dr. Rajesh', 'Kumar', 'Cardiologist', 'CARD123', 10, '10:00:00', '12:00:00', 300),
    ('Dr. Priya', 'Sharma', 'Dermatologist', 'DERM456', 8, '14:00:00', '16:00:00', 350),
    ('Dr. Amit', 'Patel', 'Gastroenterologist', 'GASTRO789', 12, '16:00:00', '18:00:00', 400),
    ('Dr. Anita', 'Verma', 'General Practitioner', 'GP101', 15, '10:00:00', '13:00:00', 300),
    ('Dr. Vikram', 'Singh', 'Neurologist', 'NEURO202', 11, '14:00:00', '16:00:00', 500),
    ('Dr. Sneha', 'Joshi', 'Ophthalmologist', 'OPHTH567', 9, '16:00:00', '18:00:00', 300),
    ('Dr. Arjun', 'Sharma', 'Pediatrician', 'PEDIATRIC303', 14, '10:00:00', '12:00:00', 350),
    ('Dr. Ananya', 'Gupta', 'Psychologist', 'PSYCH404', 7, '14:00:00', '16:00:00', 400),
    ('Dr. Neha', 'Yadav', 'Gynecologist', 'GYNEC567', 13, '16:00:00', '18:00:00', 450),
    ('Dr. Rahul', 'Verma', 'Orthopedic Surgeon', 'ORTHOPEDIC808', 10, '10:00:00', '12:00:00', 500) ;

SELECT * FROM DOCTORS ;

-- Patient Table

CREATE TABLE Patients (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    FullName VARCHAR(255) NOT NULL,
    Age INT ,
    ContactNumber VARCHAR(20)
) AUTO_INCREMENT = 100001 ;

INSERT INTO Patients (FullName, Age, ContactNumber) VALUES
    ('Rajesh Kumar', 28, '9876543210'),
    ('Priya Sharma', 35, '8765432109'),
    ('Amit Patel', 42, '7654321098');
    
SELECT * FROM PATIENTS ;

-- Appointment Table

CREATE TABLE Appointments (
    AppointmentID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    DoctorID INT NOT NULL,
    AppointmentDate DATE NOT NULL,
    AppointmentTime TIME NOT NULL,
    Status VARCHAR(50) DEFAULT 'Scheduled',
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID)
) AUTO_INCREMENT = 1000001 ;

INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime) VALUES
    (100001, 101, '2023-01-15', '10:00:00'),
	(100002, 102, '2023-02-20', '14:30:00'),
    (100003, 110, '2024-02-04', '10:00:00');
    
SELECT * FROM APPOINTMENTS ;

-- Update the status when the appointment date has passed

UPDATE Appointments
SET Status = 'Consulted'
WHERE (AppointmentDate) < CURDATE() AND Status = 'Scheduled';

SELECT * FROM APPOINTMENTS ;

-- Consultation Table

CREATE TABLE Consultation (
    ConsultationID INT AUTO_INCREMENT PRIMARY KEY,
    AppointmentID INT NOT NULL,
    DoctorID INT NOT NULL,
    PatientID INT NOT NULL,
    Symptom VARCHAR(255),
    Diagnosis TEXT,
    Medicines TEXT,
    Remarks TEXT,  -- Added Remarks column
    FOREIGN KEY (AppointmentID) REFERENCES Appointments(AppointmentID),
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID),
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
);

INSERT INTO Consultation (AppointmentID, DoctorID, PatientID, Symptom, Diagnosis, Medicines, Remarks) VALUES
    (1000001, 101, 100001, 'Chest pain and shortness of breath', 'Possible cardiac issue, further tests recommended', 'Aspirin, Metoprolol', 'Patient advised to monitor blood pressure regularly.'),
    (1000002, 102, 100002, 'Skin rash and itching', 'Diagnosed as allergic reaction, advised avoiding allergen', 'Cetirizine, Hydrocortisone', 'Patient instructed to follow up if symptoms persist.');
    
SELECT * FROM Consultation ;