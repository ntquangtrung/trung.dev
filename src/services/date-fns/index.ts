import { format } from "date-fns";

export class DateFnsService {
  readonly date: Date;
  readonly formattedDate: string;

  constructor(dateString: string) {
    this.date = new Date(dateString);
    this.formattedDate = format(this.date, "dd-MM-yyyy");
  }
}
