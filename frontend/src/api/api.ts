import axios from "axios";

const HOSTNAME = import.meta.env.BACKEND_SERVICE_NAME ?? "localhost"
const PORT = import.meta.env.BACKEND_SERVICE_PORT ?? "8000"

const BACKEND_SERVICE_BASE_URL = `http://${HOSTNAME}:${PORT}`;

export default axios.create({
  baseURL: BACKEND_SERVICE_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});
