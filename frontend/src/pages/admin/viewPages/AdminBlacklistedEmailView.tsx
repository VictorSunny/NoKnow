import React, { useEffect, useState } from "react";
import BlacklistedEmailForm from "../../../components/forms/AdminBlacklistedEmailForm";
import { BlacklistedEmail, BlacklistedEmailSchema } from "../../../schemas/BlacklistedEmailSchemas";
import { useParams } from "react-router-dom";
import useAxios from "../../../hooks/useAxios";
import useHandleError from "../../../hooks/useHandleError";
import { AdminDeleteUtilityNav } from "../../../components/adminPageComponents/navbars/general/AdminDeleteUtilityNav";

export default function AdminBlacklistedEmailView({ forUpdate }: { forUpdate?: boolean }) {
  const { id } = useParams();
  const [blacklisteEmail, setBlacklisteEmailData] = useState<BlacklistedEmail>();

  const axios = useAxios({ forAdmin: true });
  const apiErrorHandler = useHandleError();
  const [isFetching, setIsFetching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();

  useEffect(() => {
    if (forUpdate) {
      setIsFetching(true);
      axios
        .get(`/admin/email_blacklist?id=${id}`)
        .then((res) => {
          const parsedRes = BlacklistedEmailSchema.parse(res.data);
          setBlacklisteEmailData(parsedRes);
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        })
        .finally(() => {
          setIsFetching(false);
        });
    }
  }, []);
  return (
    <div className="page-container admin-blacklisted-email-view">
      {blacklisteEmail && (
        <div className="section util-container">
          <AdminDeleteUtilityNav id={blacklisteEmail.id} modelName="blacklistedEmail" />
        </div>
      )}
      <BlacklistedEmailForm
        forUpdate={forUpdate}
        blacklistedEmail={blacklisteEmail}
        setBlacklisteEmailData={setBlacklisteEmailData}
        errorMessage={errorMessage}
        setErrorMessage={setErrorMessage}
        isFetching={isFetching}
        setIsFetching={setIsFetching}
      />
    </div>
  );
}
