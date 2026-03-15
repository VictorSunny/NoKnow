import axios from "axios";

export default function useCreateAxiosInstance() {
  const axiosInstance = axios.create({
    baseURL: "http://localhost:8000",
    headers: {
      "Content-Type": "application/json",
    },
    withCredentials: true,
  });
  return axiosInstance;
}
