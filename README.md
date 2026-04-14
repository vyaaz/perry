# Perry CRM

A simple Django-based CRM for managing a window washing / home services business.  
Includes scheduling, customers, jobs, invoices, sales tracking, and geolocation mapping.

---

## 🚀 Features

- Customer management with full history tracking
- Job scheduling and assignment
- Calendar-based scheduling system
- Invoice tracking (paid/unpaid status)
- Worker commissions (seller + cleaner payouts)
- Sales tracking (doors knocked, closes, rejection tracking)
- Geolocation map with Leaflet.js
- Role-based access (Manager, Seller, Cleaner)
- Simple dashboard analytics

---

## 🛠️ Tech Stack

- Django (Monolithic app)
- SQLite (default database)
- Django Templates (server-rendered UI)
- Bootstrap (UI styling)
- Leaflet.js (maps)

---

## 📦 Installation & Setup

### 1. Clone the repository

```cmd
git clone https://github.com/vyaaz/
```
### 2. Direct into Perry
```cmd
cd perry
```
### 3. See file contents until you can see manage.py
```cmd
dir
```
### 4. Create admin superuser with relevant details
```cmd
python manage.py createsuperuser
```
### 5. Run server
```cmd
python manage.py runserver
```
### 6. Log in and test features
- Voila!!
