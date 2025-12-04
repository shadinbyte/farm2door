import { create } from "zustand";
import { persist } from "zustand/middleware";

const useCartStore = create(
  persist(
    (set, get) => ({
      items: [],
      coupon: null,

      // Add item to cart
      addItem: (product, quantity = 1) => {
        set((state) => {
          const existingItem = state.items.find(
            (item) => item.id === product.id
          );

          if (existingItem) {
            return {
              items: state.items.map((item) =>
                item.id === product.id
                  ? { ...item, quantity: item.quantity + quantity }
                  : item
              ),
            };
          }

          return {
            items: [...state.items, { ...product, quantity }],
          };
        });
      },

      // Remove item from cart
      removeItem: (productId) => {
        set((state) => ({
          items: state.items.filter((item) => item.id !== productId),
        }));
      },

      // Update item quantity
      updateQuantity: (productId, quantity) => {
        set((state) => ({
          items: state.items.map((item) =>
            item.id === productId
              ? { ...item, quantity: Math.max(1, quantity) }
              : item
          ),
        }));
      },

      // Clear cart
      clearCart: () => {
        set({ items: [], coupon: null });
      },

      // Apply coupon
      applyCoupon: (couponCode) => {
        // In real app, validate with backend
        set({ coupon: couponCode });
      },

      // Remove coupon
      removeCoupon: () => {
        set({ coupon: null });
      },

      // Get cart totals
      getCartTotals: () => {
        const state = get();
        const subtotal = state.items.reduce(
          (sum, item) => sum + item.price * item.quantity,
          0
        );

        const shipping = subtotal > 50 ? 0 : 5.99;
        const tax = subtotal * 0.08;
        const discount = state.coupon ? subtotal * 0.1 : 0; // 10% discount example
        const total = subtotal + shipping + tax - discount;

        return {
          subtotal,
          shipping,
          tax,
          discount,
          total,
          itemCount: state.items.reduce((sum, item) => sum + item.quantity, 0),
        };
      },
    }),
    {
      name: "cart-storage", // localStorage key
      partialize: (state) => ({ items: state.items, coupon: state.coupon }),
    }
  )
);

export default useCartStore;
