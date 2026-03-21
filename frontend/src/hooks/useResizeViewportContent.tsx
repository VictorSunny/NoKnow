import { useEffect } from "react";

export default function useResizeViewportContent() {
  const root = document.getElementById("root");
  const addResizeVar = () => {
    document.documentElement.style.setProperty("--vh", `${window.visualViewport?.height}px`);
  };
  useEffect(() => {
    window.visualViewport?.addEventListener("resize", addResizeVar);
    if (root instanceof HTMLDivElement) {
      root.classList.toggle("resize-box");
    }

    return () => {
      window.visualViewport?.removeEventListener("resize", addResizeVar);
      if (root instanceof HTMLDivElement) {
        root.classList.toggle("resize-box", false);
      }
    };
  });
}
