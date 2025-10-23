Farm2Door Documentation
Introduction
Farm2Door is a web-based e-commerce platform designed to connect farmers directly with consumers. The primary goal of this project is to ensure that fresh, organic, and locally produced farm goods can reach customers quickly and efficiently, while also providing fair compensation to farmers.
Traditional supply chains often involve multiple intermediaries, which results in higher prices for consumers and reduced profits for farmers. Farm2Door eliminates these middlemen by creating a direct digital bridge between farmers (suppliers) and customers (buyers).
The platform will allow farmers to list their products, manage inventory, and track orders, while customers will be able to browse items, place orders, and receive estimated delivery timelines. The system will also incorporate a delivery tracking timeline, displaying each stage of the order journey—from product pickup at the farm to final delivery at the customer’s doorstep.
Objectives
The main objectives of the Farm2Door project are as follows:
Direct Farmer-to-Customer Connection
Eliminate middlemen and provide a platform where farmers can sell directly to customers.
Ensure farmers receive fair prices for their products.

Affordable and Fresh Products for Customers
Deliver organic, farm-fresh goods at reasonable prices.
Reduce delays in delivery to maintain product quality.

Digital Marketplace for Agriculture
Provide farmers with a simple and accessible digital platform to list, manage, and sell their products.
Offer customers a modern e-commerce shopping experience for agricultural products.

Efficient Delivery Management
Introduce a delivery timeline tracking system, allowing customers to view the status of their orders (farm pickup → warehouse → delivery partner → doorstep).
Reduce uncertainty regarding delivery times.

Scalability and Growth
Build a platform that can expand to support multiple regions and diverse product categories.
Support both small-scale farmers and larger agricultural suppliers.

User-Friendly Dashboard
Provide a farmer dashboard for product management, sales analytics, and order tracking.
Provide an admin dashboard to manage users, monitor deliveries, and oversee transactions.
Scope of the Project
The Farm2Door system is designed to serve as a bridge between farmers and customers, offering a transparent, efficient, and digital platform for agricultural trade. The scope includes the following:
Farmers
Farmers can register, create profiles, and list their products.
They can manage inventory, update stock, and track sales performance.
They will receive notifications regarding orders, payments, and delivery status.

Customers
Customers can browse farm products, add items to their cart, and place orders.
They will have access to a secure payment gateway.
Customers can track their product delivery timeline from farm to doorstep.

Admin Panel
Admins can manage both farmers and customers.
They can monitor transactions, handle disputes, and verify product quality.
Admin will also oversee logistics, ensuring smooth delivery operations.

Delivery & Logistics
Integration of delivery partners to ensure timely and efficient transportation.
Delivery tracking system with estimated time of arrival (ETA).

Technology Scope
Backend: Django with PostgreSQL for secure and scalable data handling.
Frontend: Vue.js for building a responsive and dynamic user interface.
Deployment: Cloud-ready architecture, ensuring scalability.

Limitations (Out of Scope for Phase 1)
International delivery (limited to local/regional areas).
Advanced AI-based demand forecasting (future enhancement).
Wholesale bulk trading (will be introduced in future phases).
System Features
The Farm2Door system provides a range of core features to ensure smooth interaction between farmers, customers, and administrators:

1. User Authentication & Profiles
   Farmers, customers, and admins have separate accounts.
   Secure login and registration with email/phone verification.
   Profile management for updating personal and business details.

2. Product Management (Farmers)
   Farmers can add, edit, and delete product listings.
   Ability to upload product images, descriptions, and pricing.
   Stock management with alerts for low inventory.

3. Product Browsing & Search (Customers)
   Customers can browse products by category (vegetables, fruits, grains, etc.).
   Advanced search and filter options (price, type, freshness).
   Product details page with description, farmer info, and delivery options.
4. Cart & Order Management
   Add to cart, update quantity, and checkout process.
   Customers can view and manage their orders.
   Farmers can track incoming orders and prepare for delivery.
5. Delivery Timeline Tracking
   Timeline visualization from farm → collection point → processing → delivery → customer’s doorstep.
   Estimated time of arrival (ETA) displayed to customers.
   Notifications at every stage of the delivery process.
6. Payment Gateway Integration
   Secure online payment options (mobile banking, cards, cash on delivery).
   Automated invoice generation for each order.
   Farmers can track their earnings and withdrawals.
7. Admin Dashboard
   Manage users (farmers/customers).
   Monitor transactions and resolve disputes.
   Control product categories and verify authenticity.
   Generate reports on sales, revenue, and delivery performance.
8. Feedback & Rating System
   Customers can provide ratings and reviews for farmers/products.
   Helps ensure quality and trust between farmers and buyers.
9. Notifications System
   Real-time notifications via SMS/Email/App alerts.
   Order confirmation, payment success, and delivery updates.
10. Security & Data Protection
    Encrypted user data and payment details.
    Role-based access control (Admin vs Farmer vs Customer).
    Regular backups and secure authentication.

System Design (DFD Explanation)
The system is designed using Data Flow Diagrams (DFDs) to illustrate how data moves through the Farm2Door application. It shows the interaction between farmers, customers, and the admin with the system’s core processes.
Level 0 DFD (Context Diagram)
Shows the system as a single process (“Farm2Door System”).
External entities: Farmers, Customers, Admin.
Arrows show flow of data such as product info, order requests, payments, and reports.
Level 1 DFD
Breaks the system into key processes:
User Management (registration, login, profiles)
Product Management (farmers upload/manage products)
Order & Cart Management (customers place and track orders)
Payment & Invoicing (process payments, generate receipts)
Delivery Management (timeline updates, notifications)
Admin Dashboard (user monitoring, reports, conflict resolution)
Level 2 DFD Details each Level 1 process further.

1. User Management
   Input: Registration/Login details.
   Process: Authentication & Role Verification.
   Output: Access granted (Farmer/Customer/Admin dashboard).
2. Product Management
   Input: Product details from farmer.
   Process: Validate & store in PostgreSQL database.
   Output: Product listed for customers.
3. Order & Cart Management
   Input: Customer selects items and add to cart.
   Process: Order validation, stock check, assign farmer.
   Output: Order confirmation + cart update.
4. Payment & Invoicing
   Input: Customer payment details.
   Process: Payment gateway verification.
   Output: Payment success/failure + invoice generated.

5. Delivery Management
   Input: Confirmed order.
   Process: Update delivery timeline (farm → collection point → processing → delivery).
   Output: Delivery status notifications to customers.
6. Admin Dashboard
   Input: User activities, system logs.
   Process: Admin monitoring, report generation, fraud detection.
   Output: Reports, resolved disputes, system control.
