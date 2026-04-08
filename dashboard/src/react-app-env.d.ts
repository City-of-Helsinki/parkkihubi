/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_MAP_CENTER_COORDS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
