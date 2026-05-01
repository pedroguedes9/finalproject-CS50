# finalproject-CS50
The CS50 final project repository.

# Doce Império

## Video Demo

https://youtu.be/P7Lh9NpUJjA?si=bvEG1LM6JU_nketi

## Overview

Doce Império is a web application developed as the final project for CS50. The project represents a digital bakery, functioning as a landing page, a product showcase, an integrated ordering system, and an administrative panel. The goal is to simulate a small e-commerce experience, without implementing online payments directly within the application. Payments are handled via WhatsApp, a deliberate choice for simplicity, comfort, and security.

The application was built using Flask for the backend, SQLAlchemy for database modeling and manipulation, Flask-Migrate for database version control, Flask-Login for authentication, Flask-WTF/CSRFProtect for form security, and Tailwind CSS via CDN for the interface. The system allows customers to browse products, add items to a cart, place orders, and view their order history. Meanwhile, administrators have access to a protected area where they can manage products, categories, orders, payment statuses, stock, and key business metrics.

The application serves two types of users. Customers interact with the storefront and place orders, while administrators use internal tools to manage the bakery. This separation is essential, as each role has different needs: customers require a simple and intuitive experience, while administrators need control, filters, editing capabilities, and business insights.

This project also served as an opportunity to apply key concepts learned in CS50, such as route organization, password security, session handling, database relationships, form validation, error handling, file uploads, and template reuse.

## File Structure

The main project is located inside the `projeto-confeitaria` folder. This folder contains the bakery application itself. The structure was designed to separate responsibilities and avoid placing all logic in a single file.

### `app.py`

This is the main entry point of the Flask application. It initializes the app, configures the database, loads extensions, and registers all blueprints.

It also sets important configurations such as file upload limits, CSRF protection, login management, and upload paths. The app limits uploads to 2MB using `MAX_CONTENT_LENGTH` and includes a handler for oversized files.

### `config.py`

This file centralizes application settings, including environment variables, secret key configuration, and database setup.

The project uses a `.env` file to store sensitive data like `SECRET_KEY`. In real-world applications, `.env` files should not be committed to repositories.

### `models.py`

Defines the database schema using SQLAlchemy. The main entities include users, admins, products, categories, carts, orders, and order items.

Data is structured to maintain clarity and efficiency. Orders and order items are separated, as are cart items and order items, representing different stages of the purchasing process.

Prices use `Numeric(10,2)` instead of `Float` to avoid precision issues.

### `requirements.txt`

Lists all dependencies needed to run the project.

### `blueprint` folder

Organizes the application into blueprints, improving modularity and maintainability.

#### `auth`

Handles user registration, login, and logout. Uses Flask-Login and Werkzeug for password hashing.

#### `products`

Manages the product showcase. Products are displayed as cards, and featured items are randomly selected on each page load.

#### `cart`

Allows users to manage their cart. Stock validation ensures users cannot exceed available inventory.

#### `orders`

Displays order history for users. Orders are created without payment and later updated by admins.

#### `admin_panel`

Contains all admin functionality. Protected using a `before_request` hook to ensure all admin routes are secured.

Includes:
- Dashboard (metrics, insights)
- Product management
- Category management
- Order management with filters

## Templates

Uses Jinja templates with reusable layouts:
- `layout.html` for public pages
- `admin_layout.html` for admin panel

Includes reusable components:
- `_messages.html`
- `_pagination.html`

## Static Files

Stored in `static/`, including uploaded product images and JavaScript files.

Images are stored in `static/uploads` to keep the database lightweight.

## Migrations

Managed with Flask-Migrate, allowing database changes without data loss.

## Design Decisions

Key design choices include:

- Use of blueprints for organization
- Separation of admin and user roles
- Use of SQLAlchemy for safer database interaction
- Manual validation for learning purposes
- Use of flash messages for feedback
- File storage for images instead of database blobs
- CSRF protection for security
- Tailwind CSS via CDN for simplicity

The cart system was designed to improve user experience by allowing order assembly before submission.

Payments were intentionally excluded from the system to avoid handling sensitive financial data.

The admin dashboard provides insights such as revenue, order counts, and average ticket value.

## Limitations and Future Improvements

Current limitations include:

- No online payment integration
- No password recovery system
- No custom error pages (404/500)
- No deployment setup
- Limited filtering on public pages

Future improvements may include:

- Payment gateway integration
- Advanced product filtering
- Better customization of orders
- Password recovery system
- Deployment to a production environment

## How to Run

Clone the repository:

```bash
git clone https://github.com/pedroguedes9/finalproject-CS50.git

Navigate to the project folder:
cd finalproject-CS50/projeto-confeitaria

Create a virtual environment:
python -m venv venv

Activate it:
Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt

Create a .env file:
SECRET_KEY=your_secret_key_here

Run migrations:
flask db upgrade

Run the application:
python app.py

Open in browser:
http://127.0.0.1:5000

To access the admin panel, you must manually create an admin user in the database.
```
