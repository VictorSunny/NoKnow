
export default function isAlNum(stringValue: string) {
  const confirm = /^[a-zA-Z0-9]+$/.test(stringValue)
  return confirm
}
