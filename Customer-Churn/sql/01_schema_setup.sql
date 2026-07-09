CREATE TABLE Geography (
    GeographyId INT IDENTITY(1,1) PRIMARY KEY,
    CountryName VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE Customers (
    CustomerId INT PRIMARY KEY,
    Surname VARCHAR(100),
    Gender VARCHAR(10),
    Age INT,
    GeographyId INT,
    FOREIGN KEY (GeographyId) REFERENCES Geography(GeographyId)
);

CREATE TABLE Account_Details (
    AccountId INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL,
    CreditScore INT,
    Balance DECIMAL(15, 2),
    EstimatedSalary DECIMAL(15, 2),
    Tenure INT,
    FOREIGN KEY (CustomerId) REFERENCES Customers(CustomerId)
);

CREATE TABLE Credit_Cards (
    CardId INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL,
    HasCrCard INT CHECK (HasCrCard IN (0, 1)),
    Card_Type VARCHAR(20),
    Point_Earned INT,
    FOREIGN KEY (CustomerId) REFERENCES Customers(CustomerId)
);

CREATE TABLE Customer_Activity_Churn (
    ActivityId INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL,
    NumOfProducts INT,
    IsActiveMember INT CHECK (IsActiveMember IN (0, 1)),
    Complain INT CHECK (Complain IN (0, 1)),
    Satisfaction_Score INT,
    Exited INT CHECK (Exited IN (0, 1)),
    FOREIGN KEY (CustomerId) REFERENCES Customers(CustomerId)
);

