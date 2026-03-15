import { randomInt } from "crypto";

export default function randomUserID(): number {
  const randomNumber = randomInt(100000, 999999);
  return randomNumber;
}
