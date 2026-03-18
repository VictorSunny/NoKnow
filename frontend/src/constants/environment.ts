export const BACKEND_HOSTNAME = import.meta.env.VITE_BACKEND_SERVICE_NAME ?? "localhost";
export const BACKEND_PORT = import.meta.env.VITE_BACKEND_SERVICE_PORT ?? "8000";

export const ACCOUNT_SUSPENDED_ERROR_CODE =
  import.meta.env.VITE_ACCOUNT_SUSPENDED_ERROR_CODE ?? "NOT_SET";
export const NOT_ADMIN_ERROR = import.meta.env.VITE_NOT_ADMIN_ERROR ?? "NOT_SET";
