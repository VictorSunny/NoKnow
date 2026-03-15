////    RETURNS CLASS THAT FOMATS LONG NUMBERS INTO READABLE COMMA SEPERATED VALUES

const numberGrouper = new Intl.NumberFormat("en-US", {
  notation: "standard",
});

export default numberGrouper;
