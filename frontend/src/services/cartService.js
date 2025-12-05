import api from "./api";

const cartService = {
  // Get cart
  getCart: async () => {
    try {
      const response = await api.get("/orders/cart/");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Add to cart
  addToCart: async (productId, quantity) => {
    try {
      const response = await api.post("/orders/cart/add/", {
        product_id: productId,
        quantity: quantity,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Update cart item
  updateCartItem: async (itemId, quantity) => {
    try {
      const response = await api.put(`/orders/cart/items/${itemId}/update/`, {
        quantity: quantity,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Remove from cart
  removeFromCart: async (itemId) => {
    try {
      const response = await api.delete(`/orders/cart/items/${itemId}/remove/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Clear cart
  clearCart: async () => {
    try {
      const response = await api.delete("/orders/cart/clear/");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export default cartService;
