import axios from "axios";
import { BACKEND_HOSTNAME, BACKEND_PORT } from "../constants/environment";


const BACKEND_SERVICE_BASE_URL = `http://${BACKEND_HOSTNAME}:${BACKEND_PORT}`;

export default axios.create({
  baseURL: BACKEND_SERVICE_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});
