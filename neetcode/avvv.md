CDuration: 2.5 Hrs.
 
Instructions
Read all sections carefully: Ensure a thorough understanding of the requirements.
Solution: Upload all screenshots of the expected outcomes in a Word document, clearly labeled with your Enterprise ID.
Marks Allocation: Marks will be awarded on assigned task, for which proper documentation along with screenshot of output is available.
DELETE permission successfully denied for AppAdmin on the Products table.
Screenshot showing the error message when attempting to delete a record as AppAdmin.
Screenshots of successful SELECT and INSERT operations after the DELETE permission is denied.
 
Problem Statement
TechNet Solutions is deploying a new SQL Server instance for internal use. The IT department requires your assistance in installing the SQL Server, configuring a new login and user, and managing permissions. You will be responsible for setting up security by granting and denying specific permissions for different roles.
Objective:
Participants will install SQL Server, configure logins, create users, and manage permissions. They will demonstrate their ability to grant and deny permissions for different tasks using SQL Server Management Studio (SSMS).Tasks:
Part 1: Installation of SQL Server
Tasks:
Install SQL Server using a named instance called MSSQLSERVER01.
Confirm the successful installation by connecting to the SQL Server instance through SSMS.
Log in using SQL Server Authentication with the username sa
Expected Outcome:
SQL Server instance successfully installed and accessible via SSMS.
Screenshot of successful login to SSMS with the sa user.
 
Part 2: Create a SQL Server Login
Tasks:
Create a SQL Server login named AppAdmin with a secure password.
Ensure this login uses SQL Server Authentication.
Set the default database for this login to master..
Expected Outcome:
SQL Server login AppAdmin successfully created.
Screenshot of the new login configuration screen in SSMS.
 
Part 3: Create a Database and User
Tasks:
Create a new database named TechNetDB.
Create a new user in the TechNetDB database mapped to the AppAdmin login.
The user should have the db_owner role for the TechNetDB database.
Expected Outcome:
Database TechNetDB created successfully.
User AppAdmin mapped to the login and granted the db_owner role in TechNetDB.
Screenshot showing the AppAdmin user with the db_owner role for TechNetDB..
 
Part 4: Grant Permissions on a Specific Table
Tasks:
In the TechNetDB database, create a table named Products with the following columns: ProductID, ProductName, and Price.
Insert sample data into the Products table.
Grant AppAdmin SELECT and INSERT permissions on the Products table.
Verify that AppAdmin can successfully insert a new product into the table.
Expected Outcome:
Permissions successfully granted for SELECT and INSERT operations on the Products table.
Screenshot showing the AppAdmin user inserting a new product into the table and selecting the data.
 
Part 5: Deny Permissions and Test Access
Tasks:
Deny AppAdmin the DELETE permission on the Products table.
Attempt to delete a product as the AppAdmin user and capture the error message.
Verify that AppAdmin can still insert and select data but cannot delete record.
Expected Outcome:
 
 reate the complete rebuilt visualizer
bash

cat > /home/claude/pyvis_v3.html << 'HTMLEOF'
