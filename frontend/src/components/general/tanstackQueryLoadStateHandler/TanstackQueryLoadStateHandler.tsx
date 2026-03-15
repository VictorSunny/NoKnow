import LineLoadingSignal from "../fetchModals/LineLoadingModal";
import ReloadSignal from "../fetchModals/ReloadModal";
import { useEffect, useState } from "react";
import useHandleError from "../../../hooks/useHandleError";

type TanstackStateHandlerProps = {
  refetch: () => void;
  isFetching: boolean;
  isFetchingNextPage: boolean;
  isError: boolean;
  error: Error | null;
};
export default function TanstackQueryLoadStateHandler({
  refetch,
  isError,
  isFetching,
  isFetchingNextPage,
  error,
}: TanstackStateHandlerProps) {
  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  useEffect(() => {
    if (error) {
      apiErrorHandler({ err: error, setErrorMessage });
    }
  }, [error]);
  return (
    <>
      {(isFetching && !isFetchingNextPage && !isError && (
        <div className="page-container">
          <LineLoadingSignal />
        </div>
      )) ||
        (isFetching && !isFetchingNextPage && !isError && (
          <div className="page-container">
            <LineLoadingSignal />
          </div>
        )) ||
        (isError && !isFetching && (
          <div className="page-container">
            <ReloadSignal
              isFetching={isFetching}
              isFetchingNextPage={isFetchingNextPage}
              refreshClickFn={refetch}
            >
              {errorMessage}
            </ReloadSignal>
          </div>
        )) ||
        (isError && (
          <div className="page-container">
            <ReloadSignal
              isFetching={isFetching}
              isFetchingNextPage={isFetchingNextPage}
              refreshClickFn={refetch}
            >
              {errorMessage}
            </ReloadSignal>
          </div>
        ))}
    </>
  );
}
