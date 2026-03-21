import { toZonedTime } from "date-fns-tz";
import { DateTime } from "luxon";

export default function messageDateFormatter(dateString: string) {
  ////    RETURNS CLASS THAT FOMATS ISO STRING INTO READABLE DATE FORMAT
  // day-month-year
  const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const zonedTime = toZonedTime(dateString, userTimeZone).toISOString();
  const formattedDate = DateTime.fromISO(zonedTime).toFormat("h:mm a, MMM d");

  return formattedDate;
}
