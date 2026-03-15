import React, { useEffect, useState } from "react";
import {
  BlacklistedToken,
  BlacklistedTokenSchema,
} from "../../../schemas/BlacklistedRefreshTokenSchema";
import useAxios from "../../../hooks/useAxios";
import { useParams } from "react-router-dom";
import useHandleError from "../../../hooks/useHandleError";
import AdminBlacklistedTokenForm from "../../../components/forms/AdminBlacklistedTokenForm";
import LineLoadingSignal from "../../../components/general/fetchModals/LineLoadingModal";
import { AdminDeleteUtilityNav } from "../../../components/adminPageComponents/navbars/general/AdminDeleteUtilityNav";

export default function AdminBlacklistedTokenView() {
  const axios = useAxios({ forAdmin: true });
  const { id } = useParams();
  const [blacklistedToken, setBlacklistedToken] = useState<BlacklistedToken>();
  const [errorMessage, setErrorMessage] = useState<string>();
  const [isFetching, setIsFetching] = useState<boolean>(true);
  const apiErrorHandler = useHandleError();

  useEffect(() => {
    setIsFetching(true);
    axios
      .get(`/admin/token_blacklist?id=${id}`)
      .then((res) => {
        const parsedRes = BlacklistedTokenSchema.parse(res.data);
        setBlacklistedToken(parsedRes);
      })
      .catch((err) => {
        apiErrorHandler({ err, setErrorMessage });
      })
      .finally(() => {
        setIsFetching(false);
      });
  });

  return (
    <div className="page-container admin-blacklisted-token-view">
      {(isFetching && !blacklistedToken && <LineLoadingSignal />) || (
        <>
          {blacklistedToken && (
            <div className="section util-container">
              <AdminDeleteUtilityNav id={blacklistedToken.id} modelName="blacklistedToken" />
            </div>
          )}
          <AdminBlacklistedTokenForm
            blacklistedTokenData={blacklistedToken}
            setErrorMessage={setErrorMessage}
            errorMessage={errorMessage}
          />
        </>
      )}
    </div>
  );
}
