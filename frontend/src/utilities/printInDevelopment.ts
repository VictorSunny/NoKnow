function printInDevelopment(message: any): void {
  if (process.env.NODE_ENV == "development") {
    console.log(String(message));
  }
}
export default printInDevelopment;
