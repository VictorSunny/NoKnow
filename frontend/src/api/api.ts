import axios from "axios";
import { BACKEND_HOSTNAME, BACKEND_PORT } from "../constants/environment";


// const BACKEND_SERVICE_BASE_URL = `http://${BACKEND_HOSTNAME}:${BACKEND_PORT}`;

export default axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});
