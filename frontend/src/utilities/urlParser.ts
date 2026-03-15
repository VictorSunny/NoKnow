const urlParser = (urlString: string): string => {
  ////    RETURNS CLASS THAT EXTRACTS HOSTNAME FROM FULL URLS

  const parsedUrl = String(new URL(urlString).hostname).toLowerCase();
  if (parsedUrl.slice(0, 3) === "www") {
    return parsedUrl.slice(4);
  } else {
    return parsedUrl;
  }
};

export default urlParser;
