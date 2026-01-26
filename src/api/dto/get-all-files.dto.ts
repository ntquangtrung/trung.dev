export interface ApiEntry {
  FullPath: string;
  Crtime: string;
  Mime: string;
}

export interface ApiResponse {
  ShouldDisplayLoadMore: boolean;
  LastFileName: string;
  Entries: Array<ApiEntry>;
}

export class FileEntryDto {
  readonly fullPath: string;
  readonly createdTime: string;
  readonly type: string;

  constructor(data: ApiEntry) {
    this.fullPath = `${import.meta.env.VITE_API_BASE_URL}${data.FullPath}`;
    this.createdTime = data.Crtime;
    this.type = data.Mime;
  }
}

export class GetAllFilesDto {
  readonly files: FileEntryDto[];
  readonly hasMore: boolean;
  readonly lastFileName: string;

  constructor(data: ApiResponse) {
    this.files = data.Entries.map((entry) => new FileEntryDto(entry));
    this.hasMore = data.ShouldDisplayLoadMore;
    this.lastFileName = data.LastFileName;
  }
}
