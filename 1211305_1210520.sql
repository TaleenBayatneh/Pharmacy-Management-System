DROP DATABASE  PharmacyManagement;
CREATE DATABASE PharmacyManagement;
USE PharmacyManagement;

CREATE TABLE Customer (
    Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    DateOfBirth DATE,
    PhoneNumber VARCHAR(20) NOT NULL,
    City VARCHAR(100),
    Street VARCHAR(100),
    Email VARCHAR(100)
);

CREATE TABLE Pharmacist (
    Pharmacist_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Contact_Info VARCHAR(100) NOT NULL,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(100) NOT NULL,
    Role VARCHAR(50) NOT NULL,
    Wage DECIMAL(10,2),
    Working_Hours INT
);

CREATE TABLE Product (
    Product_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Description TEXT,
    Type VARCHAR(50) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    Quantity INT NOT NULL,
    Expiration_Date DATE NOT NULL,
    LastUpdatedDate DATE
);

CREATE TABLE Purchase_Order (
    Purchase_ID INT PRIMARY KEY AUTO_INCREMENT,
    Pharmacist_ID INT,
    Product_ID INT ,
    Supplier_Name VARCHAR(100) NOT NULL,
    Purchase_Date DATE,
    Quantity INT NOT NULL,
    Unit_Cost DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (Pharmacist_ID) REFERENCES Pharmacist(Pharmacist_ID) ON update CASCADE ON DELETE SET NULL,
    FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID) ON update CASCADE ON DELETE SET NULL
);

CREATE TABLE Subscription (
    Subscription_ID INT PRIMARY KEY AUTO_INCREMENT,
    Customer_ID INT NOT NULL,
    Product_ID INT NOT NULL,
    Start_Date DATE NOT NULL,
    End_Date DATE,
    Refill_Interval INT NOT NULL,
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID) ON update CASCADE on delete cascade,
    FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID) ON update CASCADE on delete cascade
);

CREATE TABLE Prescription (
    Prescription_ID INT PRIMARY KEY AUTO_INCREMENT,
    Customer_ID INT NOT NULL,
    Doctor_Name VARCHAR(100) NOT NULL,
    Date DATE,
    Notes TEXT,
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID) ON update CASCADE on delete cascade
);

CREATE TABLE Prescription_Product (
    Prescription_ID INT,
    Product_ID INT,
    Dosage VARCHAR(50),
    TakenTimes VARCHAR(50),
    Duration VARCHAR(50),
    Quantity INT,
    PRIMARY KEY (Prescription_ID, Product_ID),
    FOREIGN KEY (Prescription_ID) REFERENCES Prescription(Prescription_ID) ON update CASCADE on delete cascade,
    FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID) ON update CASCADE on delete cascade
);

CREATE TABLE Orders (
    Order_ID INT AUTO_INCREMENT PRIMARY KEY,
    Customer_ID INT ,
    Pharmacist_ID INT ,
    Order_Date DATE NOT NULL,
    Payment_Method VARCHAR(50),
    Total_Amount DECIMAL(10,2) NOT NULL,
    Insurance_Discount DECIMAL(5,2) DEFAULT 0,
    Prescription_ID INT,
    Subscription_ID INT, 
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID) ON update CASCADE ON DELETE SET NULL,
    FOREIGN KEY (Pharmacist_ID) REFERENCES Pharmacist(Pharmacist_ID) ON update CASCADE ON DELETE SET NULL,
    FOREIGN KEY (Prescription_ID) REFERENCES Prescription(Prescription_ID) ON update CASCADE ON DELETE SET NULL,
    FOREIGN KEY (Subscription_ID) REFERENCES Subscription(Subscription_ID) ON update CASCADE ON DELETE SET NULL
);

CREATE TABLE Order_Product (
    Order_ID INT,
    Product_ID INT,
    Quantity INT,
    Unit_Price DECIMAL(10,2),
    PRIMARY KEY (Order_ID, Product_ID),
    FOREIGN KEY (Order_ID) REFERENCES Orders(Order_ID) ON update CASCADE on delete cascade,
    FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID) ON update CASCADE on delete cascade
);

SHOW CREATE TABLE Orders;

