interface EnvImport {
  readonly BACKEND_SERVICE_NAME: string
  readonly BACKEND_SERVICE_PORT: string
  readonly ACCOUNT_SUSPENDED_ERROR_CODE: string
  readonly NOT_ADMIN_ERROR: string
}
interface ImportMeta {
  readonly env: EnvImport
}