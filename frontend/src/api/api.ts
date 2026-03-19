import axios from "axios";
import { BACKEND_HOSTNAME } from "../constants/environment";


export default axios.create({
  // for custom backend hostname
  // baseURL: VITE_BACKEND_HOSTNAME,

  // for reverse proxy
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});
