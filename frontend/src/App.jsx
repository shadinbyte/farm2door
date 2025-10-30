import React from "react";
import "./App.css";

function App() {
  return (
    <div className="app">
      {/* Hero Section */}
      <section className="hero">
        <h1>Welcome to Farm2Door</h1>
        <p>
          Connecting farmers directly with customers for fresh, organic, and locally produced goods.
        </p>
        <button className="cta-btn">Shop Now</button>
      </section>

      {/* Objectives Section */}
      <section className="objectives">
        <h2>Our Objectives</h2>
        <ul>
          <li><strong>Direct Farmer-to-Customer Connection:</strong> Eliminate middlemen and ensure fair prices for farmers.</li>
          <li><strong>Affordable & Fresh Products:</strong> Deliver organic goods at reasonable prices.</li>
          <li><strong>Digital Marketplace:</strong> Provide a modern e-commerce experience for agricultural products.</li>
          <li><strong>Efficient Delivery:</strong> Real-time tracking from farm to doorstep.</li>
          <li><strong>Scalability:</strong> Expand to multiple regions and diverse categories.</li>
        </ul>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2>System Features</h2>
        <div className="feature-grid">
          <div className="feature-card">
            <h3>User Authentication</h3>
            <p>Secure login and role-based access for farmers, customers, and admins.</p>
          </div>
          <div className="feature-card">
            <h3>Product Management</h3>
            <p>Farmers can easily list, manage, and track their products.</p>
          </div>
          <div className="feature-card">
            <h3>Order & Cart</h3>
            <p>Customers can browse, add to cart, and track their orders.</p>
          </div>
          <div className="feature-card">
            <h3>Delivery Timeline</h3>
            <p>Real-time delivery tracking with estimated arrival times.</p>
          </div>
          <div className="feature-card">
            <h3>Admin Dashboard</h3>
            <p>Admins manage users, products, and monitor transactions.</p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="workflow">
        <h2>How It Works</h2>
        <ol>
          <li>Farmers register and list their products.</li>
          <li>Customers browse and order fresh farm goods.</li>
          <li>Payments are securely processed.</li>
          <li>Products are delivered directly to the customer’s doorstep.</li>
        </ol>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>© {new Date().getFullYear()} Farm2Door | Fresh from Farm to Doorstep</p>
      </footer>
    </div>
  );
}

export default App;
