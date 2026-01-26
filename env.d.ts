/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SEAWEEDFS_BASE_URL: string;
  readonly VITE_SEAWEEDFS_TUS_ENDPOINT: string;
  readonly VITE_API_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