INSERT INTO Customer (Name, DateOfBirth, PhoneNumber, City, Street, Email)
VALUES
('Ahmad Khalil', '1990-02-15', '0599123456', 'Gaza City', 'Al-Rasheed Street', 'ahmad.khalil@gmail.com'),
('Fatima Abu Omar', '1985-07-10', '0598234567', 'Nablus', 'Al-Jabal Street', 'fatima.abuomar@gmail.com'),
('Hussein Saleh', '1978-12-01', '0598345678', 'Hebron', 'Wadi Al-Tuffah Street', 'hussein.saleh@gmail.com'),
('Mariam Al-Hajj', '1995-05-20', '0598456789', 'Jericho', 'Ein Al-Sultan Street', 'mariam.hajj@gmail.com'),
('Yousef Taha', '1982-03-30', '0598567890', 'Ramallah', 'Al-Balou Street', 'yousef.taha@gmail.com'),
('Layla Saeed', '1992-11-15', '0598678901', 'Jenin', 'Al-Marah Street', 'layla.saeed@gmail.com'),
('Khaled Naser', '1980-06-25', '0598789012', 'Gaza City', 'Al-Shifa Street', 'khaled.naser@gmail.com'),
('Hala Zayed', '1988-01-18', '0598890123', 'Bethlehem', 'Manger Street', 'hala.zayed@gmail.com'),
('Ali Hassan', '1975-09-05', '0598901234', 'Tulkarm', 'Al-Quds Street', 'ali.hassan@gmail.com'),
('Nour Mansour', '1993-08-22', '0599012345', 'Qalqilya', 'Al-Salam Street', 'nour.mansour@gmail.com'),
('Samah Khalil', '1990-02-15', '0598123456', 'Ramallah', 'Al-Quds Street', 'samah@gmail.com'),
('Omar Farooq', '1987-04-12', '0599023456', 'Gaza City', 'Al-Nasr Street', 'omar.farooq@gmail.com'),
('Lina Ibrahim', '1991-09-03', '0599134567', 'Nablus', 'Al-Qaryoun Street', 'lina.ibrahim@gmail.com'),
('Tamer Abu Rida', '1983-11-22', '0599245678', 'Hebron', 'Al-Sheikh Street', 'tamer.aburida@gmail.com'),
('Rasha Khaled', '1996-06-17', '0599356789', 'Jericho', 'Al-Auja Street', 'rasha.khaled@gmail.com'),
('Ibrahim Jaber', '1979-08-08', '0599467890', 'Ramallah', 'Al-Tira Street', 'ibrahim.jaber@gmail.com'),
('Sara Nassar', '1994-03-14', '0599578901', 'Jenin', 'Al-Hadaf Street', 'sara.nassar@gmail.com'),
('Mohammad Awad', '1986-12-30', '0599689012', 'Gaza City', 'Al-Zeitoun Street', 'mohammad.awad@gmail.com'),
('Aya Zain', '1990-07-19', '0599790123', 'Bethlehem', 'Al-Najah Street', 'aya.zain@gmail.com'),
('Kamal Hussein', '1976-05-25', '0599801234', 'Tulkarm', 'Al-Nour Street', 'kamal.hussein@gmail.com'),
('Reem Salah', '1997-10-10', '0599912345', 'Qalqilya', 'Al-Jazeera Street', 'reem.salah@gmail.com');

INSERT INTO Pharmacist (Name, Contact_Info, Username, Password, Role, Wage, Working_Hours)
VALUES
('Areej Shrateh', '0598567165', 'ashrateh', 'Areej456', 'Senior Pharmacist', 3000.00, 40),
('Asem Rimawi', '0598567166', 'arimawi', 'Asem456', 'Senior Pharmacist', 2800.00, 35),
('Sarah Hassan', '0598123456', 'shassan', 'Sarah123', 'Pharmacist', 2500.00, 30),
('Ahmad Nasser', '0598234567', 'dnasser', 'Ahmad456', 'Pharmacist', 2700.00, 32),
('Rania Al-Jamal', '0598345678', 'rjamal', 'Rania123', 'Pharmacist', 2600.00, 28),
('Laila Qasim', '0599567165', 'lqasim', 'Laila789', 'Pharmacist', 2400.00, 25),
('Yazan Khalil', '0599667166', 'ykhalil', 'Yazan123', 'Senior Pharmacist', 2900.00, 38),
('Nada Younis', '0599223456', 'nyounis', 'Nada456', 'Pharmacist', 2600.00, 30),
('Omar Shaban', '0599334567', 'oshaban', 'Omar789', 'Pharmacist', 2500.00, 28),
('Hanan Ali', '0599445678', 'hali', 'Hanan123', 'Senior Pharmacist', 3000.00, 40);

