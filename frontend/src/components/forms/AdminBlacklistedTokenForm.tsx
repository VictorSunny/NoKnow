import { AnimatePresence } from "framer-motion";
import { BlacklistedToken } from "../../schemas/BlacklistedRefreshTokenSchema";
import APIResponsePopup from "../general/modals/APIResponsePopup";
import { SetOptionalTextState } from "../../types/types";

type Props = {
  blacklistedTokenData?: BlacklistedToken;
  errorMessage: string | undefined;
  setErrorMessage: SetOptionalTextState;
};

export default function AdminBlacklistedTokenForm({
  blacklistedTokenData,
  errorMessage,
  setErrorMessage,
}: Props) {
  return (
    <>
      <form name="blacklisted-token-form" className="spaced-out-form">
        <div className="form-section form-main-content-container">
          <div className="input-container">
            <label htmlFor="jti">id</label>
            <input
              name="id"
              id="id"
              key="id"
              type="text"
              value={blacklistedTokenData?.id}
              disabled
            />
          </div>
          <div className="input-container">
            <label htmlFor="jti">jti</label>
            <input
              name="jti"
              id="jti"
              key="jti"
              type="text"
              placeholder="new@example.com"
              defaultValue={blacklistedTokenData?.jti}
              disabled
            />
          </div>
          <div className="input-container">
            <label htmlFor="created_at">created at</label>
            <input
              name="created_at"
              id="created_at"
              key="created_at"
              type="text"
              placeholder="new@example.com"
              defaultValue={blacklistedTokenData?.created_at}
              disabled
            />
          </div>
          <div className="input-container">
            <label htmlFor="exp">expiry</label>
            <input
              name="exp"
              id="exp"
              key="exp"
              type="text"
              placeholder="new@example.com"
              defaultValue={blacklistedTokenData?.exp}
              disabled
            />
          </div>
          <div className="input-container">
            <label htmlFor="expired">expired</label>
            <input
              name="expired"
              id="expired"
              key="expired"
              type="text"
              placeholder="new@example.com"
              value={(blacklistedTokenData?.expired && "yes") || "no"}
              disabled
            />
          </div>
        </div>
      </form>
      <AnimatePresence>
        {errorMessage && (
          <APIResponsePopup popupType="fail" message={errorMessage} setMessage={setErrorMessage} />
        )}
      </AnimatePresence>
    </>
  );
}
