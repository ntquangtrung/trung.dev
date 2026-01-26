import type {
  IUppyService,
  UploadedFile,
  UppyEventHandlers,
  UppyLogger,
  UppyMeta,
  UppyServiceConfig,
} from "@/components/uppy/inteface";
import Uppy from "@uppy/core";
import Tus, { type TusBody, type TusDetailedError, type TusOpts } from "@uppy/tus";
import { v4 as uuidv4 } from "uuid";

// ============================================
// Default Implementations (OCP - easily swappable)
// ============================================
const defaultConfig: UppyServiceConfig = {
  autoProceed: false,
  restrictions: {
    maxNumberOfFiles: 30,
    allowedFileTypes: ["image/*", "video/*"],
  },
  tus: {
    endpoint: `${import.meta.env.VITE_SEAWEEDFS_BASE_URL}${import.meta.env.VITE_SEAWEEDFS_TUS_ENDPOINT}`,
    chunkSize: 50 * 1024 * 1024, // 50 MB
    retryDelays: [0, 1000, 3000, 5000, 10000, 30000],
    storeFingerprintForResuming: true,
    removeFingerprintOnSuccess: true,
    limit: 3,
  },
};

const debugLogger: UppyLogger = {
  debug: (..._args) => {},
  warn: (..._args) => {},
  error: (...args) => console.error("[uppy]", ...args),
};

// ============================================
// TusUppyService Class (SRP + DIP)
// ============================================
export class TusUppyService implements IUppyService {
  readonly uppy: Uppy<UppyMeta, TusBody>;
  private readonly logger: UppyLogger;
  private readonly eventHandlers: UppyEventHandlers;

  constructor(
    config: Partial<UppyServiceConfig> = {},
    eventHandlers: UppyEventHandlers = {},
    logger: UppyLogger = debugLogger
  ) {
    this.logger = logger;
    this.eventHandlers = eventHandlers;

    const mergedConfig = this.mergeConfig(config);

    this.uppy = this.createUppyInstance(mergedConfig);
    this.configureTusPlugin(mergedConfig.tus);
    this.registerEventHandlers();
  }

  private createUppyInstance(config: UppyServiceConfig): Uppy<UppyMeta, TusBody> {
    return new Uppy<UppyMeta, TusBody>({
      logger: this.logger,
      autoProceed: config.autoProceed,
      restrictions: config.restrictions,
      meta: {
        "Seaweed-Date-Added": new Date().toISOString(),
      },
      onBeforeFileAdded: (currentFile, _files) => {
        const uniqueName = uuidv4();
        return {
          ...currentFile,
          name: uniqueName,
          meta: {
            ...currentFile.meta,
            name: uniqueName,
            filename: uniqueName,
            "content-type": currentFile.meta.type,
          },
        };
      },
    });
  }

  private configureTusPlugin(tusConfig: UppyServiceConfig["tus"]): void {
    this.uppy.use(Tus<UppyMeta, TusBody>, {
      endpoint: tusConfig.endpoint,
      chunkSize: tusConfig.chunkSize,
      retryDelays: tusConfig.retryDelays,
      storeFingerprintForResuming: tusConfig.storeFingerprintForResuming,
      removeFingerprintOnSuccess: tusConfig.removeFingerprintOnSuccess,
      limit: tusConfig.limit,
      withCredentials: false,
      onShouldRetry: this.createRetryHandler,
    });
  }

  private createRetryHandler(
    err: TusDetailedError,
    _retryAttempt: number,
    _options: TusOpts<UppyMeta, TusBody>,
    next: (e: TusDetailedError) => boolean
  ) {
    const status = err?.originalResponse?.getStatus();
    // Don't retry on 4xx errors (except 409 conflict, 423 locked)
    if (status !== undefined && status >= 400 && status < 500 && status !== 409 && status !== 423) {
      return false;
    }
    return next(err);
  }

  private registerEventHandlers(): void {
    this.uppy.on("upload", () => {
      this.eventHandlers.onUploadStart?.();
    });

    this.uppy.on("progress", (progress) => {
      this.eventHandlers.onProgress?.(progress);
    });

    this.uppy.on("upload-success", (file) => {
      if (file === undefined) {
        return;
      }

      const uploadedFile: UploadedFile = {
        id: file.id,
        name: file.name ?? "unknown",
        url: "",
      };

      this.eventHandlers.onFileSuccess?.(uploadedFile);
    });

    this.uppy.on("upload-error", (file, error) => {
      this.eventHandlers.onFileError?.(file?.name ?? "unknown", error);
    });

    this.uppy.on("complete", (result) => {
      const successful: UploadedFile[] =
        result.successful?.map((f) => ({
          id: f.id,
          name: f.name ?? "unknown",
          url: "",
        })) ?? [];

      const failed = result.failed?.map((f) => f.name ?? "unknown") ?? [];

      this.eventHandlers.onComplete?.(successful, failed);
    });

    this.uppy.on("upload-retry", (fileId) => {
      this.eventHandlers.onRetry?.(fileId);
    });

    this.uppy.on("files-added", (files) => {
      this.eventHandlers.onFilesAdded?.(files);
    });
  }

  private mergeConfig(config: Partial<UppyServiceConfig>): UppyServiceConfig {
    return {
      ...defaultConfig,
      ...config,
      restrictions: {
        ...defaultConfig.restrictions,
        ...config.restrictions,
      },
      tus: {
        ...defaultConfig.tus,
        ...config.tus,
      },
    };
  }

  destroy(): void {
    this.uppy.destroy();
  }
}

// ============================================
// Factory Function (convenience)
// ============================================
export function createTusUppyService(
  config?: Partial<UppyServiceConfig>,
  eventHandlers?: UppyEventHandlers,
  logger?: UppyLogger
): TusUppyService {
  return new TusUppyService(config, eventHandlers, logger);
}
