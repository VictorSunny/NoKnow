import { UUID } from "crypto";

export default function useGetRecentChatrooms() {
  const storageKey = "recent_chatrooms";
  const recentlyVisitedRoomsUIDs = sessionStorage.getItem(storageKey)

  const updateRecentlyVisitedRoomsUIDs = (chatroomUID: UUID) => {
    if (recentlyVisitedRoomsUIDs) {
      const UIDList = recentlyVisitedRoomsUIDs.split(",");
      // check if uid already exists in recents list
      if (!UIDList.includes(chatroomUID)) {
        if (UIDList.length == 8) {
          UIDList.pop()
        }
        UIDList.push(chatroomUID);
        const refreshUIDList = UIDList.join(",");
        sessionStorage.setItem(storageKey, refreshUIDList);
      }
    } else {
      const firstUID = `${chatroomUID},`;
      sessionStorage.setItem(storageKey, firstUID);
    }
  };

  const value = {
    recentlyVisitedRoomsUIDs: recentlyVisitedRoomsUIDs,
    updateRecentlyVisitedRoomsUIDs: updateRecentlyVisitedRoomsUIDs,
  };

  // const value = undefined
  return value;
}
