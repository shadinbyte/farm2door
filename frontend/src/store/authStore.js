import { create } from "zustand";
import { persist } from "zustand/middleware";
import authService from "../services/authService";

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      // Login
      login: async (credentials) => {
        try {
          const data = await authService.login(credentials);
          set({
            user: data.user,
            token: data.token,
            isAuthenticated: true,
          });
          return data;
        } catch (error) {
          throw error;
        }
      },

      // Register
      register: async (userData) => {
        try {
          const data = await authService.register(userData);
          set({
            user: data.user,
            token: data.token,
            isAuthenticated: true,
          });
          return data;
        } catch (error) {
          throw error;
        }
      },

      // Logout
      logout: () => {
        authService.logout();
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      // Update user profile
      updateProfile: async (userData) => {
        try {
          const data = await authService.updateProfile(userData);
          set({ user: data.user });
          return data;
        } catch (error) {
          throw error;
        }
      },

      // Initialize auth from localStorage
      initAuth: () => {
        const user = authService.getCurrentUser();
        const token = localStorage.getItem("token");

        if (user && token) {
          set({
            user,
            token,
            isAuthenticated: true,
          });
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
