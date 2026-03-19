interface EnvImport {
  readonly VITE_BACKEND_HOSTNAME: string;
  readonly VITE_ACCOUNT_SUSPENDED_ERROR_CODE: string;
  readonly VITE_NOT_ADMIN_ERROR_CODE: string;
  readonly VITE_DEBUG: boolean;
}
interface ImportMeta {
  readonly env: EnvImport;
}
