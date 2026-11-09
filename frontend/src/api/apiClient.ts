import axios from "axios";

export { axios };

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 120000,
});
