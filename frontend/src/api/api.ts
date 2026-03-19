import axios from "axios";

export default axios.create({
  // for reverse proxy
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});
