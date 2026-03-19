import axios from "axios";

export default function useCreateAxiosInstance() {
  const axiosInstance = axios.create({
    // for custom backend hostname
    // baseURL: VITE_BACKEND_HOSTNAME,

    // for reverse proxy
    baseURL: "/api",
    headers: {
      "Content-Type": "application/json",
    },
    withCredentials: true,
  });
  return axiosInstance;
}
