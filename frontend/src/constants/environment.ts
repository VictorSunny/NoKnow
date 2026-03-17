
export const FRONTEND_HOSTNAME = import.meta.env.BACKEND_SERVICE_NAME ?? "localhost"
export const FRONTEND_PORT = import.meta.env.BACKEND_SERVICE_PORT ?? "8000"

export const ACCOUNT_SUSPENDED_ERROR_CODE = import.meta.env.ACCOUNT_SUSPENDED_ERROR_CODE ?? "NOT_SET"
export const NOT_ADMIN_ERROR = import.meta.env.NOT_ADMIN_ERROR ?? "NOT_SET"