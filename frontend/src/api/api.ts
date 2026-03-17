import axios from "axios";
import { FRONTEND_HOSTNAME, FRONTEND_PORT } from "../constants/environment";


const BACKEND_SERVICE_BASE_URL = `http://${FRONTEND_HOSTNAME}:${FRONTEND_PORT}`;

export default axios.create({
  baseURL: BACKEND_SERVICE_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});
