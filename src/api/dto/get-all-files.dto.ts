export interface ApiEntry {
  FullPath: string;
  Crtime: string;
}

export interface ApiResponse {
  ShouldDisplayLoadMore: boolean;
  Entries: Array<ApiEntry>;
}

export class FileEntryDto {
  fullPath: string;
  createdTime: string;

  constructor(data: ApiEntry) {
    this.fullPath = data.FullPath;
    this.createdTime = data.Crtime;
  }
}

export class GetAllFilesDto {
  files: FileEntryDto[];
  hasMore: boolean;

  constructor(data: ApiResponse) {
    this.files = data.Entries.map((entry) => new FileEntryDto(entry));
    this.hasMore = data.ShouldDisplayLoadMore;
  }
}
