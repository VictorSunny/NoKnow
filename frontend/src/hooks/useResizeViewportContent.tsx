import { useEffect } from "react";

export default function useResizeViewportContent(onChange: () => void) {
  const root = document.getElementById("root");
  const html = document.documentElement;
  const addResizeVar = () => {
    const newHeight = `${window.visualViewport?.height}px`;
    document.documentElement.style.setProperty("--vh", newHeight);
    html.style.height = newHeight;
    onChange();
  };
  useEffect(() => {
    document.documentElement.style.setProperty("--vh", `${window.visualViewport?.height}px`);
    window.visualViewport?.addEventListener("resize", addResizeVar);
    if (root instanceof HTMLDivElement) {
      root.classList.toggle("resize-box");
    }

    return () => {
      document.documentElement.style.removeProperty("--vh");
      window.visualViewport?.removeEventListener("resize", addResizeVar);
      if (root instanceof HTMLDivElement) {
        root.classList.toggle("resize-box", false);
      }
    };
  });
}
