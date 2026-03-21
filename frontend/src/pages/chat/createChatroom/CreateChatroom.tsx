import { useState } from "react";
import CreateChatroomForm from "../../../components/forms/CreateChatroomForm";
import { CHATROOM_PRIVACY_OPTIONS } from "../../../schemas/ChatSchemas";
import { useParams } from "react-router-dom";
import useSetPageTitle from "../../../hooks/useSetPageTitle";
import { ChatroomPrivatePublicTypes } from "../../../types/chatroomTypes";

export default function CreateChatroom() {
  const { chatroomType } = useParams();
  const [roomType, setSelectedChatroomType] = useState(chatroomType as ChatroomPrivatePublicTypes);
  if (!CHATROOM_PRIVACY_OPTIONS.includes(roomType)) {
    setSelectedChatroomType("public");
  }
  const _ = useSetPageTitle(`create ${roomType} chatroom`);

  return (
    <div className="page-container create-chatroom-page">
      <div className="section grow">
        <CreateChatroomForm chatroomType={roomType} />
      </div>
    </div>
  );
}
