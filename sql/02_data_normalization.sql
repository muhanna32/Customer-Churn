INSERT INTO Geography (CountryName)
SELECT DISTINCT Geography 
FROM Staging_Customer_Raw
WHERE Geography IS NOT NULL;

select * from Geography;

INSERT INTO Customers (CustomerId, Surname, Gender, Age, GeographyId)
SELECT DISTINCT 
    raw.CustomerId, 
    raw.Surname, 
    raw.Gender, 
    raw.Age, 
    geo.GeographyId
FROM Staging_Customer_Raw raw
LEFT JOIN Geography geo ON raw.Geography = geo.CountryName;

select * from Customers;

INSERT INTO Account_Details (CustomerId, CreditScore, Balance, EstimatedSalary, Tenure)
SELECT 
    CustomerId, 
    CreditScore, 
    Balance, 
    EstimatedSalary, 
    Tenure
FROM Staging_Customer_Raw;

select * from Account_Details;

INSERT INTO Credit_Cards (CustomerId, HasCrCard, Card_Type, Point_Earned)
SELECT 
    CustomerId, 
    HasCrCard, 
    Card_Type, 
    Point_Earned
FROM Staging_Customer_Raw;

select * from Credit_Cards;

INSERT INTO Customer_Activity_Churn (CustomerId, NumOfProducts, IsActiveMember, Complain, Satisfaction_Score, Exited)
SELECT 
    CustomerId, 
    NumOfProducts, 
    IsActiveMember, 
    Complain, 
    Satisfaction_Score, 
    Exited
FROM Staging_Customer_Raw;

select * from Customer_Activity_Churn;