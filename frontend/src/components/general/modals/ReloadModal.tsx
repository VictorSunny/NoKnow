import "./styles/FetchModals.css";
import { ReactComponent as ErrorIcon } from "../../../assets/icons/fall-accident-icon.svg";

type Props = {
  refreshClickFn: () => void;
  children?: React.ReactNode;
  isFetching: boolean;
  isFetchingNextPage: boolean;
  hideRefreshButton?: boolean | undefined;
};

function ReloadSignal({
  refreshClickFn,
  isFetching,
  isFetchingNextPage,
  hideRefreshButton,
  children,
}: Props) {
  return (
    <div className="reload-signal signal-modal">
      <div>
        <ErrorIcon className="signal-icon signal-action-response-icon" aria-label="error sign" />
        <p>{children}</p>
        {!hideRefreshButton && (
          <button
            className="btn signal-btn"
            type="button"
            aria-label="try reload"
            onClick={refreshClickFn}
            disabled={isFetching || isFetchingNextPage}
          >
            {((isFetching || isFetchingNextPage) && "retrying") || "try again"}
          </button>
        )}
      </div>
    </div>
  );
}

export default ReloadSignal;
