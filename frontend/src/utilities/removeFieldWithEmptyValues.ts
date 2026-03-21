export default function removeFieldWithEmptyValues(data: Record<string, any>) {
  return Object.fromEntries(Object.entries(data).filter(([_, v]) => v != "" && v != null));
}
