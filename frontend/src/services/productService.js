import api from "./api";

const productService = {
  // Get all products
  getProducts: async (params = {}) => {
    try {
      const response = await api.get("/products/", { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get product by slug
  getProduct: async (slug) => {
    try {
      const response = await api.get(`/products/${slug}/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get categories
  getCategories: async () => {
    try {
      const response = await api.get("/products/categories/");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get featured products
  getFeaturedProducts: async () => {
    try {
      const response = await api.get("/products/featured/");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Search products
  searchProducts: async (query) => {
    try {
      const response = await api.get("/products/search/suggestions/", {
        params: { q: query },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get products by farmer
  getFarmerProducts: async (farmerId) => {
    try {
      const response = await api.get(`/products/farmer/${farmerId}/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get products by category
  getCategoryProducts: async (categoryId) => {
    try {
      const response = await api.get(`/products/category/${categoryId}/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Toggle wishlist
  toggleWishlist: async (productId) => {
    try {
      const response = await api.post(
        `/products/${productId}/wishlist/toggle/`
      );
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get wishlist
  getWishlist: async () => {
    try {
      const response = await api.get("/products/wishlist/");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export default productService;
