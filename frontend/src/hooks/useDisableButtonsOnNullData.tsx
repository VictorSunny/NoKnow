import { InfiniteData } from "@tanstack/react-query";
import { useEffect, useState } from "react";

type hookProps = {
  pagesData: InfiniteData<any, unknown> | undefined;
};
export default function useDisableButtonsOnNullData({ pagesData }: hookProps) {
  const [queryButtonsDisabled, setQueryButtonsDisabled] = useState(true);
  useEffect(() => {
    (!pagesData?.pages || pagesData.pages.length < 1) && setQueryButtonsDisabled(true) ||
      setQueryButtonsDisabled(false);
  }, [pagesData]);
  return queryButtonsDisabled;
}
