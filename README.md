# EVENT BOOKING


A ticketing platform with QR-based ticket validation, downloadable tickets and seamless real-time updates.  


##  Live Demo
[Try it here](https://event-booking-h693.onrender.com)


## Features
- Generate and validate tickets with unique QR codes
- Downloadable PDF receipts (using xhtml2pdf)
- Partial page updates via **HTMX** for a smoother UX
- Admin dashboard for attendee tracking and ticket scan logs
- **Cloudinary** integration for image uploads
- TailwindCSS for a responsive and modern UI


## Tech Stack
- **Backend:** Django 5.2.5, Django HTMX, Django Tailwind
- **Frontend:** TailwindCSS, HTMX
- **Media & Assets:** Cloudinary, Pillow
- **PDF & QR:**  xhtml2pdf, qrcode
- **Environment & Utilities:** python-dotenv, requests, arrow
- **Others:** django-browser-reload (for live dev reloading)


## Installation
```bash
git clone https://github.com/Tarvel/event-booking.git
cd event-booking
cp .env.example .env
docker compose up --build
docker compose exec django-web python manage.py createsuperuser

```
## What I Learned

- How to integrate **Django with HTMX** for partial updates, modals and real-time notifications (via polling)
- Generating and validating **QR codes** for event tickets (using `qrcode`)
- Creating **PDF receipts from HTML templates** with xhtml2pdf
- Uploading and managing media files with **Cloudinary**
- Using **Django Tailwind** for building a responsive, modern UI
- Improved understanding of **PDF signing & validation** with pyHanko
- Leveraging **django-browser-reload** for faster local development
- Strengthened knowledge of **forms, model relationships** in Django
- integration of third party APId: Paystack and Cloudinary
- Access controls
