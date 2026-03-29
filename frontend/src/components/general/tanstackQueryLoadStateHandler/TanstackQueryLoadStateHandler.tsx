import { useEffect, useState } from "react";
import useHandleError from "../../../hooks/useHandleError";
import { InfiniteData } from "@tanstack/react-query";
import ReloadSignal from "../modals/ReloadModal";
import SpinnerLoader from "../loaders/SpinnerLoader";
import { AxiosError } from "axios";

type TanstackStateHandlerProps = {
  refetch: () => void;
  isFetching: boolean;
  isFetchingNextPage: boolean;
  isError: boolean;
  error: Error | null;
  data: InfiniteData<any, unknown> | undefined;
};
export default function TanstackQueryLoadStateHandler({
  refetch,
  isError,
  isFetching,
  isFetchingNextPage,
  error,
  data,
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
      {(isFetching && !isFetchingNextPage && !isError && !data?.pages && (
        <div className="page-container">
          <SpinnerLoader />
        </div>
      )) ||
        (isError && !isFetching && (
          <div className="page-container">
            <ReloadSignal
              isFetching={isFetching}
              isFetchingNextPage={isFetchingNextPage}
              refreshClickFn={refetch}
              hideRefreshButton={error instanceof AxiosError && (error.status == 401 || error.status == 403) }
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
