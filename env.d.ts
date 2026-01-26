/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SEAWEEDFS_BASE_URL: string;
  readonly VITE_SEAWEEDFS_TUS_ENDPOINT: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
