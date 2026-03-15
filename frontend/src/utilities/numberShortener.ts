const currencyShortener = (currencySymbol: string) => {
  ////    RETURNS CLASS THAT FOMATS LONG NUMBERS INTO SHORTENED CURRENCY VALUES

  const currency: string = String(currencySymbol).toUpperCase();

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency,
    notation: "compact",
    compactDisplay: "short",
    maximumFractionDigits: 2,
  });
};

export default currencyShortener;
