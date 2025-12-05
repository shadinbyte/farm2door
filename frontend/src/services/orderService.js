import api from "./api";

const orderService = {
  // Create order
  createOrder: async (orderData) => {
    try {
      const response = await api.post("/orders/create/", orderData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get customer orders
  getMyOrders: async () => {
    try {
      const response = await api.get("/orders/my-orders/");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get order details
  getOrderDetails: async (orderNumber) => {
    try {
      const response = await api.get(`/orders/my-orders/${orderNumber}/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Cancel order
  cancelOrder: async (orderNumber) => {
    try {
      const response = await api.post(`/orders/${orderNumber}/cancel/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get order statuses
  getOrderStatuses: async () => {
    try {
      const response = await api.get("/orders/statuses/");
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export default orderService;
