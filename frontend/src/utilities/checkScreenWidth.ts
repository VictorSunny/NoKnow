function checkScreenWidth() {
  const scales = {
    MOBILE: 480,
    TABLET: 768,
    DESKTOP: 992,
  };

  const deviceWidth: number = screen.width;

  const isMobile = deviceWidth <= scales.MOBILE;
  const isTablet = deviceWidth > scales.MOBILE && deviceWidth < scales.DESKTOP;
  const isDesktop = deviceWidth >= scales.DESKTOP;

  const values = {
    isMobile: isMobile,
    isTablet: isTablet,
    isDesktop: isDesktop,
  };

  return values;
}

export default checkScreenWidth;
