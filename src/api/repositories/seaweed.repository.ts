import type { ApiResponse } from "@/api/dto/get-all-files.dto";
import { GetAllFilesDto } from "@/api/dto/get-all-files.dto";
import { HttpClient } from "@/api/http-client";

interface GetAllFilesParams {
  limit?: number;
}

class SeaweedRepository extends HttpClient {
  private readonly resource: string;
  constructor() {
    super();
    this.resource = "/media-gallery/";
  }

  async getAllFiles(params?: GetAllFilesParams): Promise<GetAllFilesDto> {
    const response = await this.get<ApiResponse>(this.resource, { params });
    return new GetAllFilesDto(response);
  }
}
export default new SeaweedRepository();
