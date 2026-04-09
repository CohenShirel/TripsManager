# 🌍 TripManager Pro
### Group Trip and Event Management System

**Contributors:** Neomi Golkin & Shirel Cohen

---

## 📑 Table of Contents
* [Phase 1: Design and Build the Database](#phase-1)
  * [Introduction](#introduction)
  * [ERD (Entity-Relationship Diagram)](#erd)
  * [DSD (Data Structure Diagram)](#dsd)
  * [SQL Scripts](#scripts)
  * [Data](#data)
  * [Backup](#backup)
* [Phase 2: Integration](#phase-2)

---

## Phase 1: Design and Build the Database <a name="phase-1"></a>

---

## 📝 Project Overview <a name="introduction"></a>
The **Group Trip and Event Management System** is designed to efficiently manage information related to travel groups, professional guides, participants, and scheduled itineraries. 

> This system ensures smooth organization and tracking of essential details such as group assignments, guide expertise, and real-time trip logistics.

---

## 🎯 Purpose of the Database
This database serves as a structured and reliable solution for travel agencies and tour operators to:

* 📍 **Organize Travel Groups** – Link groups to specific participants and itineraries seamlessly.
* 👨‍🏫 **Manage Professional Guides** – Track regional specializations, experience, and contact details.
* 🗺️ **Plan & Monitor Trips** – Ensure proper guide allocation and real-time status tracking across regions.
* 📅 **Schedule Events** – Maintain a detailed and organized timeline for activities within each trip.
* 📂 **Centralized Directory** – Manage locations, points of interest, and comprehensive participant data.

---

## 🚀 Potential Use Cases

| Role | Responsibility |
| :--- | :--- |
| **Administrators** | Oversee operations, allocate resources, and manage directories. |
| **Tour Guides** | Access assigned trips and manage event schedules based on expertise. |
| **Coordinators** | Track participant lists and ensure logistics align with group needs. |
| **Operations Staff** | Maintain real-time records and communication between all parties. |

---

# 💡 Summary
This structured database helps **streamline tour and event operations**, improving logistical efficiency, guide-to-region matching, and communication among all stakeholders involved in group travel.


-----


# ERD (Entity-Relationship Diagram) <a name="erd"></a>
<img width="4002" height="1533" alt="erdplus (8)" src="https://github.com/user-attachments/assets/2d23cf47-ea7d-44bd-a503-7845f65ac55e" />

# DSD (Data Structure Diagram) <a name="dsd"></a>
<img width="4002" height="1533" alt="erdplus (6)" src="https://github.com/user-attachments/assets/4d5fd525-376a-4f41-b061-05365b5e516b" />

# SQL Scripts <a name="scripts"></a>

Provide the following SQL scripts:

* **Create Tables Script** - The SQL script for creating the database tables is available in the repository:
  📜 [createTables.sql](./Phase1/scripts/method1/createTables.sql)

* **Insert Data Script** - The SQL script for inserting data to the database tables is available in the repository:
  📜 [insertTables.sql](./Phase1/scripts/method1/insertTables.sql)

* **Drop Tables Script** - The SQL script for dropping all tables is available in the repository:
  📜 [dropTables.sql](./Phase1/dropTables.sql)

* **Select All Data Script** - The SQL script for selecting all tables is available in the repository:
  📜 [selectAll_tables.sql](./Phase1/dropTables.sql)
  
# Data

# First tool: using mockaro to create csv file
[Entering a data to person table](./Phase1/scripts/method2/generateData)

![צילום מסך 2026-04-10 000653](https://github.com/user-attachments/assets/8171a2be-7bd2-4895-80ea-ac0c1bcc79c6)
# Second tool: using python to create csv file
![צילום מסך 2026-04-10 002617](https://github.com/user-attachments/assets/6dc98c86-0e73-413d-878b-2dbe6d6b76ba)


# Third tool: using python to create csv file

[Link to python file](./Phase1/scripts/method3/generateData/createTables.py)


## Backup
backups files are kept with the date and hour of the backup:
עבור לתיקיית הגיבויים

## Phase 2: Integration


