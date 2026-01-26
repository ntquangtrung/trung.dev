import { HttpClient } from "@/api/http-client";

interface UserLoginRequestBody {
  firstName: string;
  phoneNumber: string;
}

class UserRepository extends HttpClient {
  private readonly resource: string;
  constructor() {
    super();
    this.resource = "/api/v1/users";
  }

  async userLogin(body: UserLoginRequestBody): Promise<unknown> {
    const response = await this.post(this.resource, body);
    return response;
  }

  async adminLogin(body: UserLoginRequestBody): Promise<unknown> {
    const response = await this.post(`${this.resource}/admin`, body);
    return response;
  }
}
export default new UserRepository();