INSERT INTO Product (Name, Description, Type, Price, Quantity, Expiration_Date, LastUpdatedDate)

VALUES
-- Medications
('ZITROCIN', 'Upper respiratory tract infection', 'Capsule', 40.00, 400, '2025-10-15', '2024-11-29'),
('AZIMEX', 'Upper respiratory tract infection', 'Capsule', 42.00, 150, '2025-12-30', '2024-11-29'),
('Azicare', 'Upper respiratory tract infection', 'Capsule', 40.00, 300, '2025-06-10', '2024-11-29'),
('Aziro', 'Upper respiratory tract infection', 'Capsule', 22.00, 100, '2025-03-20', '2024-11-29'),
('Dexamol', 'pain relief and fever reduction', 'Syrup', 28.00, 120, '2025-07-30', '2024-11-29'),
('Sedamol', 'pain relief and fever reduction', 'Syrup', 10.00, 400, '2026-01-01', '2024-11-29'),
('Acamol', 'pain relief and fever reduction', 'Syrup', 13.00, 180, '2025-11-25', '2024-11-29'),
('Panadol', 'pain relief and fever reduction', 'Tablet', 14.00, 90, '2025-10-15', '2024-11-29'),
('Advil Fort', 'pain relief and reducing inflammation', 'Capsule', 49.00, 250, '2025-12-01', '2024-11-29'),
('IBUFEN', 'pain relief and reducing inflammation', 'Syrup', 32.00, 140, '2025-08-20', '2024-11-29'),
('TRUFEN', 'Topical gel for pain relief', 'Gel', 15.00, 140, '2025-09-20', '2024-11-29'),
('VALZAN-HCT', 'Manages high blood pressure', 'Tablet', 26.00, 146, '2025-08-02', '2024-11-29'),
('Diovan', 'Manages high blood pressure', 'Tablet', 28.00, 110, '2025-10-17', '2024-11-29'),
('CLAMOXIN BID', 'treat bacterial infections', 'Syrup', 38.00, 146, '2025-12-12', '2024-11-29'),
('AMOXICLAV', 'treat bacterial infections', 'Syrup', 37.00, 80, '2025-04-20', '2024-11-29'),
('Augmentin', 'treat bacterial infections', 'Syrup', 37.00, 140, '2025-07-14', '2024-11-29'),
('LIPONIL', 'manage high cholesterol levels and triglycerides', 'Tablet', 49.00, 140, '2025-08-20', '2024-11-29'),
('LIPIDEX', 'manage high cholesterol levels and triglycerides', 'Tablet', 45.00, 200, '2025-08-29', '2024-11-29'),
('Lipitor', 'manage high cholesterol levels and triglycerides', 'Tablet', 54.00, 140, '2025-08-20', '2024-11-29'),
('ROSULIP', 'manage high cholesterol levels and triglycerides', 'Tablet', 80.00, 140, '2025-08-20', '2024-11-29'),
('Crestor', 'manage high cholesterol levels and triglycerides', 'Tablet', 99.00, 140, '2025-08-20', '2024-11-29'),
('ANAPRIL', 'treat conditions related to the heart and blood vessels', 'Tablet', 25.00, 140, '2025-08-20', '2024-11-29'),
('ENALADEX', 'treat conditions related to the heart and blood vessels', 'Tablet', 15.00, 140, '2025-08-20', '2024-11-29'),
('Lucast', 'Relieves symptoms of seasonal allergies and allergic rhinitis', 'Tablet', 65.00, 140, '2025-08-20', '2024-11-29'),
('SINGULAIR', 'Relieves symptoms of seasonal allergies and allergic rhinitis', 'Tablet', 81.00, 140, '2025-08-20', '2024-11-29'),
('LEUKOMONT4MG CHEWABEL TABLETS', 'Relieves symptoms of seasonal allergies and allergic rhinitis', 'Chewable Tablet', 67.00, 140, '2025-08-20', '2024-11-29'),
('Rhinofex', 'nasal congestion', 'Nasal Spray', 20.00, 140, '2025-08-20', '2024-11-29'),
('Otrivin', 'nasal congestion', 'Nasal Spray', 32.00, 140, '2025-08-20', '2024-11-29'),
('Candistan', 'treat a variety of fungal infections', 'Cream', 14.00, 140, '2025-08-20', '2024-11-29'),
('Canesten', 'treat a variety of fungal infections', 'Cream', 41.00, 140, '2025-08-20', '2024-11-29'),
('Vitamin D3', 'Vitamin', 'Drops', 36.00, 100, '2026-02-01', '2024-11-29'),
('Vitamin B12', 'Vitamin', 'Injection', 28.00, 90, '2028-02-01', '2024-11-29'),
('Vitamin C', 'Vitamin', 'Tablet', 41.00, 70, '2026-12-01', '2024-11-29'),

