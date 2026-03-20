import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { UUID } from "crypto";
import { Chatroom, ChatroomSchema } from "../../../schemas/ChatSchemas";
import useHandleError from "../../../hooks/useHandleError";
import useAxios from "../../../hooks/useAxios";
import AdminChatroomCompleteForm from "../../../components/forms/AdminChatroomCompleteForm";
import { AdminDeleteUtilityNav } from "../../../components/adminPageComponents/navbars/general/AdminDeleteUtilityNav";
import useGetLoggedInUser from "../../../hooks/useGetLoggedInUser";

export default function AdminChatroomView({ forUpdate }: { forUpdate?: boolean }) {
  const axios = useAxios({ forAdmin: true });
  const { chatroomUID } = useParams();
  const [chatroomData, setChatroomData] = useState<Chatroom>();
  const apiErrorHandler = useHandleError();
  const [isFetching, setIsFetching] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();

  const loggedInUser = useGetLoggedInUser({ setErrorMessage });

  useEffect(() => {
    if (forUpdate) {
      setIsFetching(true);
      axios
        .get(`/admin/chat?id=${chatroomUID}`)
        .then((res) => {
          console.log(res.data);
          const parsedData = ChatroomSchema.parse(res.data);
          setChatroomData(parsedData);
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
    <div className="page-container admin-chatroom-view">
      {forUpdate && chatroomData && loggedInUser && (
        <div className="section util-container">
          <AdminDeleteUtilityNav id={chatroomData.uid} modelName="chatroom" />
        </div>
      )}
      <div className="section grow">
        <AdminChatroomCompleteForm
          chatroomUID={chatroomUID as UUID}
          chatroomData={chatroomData}
          isFetching={isFetching}
          errorMessage={errorMessage}
          setChatroomData={setChatroomData}
          setErrorMessage={setErrorMessage}
          setIsFetching={setIsFetching}
          forUpdate={forUpdate}
        />
      </div>
    </div>
  );
}
