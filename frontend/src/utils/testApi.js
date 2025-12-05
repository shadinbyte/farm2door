import authService from "../services/authService";
import productService from "../services/productService";

export const testApiConnection = async () => {
  console.log("🧪 Testing API Connection...\n");

  try {
    // Test 1: Health Check
    console.log("1️⃣ Testing health endpoint...");
    const healthResponse = await fetch("http://localhost:8000/health/");
    const healthData = await healthResponse.json();
    console.log("✅ Health Check:", healthData.status);

    // Test 2: Get Categories
    console.log("\n2️⃣ Testing categories endpoint...");
    const categories = await productService.getCategories();
    console.log(`✅ Categories loaded: ${categories.length} categories`);

    // Test 3: Get Products
    console.log("\n3️⃣ Testing products endpoint...");
    const products = await productService.getProducts();
    console.log(
      `✅ Products loaded: ${
        products.results?.length || products.length
      } products`
    );

    console.log("\n✅ All API tests passed!");
    return true;
  } catch (error) {
    console.error("\n❌ API Test Failed:", error.message);
    if (error.response) {
      console.error("Response data:", error.response.data);
      console.error("Status:", error.response.status);
    }
    return false;
  }
};