-- Cosmetic Products
('LABELLO LIPSTICK', 'Lipstick', 'Lipstick', 10.00, 50, '2026-03-15', '2024-11-29'),
('JOKO MATT LIPS LIPSTICK', 'Lipstick', 'Lipstick', 15.00, 30, '2026-07-15', '2024-11-29'),
('MUSIC FLOWER ULTRA VELVET MATTE LIPSTICk', 'Lipstick', 'Lipstick', 15.00, 80, '2026-07-15', '2024-11-29'),
('YOKO HEALTHY WHITE MOISTURIZER CREAM', 'Hydrating skin moisturizer', 'Cream', 45.00, 90, '2025-11-20', '2024-11-29'),
('NEUTROGENA HYDRO BOOST GEL CREAM, DRY SKIN', 'Hydrating skin moisturizer', 'Cream', 55.00, 100, '2025-12-20', '2024-11-29'),
('BIODERM ATODERM GEL CREAM, DRY SKIN', 'Hydrating skin moisturizer', 'Cream', 75.00, 100, '2026-04-20', '2024-11-29'),
('INSPIRE PERFUMED SPRAY', 'body spray', 'Perfume Spray', 25.00, 30, '2027-08-01', '2024-11-29'),
('MINI CRYSTAL PERFUMED', 'body spray', 'Perfume Spray', 25.00, 20, '2027-09-01', '2024-11-29'),
('MAISON ALHAMBRA EXTRA LONG LASING PERFUMED BODY SPRAY', 'body spray', 'Perfume Spray', 25.00, 40, '2027-08-01', '2024-11-29'),
('BIODERM Sunscreen', 'Sunscreen', 'Sunscreen', 80.00, 60, '2025-04-15', '2024-11-29'),
('Avene Sunscreen', 'Sunscreen', 'Sunscreen', 110.00, 60, '2025-08-15', '2024-11-29'),
('Nextgen SPF Sunscreen', 'Sunscreen', 'Sunscreen', 90.00, 60, '2025-07-15', '2024-11-29'),
('TOPFACE Foundation', 'Foundation', 'Foundation', 35.00, 40, '2026-09-30', '2024-11-29'),
('TONY MAKE UP FOR YOU HD PROFESSIONAL FOUNDATION', 'Foundation', 'Foundation', 50.00, 30, '2026-09-30', '2024-11-29'),
('OSHEA Foundation', 'Foundation', 'Foundation', 55.00, 30, '2026-09-30', '2024-11-29'),
('BIODERM Face Wash', 'Face Wash', 'Face Wash', 110.00, 100, '2025-06-05', '2024-11-29'),
('Avene Face Wash', 'Face Wash', 'Face Wash', 80.00, 100, '2025-06-05', '2024-11-29'),
('NIVEA CLEANSE & CARE FACE WASH', 'Face Wash', 'Face Wash', 70.00, 100, '2025-06-05', '2024-11-29'),
('CHI ROYAL SHAMPOO', 'shampoo', 'Shampoo', 100.00, 120, '2026-01-20', '2024-11-29'),
('ALASEEL COSMETICS HAIR SHAMPOO', 'shampoo', 'Shampoo', 90.00, 80, '2026-01-20', '2024-11-29'),
('BABY SEBAMED SHAMPOO', 'shampoo', 'Shampoo', 100.00, 120, '2026-12-20', '2024-11-29'),
('LANA LINE HELLO BEAUTIFUL HAND CREAM', 'hand cream', 'Cream', 150.00, 80, '2026-03-10', '2024-11-29'),
('LOVINA CARE TREAT HAND CREAM', 'hand cream', 'Cream', 35.00, 80, '2026-03-10', '2024-11-29'),
('ESFOLIO FRESH PINK PEACH HAND CREAM', 'hand cream', 'Cream', 70.00, 80, '2026-03-10', '2024-11-29'),
('TO-ME JOJOBA EXTRACT BODY LOTION', 'body lotion', 'Lotion', 110.00, 90, '2025-11-15', '2024-11-29'),
('NIVEA NATURAL GLOW C&A VITAMIN BODY LOTION', 'body lotion', 'Lotion', 75.00, 90, '2025-11-15', '2024-11-29'),
('VASU SHEA BUTTER CARE BODY LOTION', 'body lotion', 'Lotion', 130.00, 90, '2025-11-15', '2024-11-29'),
('VATIKA ONION ENRICHED HAIR OIL', 'Hair Oil', 'Hair Oil', 35.00, 60, '2026-06-15', '2024-11-29'),
('KISS BEAUTY HAIR OIL', 'Hair Oil', 'Hair Oil', 25.00, 60, '2026-10-15', '2024-11-29'),
('PURE HAIR OIL', 'Hair Oil', 'Hair Oil', 100.00, 60, '2026-06-15', '2024-11-29'),
('ULTRA MAX', 'Deodorant', 'Deodorant', 20.00, 140, '2026-05-25', '2024-11-29'),
('DOVE', 'Deodorant', 'Deodorant', 18.00, 140, '2025-05-25', '2024-11-29'),
('HUGO Deodorant', 'Deodorant', 'Deodorant', 45.00, 140, '2028-05-25', '2024-11-29'),
('SUN GEL LOLO PLUS HAND SANITIZER', 'Hand Sanitizer', 'Sanitizer', 30.00, 50, '2025-03-01', '2024-11-29'),
('HIGEEN ANTI-BACTERIAL HAND SANITIZER', 'Hand Sanitizer', 'Sanitizer', 10.00, 100, '2027-03-01', '2024-11-29'),
('MIX HAND SANITIZER GEL', 'Hand Sanitizer', 'Sanitizer', 15.00, 200, '2025-03-01', '2024-11-29'),
('ORAL-B PRO-EXPERT DEEP CLEAN TOOTHPASTE', 'Toothpaste', 'Toothpaste', 15.00, 90, '2026-07-05', '2024-11-29'),
('SIGNAL COMPLETE Toothpaste', 'Toothpaste', 'Toothpaste', 14.00, 60, '2026-07-05', '2024-11-29'),
('WHITE GLO PROFESSIONAL CHOICE TOOTHPASTE', 'Toothpaste', 'Toothpaste', 27.00, 80, '2026-07-05', '2024-11-29');

