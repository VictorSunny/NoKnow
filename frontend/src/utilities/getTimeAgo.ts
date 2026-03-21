import { formatDistanceToNow } from "date-fns";
import { toZonedTime } from "date-fns-tz";

export default function getTimeAgo(dateString: string) {
  const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const zonedTime = toZonedTime(dateString, userTimeZone);
  const timeAgo = formatDistanceToNow(zonedTime, { addSuffix: true });
  return timeAgo;
}
