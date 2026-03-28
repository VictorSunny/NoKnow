import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { UUID } from "crypto";
import useHandleError from "../../../hooks/useHandleError";
import { UserComplete, UserCompleteSchema } from "../../../schemas/AuthSchema";
import useAxios from "../../../hooks/useAxios";
import AdminUserCompleteForm from "../../../components/forms/AdminUserCompleteForm";
import { AdminUserUtilityNavSection } from "../../../components/adminPageComponents/navbars/user/AdminUserNavbars";
import useGetLoggedInUser from "../../../hooks/useGetLoggedInUser";

export default function AdminUserView({ forUpdate }: { forUpdate?: boolean }) {
  const axios = useAxios({ forAdmin: true });
  const { userUID } = useParams();

  const apiErrorHandler = useHandleError();
  const [isFetching, setIsFetching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();
  const [userData, setUserData] = useState<UserComplete>();

  const loggedInUser = useGetLoggedInUser({ setErrorMessage });

  useEffect(() => {
    if (userUID) {
      setIsFetching(true);
      axios
        .get(`/admin/user?id=${userUID}`)
        .then((res) => {
          const parsedUserData = UserCompleteSchema.parse(res.data);
          setUserData(parsedUserData);
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        })
        .finally(() => {
          setIsFetching(false);
        });
    }
  }, [userUID, forUpdate]);

  return (
    <div className="page-container admin-user-view">
      {forUpdate && userData && loggedInUser && (
        <div className="section util-container">
          <nav>
            <AdminUserUtilityNavSection loggedInUser={loggedInUser} userData={userData} />
          </nav>
        </div>
      )}
      <div className="section grow">
        <AdminUserCompleteForm
          userUID={userUID as UUID}
          userData={userData}
          setUserData={setUserData}
          isFetching={isFetching}
          setIsFetching={setIsFetching}
          errorMessage={errorMessage}
          setErrorMessage={setErrorMessage}
          forUpdate={forUpdate}
        />
      </div>
    </div>
  );
}