INSERT INTO Prescription (Customer_ID, Doctor_Name, Date, Notes)
VALUES
(2, 'Dr. Mohammad Ahmad', '2025-01-15', 'Take twice daily for infection'),
(3, 'Dr. Hazem Aiash', '2025-02-10', 'For high blood pressure'),
(4, 'Dr. Amina Said', '2025-03-01', 'Take once daily with meal'),
(5, 'Dr. Khaled Ismail', '2025-03-15', 'For diabetes management'),
(6, 'Dr. Fatima Nour', '2025-04-01', 'Twice daily for infection'),
(7, 'Dr. Omar Jaber', '2025-04-10', 'For cholesterol control'),
(8, 'Dr. Laila Hassan', '2025-06-01', 'Follow up after 2 weeks');

INSERT INTO Prescription_Product (Prescription_ID, Product_ID, Dosage, TakenTimes, Duration, Quantity)
VALUES
(1, 1, '500mg', 'Twice daily', '7 days', 14),
(2, 7, '20mg', 'Once daily', '30 days', 30),
(3, 2, '500mg', 'Once daily', '10 days', 10),
(4, 6, '20mg', 'Twice daily', '15 days', 30),
(5, 3, '400mg', 'Once daily', '7 days', 7),
(6, 8, '10mg', 'Once daily', '20 days', 20),
(7, 5, '75mg', 'Twice daily', '14 days', 28);

