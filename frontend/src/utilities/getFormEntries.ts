export default function getFormEntries(formTarget: HTMLFormElement & EventTarget) {
  const formData = new FormData(formTarget);
  const formEntries = Object.fromEntries(formData.entries());
  return formEntries;
}
