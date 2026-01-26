import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from "axios";

export class HttpClient {
  protected readonly client: AxiosInstance;

  constructor(config?: AxiosRequestConfig) {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL,
      timeout: 10_000,
      headers: {
        "Content-Type": "application/json",
      },
      ...config,
    });
  }

  protected async request<TResponse, TRequest = unknown>(
    config: AxiosRequestConfig<TRequest>
  ): Promise<TResponse> {
    const response = await this.client.request<TResponse, AxiosResponse<TResponse>, TRequest>(
      config
    );
    return response.data;
  }

  protected get<TResponse>(url: string, config?: AxiosRequestConfig): Promise<TResponse> {
    return this.request<TResponse>({
      url,
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      ...config,
    });
  }

  protected post<TResponse, TRequest>(
    url: string,
    data: TRequest,
    config?: AxiosRequestConfig
  ): Promise<TResponse> {
    return this.request<TResponse, TRequest>({
      url,
      method: "POST",
      data,
      ...config,
    });
  }
}
