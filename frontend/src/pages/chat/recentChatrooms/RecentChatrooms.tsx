import { useEffect, useState } from "react";

import { ChatroomListResponse, ChatroomListResponseSchema } from "../../../schemas/ChatSchemas";
import useAxios from "../../../hooks/useAxios";
import useGetRecentChatrooms from "../../../hooks/useGetRecentChatrooms";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import useHandleError from "../../../hooks/useHandleError";
import NoDataSignal from "../../../components/general/modals/NoDataModal";
import FetchErrorSignal from "../../../components/general/modals/FetchErrorModal";
import { ChatroomCard } from "../../../components/pageComponents/chatComponents/ChatroomPages";

export default function RecentlyVisitedChatrooms() {
  const { recentlyVisitedRoomsUIDs } = useGetRecentChatrooms();
  const [isFetching, setIsFetching] = useState(false);
  const [recentlyVisitedRooms, setRecentlyVisitedRooms] = useState<ChatroomListResponse>();
  const axios = useAxios();

  const [errorMessage, setErrorMessage] = useState<string>();
  const apiErrorHandler = useHandleError();

  const _ = useSetPageTitle("recently engaged");

  useEffect(() => {
    if (recentlyVisitedRoomsUIDs) {
      setIsFetching(true);
      axios
        .get(`/chat/all?id=${recentlyVisitedRoomsUIDs}`)
        .then((res) => {
          const parsedData = ChatroomListResponseSchema.parse(res.data);
          setRecentlyVisitedRooms(parsedData);
        })
        .catch((err) => {
          apiErrorHandler({ err, setErrorMessage });
        })
        .finally(() => {
          setIsFetching(false);
        });
    }
  }, [recentlyVisitedRoomsUIDs]);

  return (
    <div className="page-container recent-chatrooms-page">
      <div className="section grow">
        {(recentlyVisitedRooms &&
          recentlyVisitedRooms.chatrooms?.map((chatroomDetails) => {
            return <ChatroomCard key={chatroomDetails.uid} chatroomDetails={chatroomDetails} />;
          })) ||
          (!isFetching && !recentlyVisitedRooms && errorMessage && (
            <FetchErrorSignal errorMessage={errorMessage} />
          )) ||
          (!recentlyVisitedRoomsUIDs && <NoDataSignal expectedData="recently engaged chatroom" />)}
      </div>
    </div>
  );
}
