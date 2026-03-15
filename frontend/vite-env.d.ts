interface EnvImport {
  readonly BACKEND_SERVICE_NAME: string
  readonly BACKEND_SERVICE_PORT: string
}
interface ImportMeta {
  readonly env: EnvImport
}