import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
      title: "Fresh Vegetables ",
      description: "Direct from local farms to your doorstep"
    },
    {
      image: "https://images.unsplash.com/photo-1444858291040-58f756a3bdd6?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1378",
      title: "Organic Fruits ",
      description: "100% natural and chemical-free"
    },
    {
      image: "https://images.unsplash.com/photo-1608753478723-494e2dc286f2?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170",
      title: "Fresh Dairy ",
      description: "Pure milk and dairy products from happy cows"
    }
  ];

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev === slides.length - 1 ? 0 : prev + 1));
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev === 0 ? slides.length - 1 : prev - 1));
  };

  const goToSlide = (index) => {
    setCurrentSlide(index);
  };

  // Auto slide every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      nextSlide();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app">
      {/* Navbar */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="nav-logo">
            <h2>🌱 Farm2Door</h2>
          </div>
          <ul className="nav-menu">
            <li className="nav-item">
              <a href="#home" className="nav-link">Home</a>
            </li>
            <li className="nav-item">
              <a href="#products" className="nav-link">Products</a>
            </li>
            <li className="nav-item">
              <a href="#about" className="nav-link">About</a>
            </li>
            <li className="nav-item">
              <a href="#contact" className="nav-link">Contact</a>
            </li>
            <li className="nav-item">
              <button className="nav-btn">Login</button>
            </li>
          </ul>
        </div>
      </nav>

      {/* Carousel Section */}
      <section className="carousel">
        <div
          className="carousel-container"
          style={{ transform: `translateX(-${currentSlide * 100}%)` }}
        >
          {slides.map((slide, index) => (
            <div key={index} className="carousel-slide">
              <img src={slide.image} alt={slide.title} />
              <div className="carousel-caption">
                <h3>{slide.title}</h3>
                <p>{slide.description}</p>
              </div>
            </div>
          ))}
        </div>
        <button className="carousel-btn carousel-btn-prev" onClick={prevSlide}>
          ‹
        </button>
        <button className="carousel-btn carousel-btn-next" onClick={nextSlide}>
          ›
        </button>
        <div className="carousel-indicators">
          {slides.map((_, index) => (
            <span
              key={index}
              className={`indicator ${index === currentSlide ? 'active' : ''}`}
              onClick={() => goToSlide(index)}
            ></span>
          ))}
        </div>
      </section>

      {/* Hero Section */}
      <section className="hero" id="home">
        <h1>Welcome to Farm2Door 🌿</h1>
        <p>
          Connecting farmers directly with customers for fresh, organic, and locally produced goods.
        </p>
        <button className="cta-btn">Shop Now 🛒</button>
      </section>

      {/* Objectives Section */}
      <section className="objectives">
        <h2>🎯 Our Objectives</h2>
        <ul>
          <li><strong>👨‍🌾 Direct Farmer-to-Customer Connection:</strong> Eliminate middlemen and ensure fair prices for farmers.</li>
          <li><strong>💰 Affordable & Fresh Products:</strong> Deliver organic goods at reasonable prices.</li>
          <li><strong>🛒 Digital Marketplace:</strong> Provide a modern e-commerce experience for agricultural products.</li>
          <li><strong>🚚 Efficient Delivery:</strong> Real-time tracking from farm to doorstep.</li>
          <li><strong>📈 Scalability:</strong> Expand to multiple regions and diverse categories.</li>
        </ul>
      </section>

      {/* Features Section */}
      <section className="features">
        <h2>✨ System Features</h2>
        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">🔐</div>
            <h3>User Authentication</h3>
            <p>Secure login and role-based access for farmers, customers, and admins.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📦</div>
            <h3>Product Management</h3>
            <p>Farmers can easily list, manage, and track their products.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🛒</div>
            <h3>Order & Cart</h3>
            <p>Customers can browse, add to cart, and track their orders.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📱</div>
            <h3>Delivery Timeline</h3>
            <p>Real-time delivery tracking with estimated arrival times.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Admin Dashboard</h3>
            <p>Admins manage users, products, and monitor transactions.</p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="workflow">
        <h2>🔄 How It Works</h2>
        <ol>
          <li>👨‍🌾 Farmers register and list their products.</li>
          <li>🛒 Customers browse and order fresh farm goods.</li>
          <li>💳 Payments are securely processed.</li>
          <li>🚚 Products are delivered directly to the customer's doorstep.</li>
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
