-- pharmacy_db.sql
CREATE DATABASE IF NOT EXISTS PharmacyDB;
USE PharmacyDB;

-- drop for fresh import
DROP TABLE IF EXISTS BillDetails;
DROP TABLE IF EXISTS Bill;
DROP TABLE IF EXISTS Medicine;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Employee;

-- Employee
CREATE TABLE IF NOT EXISTS Employee (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_name VARCHAR(100),
    username VARCHAR(50) UNIQUE,
    password VARCHAR(50)
);

-- Customer (no address)
CREATE TABLE IF NOT EXISTS Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100),
    phone VARCHAR(20)
);

-- Medicine
CREATE TABLE IF NOT EXISTS Medicine (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(200),
    quantity INT DEFAULT 0,
    price DECIMAL(10,2),
    expiry_date DATE
);

-- Bill (customer_id preserved)
CREATE TABLE IF NOT EXISTS Bill (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    emp_id INT,
    bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(12,2),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (emp_id) REFERENCES Employee(emp_id)
);

-- BillDetails: store medicine snapshot + medicine_id reference
CREATE TABLE IF NOT EXISTS BillDetails (
    billdetails_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT,
    medicine_id INT NULL,
    medicine_name VARCHAR(255),
    price DECIMAL(10,2),
    quantity INT,
    subtotal DECIMAL(12,2),
    FOREIGN KEY (bill_id) REFERENCES Bill(bill_id)
);

-- Sample employees
INSERT INTO Employee (emp_name, username, password) VALUES
('Anil Kumar','anil','anil123'),
('Ravi Shankar','ravi','ravi123'),
('Prakash Rao','prakash','prakash123'),
('Mahesh Babu','mahesh','mahesh123'),
('Suresh Reddy','suresh','suresh123');

-- Sample customers
INSERT INTO Customer (customer_name, phone) VALUES
('Arun Prakash', '9876102345'),
('Deepika Rao', '9023456712'),
('Vijay Kumar', '9988001122'),
('Shilpa Reddy', '9001237890'),
('Mahesh Gowda', '9099123456'),
('Nandini Rao', '9877001234'),
('Harsha V', '9123459800'),
('Rohini Shetty', '9012349876'),
('Manoj S', '9888990011'),
('Aishwarya K', '9345678123');


-- Sample medicines
INSERT INTO Medicine (medicine_name, quantity, price, expiry_date) VALUES
('Crocin 500mg', 150, 22.00, '2027-02-18'),
('Zifi 200mg', 90, 110.00, '2026-08-14'),
('Novamox 250mg', 60, 75.00, '2027-03-20'),
('Shelcal 500', 100, 95.00, '2028-05-10'),
('Ecosprin 150mg', 40, 18.00, '2026-02-15'),
('Supradyn Tablets', 85, 85.00, '2027-10-22'),
('Revital H', 45, 180.00, '2028-06-01'),
('ORS Lemon', 200, 18.00, '2028-12-10'),
('Amrutanjan Roll On', 30, 60.00, '2026-11-09'),
('T-Minic Syrup', 20, 70.00, '2024-12-12'),   
('Nise 100mg', 10, 28.00, '2025-12-05'),       
('Cofsils Lozenges', 300, 5.00, '2028-01-18'),
('Omez 20mg', 50, 35.00, '2026-09-22'),
('ORS Apple', 140, 20.00, '2027-04-01'),
('Zyrtec 10mg', 5, 12.00, '2025-02-15'),      
('Pantodac 40mg', 90, 38.00, '2027-06-19'),
('Tenolol 50mg', 70, 45.00, '2026-03-11'),
('Volini Spray', 42, 95.00, '2027-10-19'),
('Betadin Ointment', 12, 55.00, '2026-07-21'),
('Vaseline 50ml', 60, 35.00, '2028-03-15');


INSERT INTO Bill (customer_id, emp_id, total_amount, bill_date) VALUES
(1, 1, 450.00, '2025-11-22 10:05:22'),
(2, 2, 220.00, '2025-11-22 10:12:40'),
(3, 3, 680.00, '2025-11-22 11:01:12'),
(4, 2, 145.00, '2025-11-22 11:22:55'),
(5, 4, 330.00, '2025-11-22 11:45:19'),
(6, 5, 570.00, '2025-11-22 12:10:33'),
(7, 1, 255.00, '2025-11-22 12:22:42'),
(8, 3, 920.00, '2025-11-22 12:45:00'),
(9, 4, 110.00, '2025-11-22 13:05:49'),
(10, 2, 380.00, '2025-11-22 13:22:48');




INSERT INTO BillDetails (bill_id, medicine_id, medicine_name, price, quantity, subtotal) VALUES
(1, 1, 'Crocin 500mg', 22, 5, 110),
(1, 3, 'Novamox 250mg', 75, 3, 225),
(2, 15, 'Zyrtec 10mg', 12, 4, 48),
(2, 8, 'ORS Lemon', 18, 3, 54),
(3, 2, 'Zifi 200mg', 110, 4, 440),
(3, 18, 'Volini Spray', 95, 2, 190),
(4, 12, 'Cofsils Lozenges', 5, 15, 75),
(5, 11, 'Nise 100mg', 28, 3, 84),
(5, 14, 'ORS Apple', 20, 5, 100),
(6, 7, 'Revital H', 180, 2, 360),
(6, 4, 'Shelcal 500', 95, 2, 190),
(7, 20, 'Vaseline 50ml', 35, 3, 105),
(8, 6, 'Supradyn Tablets', 85, 4, 340),
(8, 9, 'Amrutanjan Roll On', 60, 2, 120),
(8, 16, 'Pantodac 40mg', 38, 4, 152),
(9, 10, 'T-Minic Syrup', 70, 1, 70),
(10, 17, 'Tenolol 50mg', 45, 2, 90),
(10, 13, 'Omez 20mg', 35, 4, 140);


-- Views for alerts
CREATE OR REPLACE VIEW LowStockView AS
SELECT medicine_id, medicine_name, quantity, price, expiry_date FROM Medicine WHERE quantity < 5;

CREATE OR REPLACE VIEW ExpiredMedicineView AS
SELECT medicine_id, medicine_name, quantity, price, expiry_date FROM Medicine WHERE expiry_date < CURDATE();

CREATE OR REPLACE VIEW ExpiringSoonView AS
SELECT medicine_id, medicine_name, quantity, price, expiry_date FROM Medicine
WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY);

-- Event to delete expired medicines daily
SET GLOBAL event_scheduler = ON;
DROP EVENT IF EXISTS DeleteExpiredMedicines;
CREATE EVENT DeleteExpiredMedicines
ON SCHEDULE EVERY 1 DAY
DO
  DELETE FROM Medicine WHERE expiry_date < CURDATE();
