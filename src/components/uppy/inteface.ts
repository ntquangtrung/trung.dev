import type Uppy from "@uppy/core";
import type { UppyFile } from "@uppy/core";
import type { TusBody } from "@uppy/tus";

// ============================================
// Meta & File Types
// ============================================
export type UppyMeta = {
  "Seaweed-Date-Added": string;
};

export interface UploadedFile {
  id: string;
  name: string;
  url: string;
}

// ============================================
// Configuration Interfaces (SRP + OCP)
// ============================================
export interface UppyRestrictions {
  maxNumberOfFiles?: number;
  maxFileSize?: number;
  allowedFileTypes?: string[];
}

export interface TusConfig {
  endpoint: string;
  chunkSize?: number;
  retryDelays?: number[];
  limit?: number;
  storeFingerprintForResuming?: boolean;
  removeFingerprintOnSuccess?: boolean;
}

export interface UppyServiceConfig {
  autoProceed?: boolean;
  restrictions?: UppyRestrictions;
  tus: TusConfig;
}

// ============================================
// Event Handler Interfaces (ISP)
// ============================================
export interface UppyEventHandlers {
  onUploadStart?: () => void;
  onProgress?: (progress: number) => void;
  onFileSuccess?: (file: UploadedFile) => void;
  onFileError?: (fileName: string, error: Error) => void;
  onComplete?: (successful: UploadedFile[], failed: string[]) => void;
  onRetry?: (fileId: UppyFile<UppyMeta, TusBody>) => void;
  onFilesAdded?: (files: UppyFile<UppyMeta, TusBody>[]) => void;
}

// ============================================
// Logger Interface (DIP) - matches Uppy's logger interface
// ============================================
export interface UppyLogger {
  debug(...args: unknown[]): void;
  warn(...args: unknown[]): void;
  error(...args: unknown[]): void;
}

// ============================================
// Service Interface (DIP + ISP)
// ============================================
export interface IUppyService {
  readonly uppy: Uppy<UppyMeta, TusBody>;
  destroy(): void;
}