INSERT INTO Subscription (Customer_ID, Product_ID, Start_Date, End_Date, Refill_Interval)
VALUES
(1, 9, '2025-01-01', '2025-12-31', 30),
(5, 7, '2025-02-01', '2025-08-01', 7),
(6, 4, '2025-03-01', '2026-03-01', 15),
(7, 5, '2025-04-01', '2026-04-01', 30),
(8, 6, '2025-05-01', '2026-05-01', 10),
(9, 7, '2025-06-01', '2026-06-01', 20),
(10, 8, '2025-06-07', '2026-06-07', 14);

INSERT INTO Orders (Customer_ID, Pharmacist_ID, Order_Date, Payment_Method, Total_Amount, Insurance_Discount, Prescription_ID, Subscription_ID)
VALUES
(1, 2, '2025-01-15', 'Cash', 80.00, 5.00, NULL, NULL),
(2, 1, '2025-01-20', 'Card', 44.99, 0.00, 1, NULL),
(3, 3, '2025-02-05', 'Cash', 66.00, 10.00, 2, NULL),
(4, 2, '2025-02-10', 'Card', 123.99, 2.50, NULL, 1),
(5, 3, '2025-06-01', 'Cash', 50.00, 0.00, 3, NULL),
(6, 4, '2025-06-03', 'Card', 72.00, 5.00, 4, NULL),
(7, 5, '2025-06-05', 'Cash', 88.00, 10.00, 5, NULL),
(8, 1, '2025-06-07', 'Card', 110.00, 2.00, NULL, 2),
(9, 2, '2025-06-07', 'Cash', 65.00, 0.00, NULL, 3);

INSERT INTO Order_Product (Order_ID, Product_ID, Quantity, Unit_Price)
VALUES
(1, 1, 2, 40.00),
(2, 7, 1, 44.99),
(3, 4, 2, 28.00),
(4, 10, 1, 9.99),
(4, 11, 2, 12.99),
(5, 2, 2, 35.00),
(6, 6, 1, 30.00),
(7, 3, 2, 20.00),
(8, 7, 2, 22.00),
(9, 4, 3, 25.00);

INSERT INTO Purchase_Order (Pharmacist_ID, Product_ID, Supplier_Name, Purchase_Date, Quantity, Unit_Cost)
VALUES
(1, 1, 'Birzeit Pharmaceuticals', '2025-01-10', 50, 35.00),
(2, 3, 'Jerusalem Pharmaceutical', '2025-02-01', 30, 38.00),
(3, 5, 'Gaza Pharma', '2025-02-15', 100, 10.00),
(3, 2, 'Nablus Pharma', '2025-06-01', 40, 32.00),
(4, 4, 'Hebron Supplies', '2025-06-03', 60, 22.00),
(5, 6, 'Ramallah Distributors', '2025-06-05', 50, 27.00),
(1, 8, 'Gaza Traders', '2025-06-07', 30, 40.00),
(2, 10, 'Jericho Imports', '2025-06-07', 70, 10.00);

ALTER TABLE Customer AUTO_INCREMENT = 1;
ALTER TABLE Pharmacist AUTO_INCREMENT = 1;
ALTER TABLE Product AUTO_INCREMENT = 1;
ALTER TABLE Orders AUTO_INCREMENT = 1;
ALTER TABLE Purchase_Order AUTO_INCREMENT = 1;
ALTER TABLE Subscription AUTO_INCREMENT = 1;
ALTER TABLE Prescription AUTO_INCREMENT = 1;

SELECT * FROM Customer;
SELECT * FROM Pharmacist;
SELECT * FROM Product;
SELECT * FROM Orders;
SELECT * FROM Order_Product;
SELECT * FROM Purchase_Order;
SELECT * FROM Subscription;
SELECT * FROM Prescription;
SELECT * FROM Prescription_Product;
