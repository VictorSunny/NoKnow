export type Message = {
  sender_username: string;
  content: string;
  type: string;
  created_at: string;
};

export type MessageList = {
  chatroom_type: string;
  messages: Message[];
};

export const userInfo = {
  first_name: "victor",
  last_name: "sunny",
  username: "dbm",
  email: "victor@dbm.xyz",
  bio: "here for the gist",
  joined: "2025-10-02T10:58:36.392302Z",
};

export const roomCreatedResponse = {
  uid: "bd99917b-9e40-4e6c-bc8e-e45a539b07f8",
  name: "ragdolls",
  created_at: "2025-10-02T00:00:00",
  creator: "tyler",
  room_type: "public",
};

export const recentlyVisitedRooms = [
  {
    uid: "bd99917b-9e40-4e6c-bc8e-e45a539b0td8",
    name: "ragdolls",
    created_at: "2024-10-02T00:00:00",
    creator: "tyler",
    room_type: "public",
  },
  {
    uid: "bd99917b-9e40-4e6c-bc8e-e45a539b023w",
    name: `the people's choice`,
    created_at: "2025-04-02T00:00:00",
    creator: "blackjohn",
    room_type: "public",
  },
  {
    uid: "bd99917b-9e40-4e6c-bc8e-e45a539b053r",
    name: "vips onlu",
    created_at: "2025-14-22T00:00:00",
    creator: "whitelion",
    room_type: "private",
  },
  {
    uid: "bd99917b-9e40-4e6c-bc8e-e45a539btrd54",
    name: "ragdolls",
    created_at: "2025-02-04T00:00:00",
    creator: "tyler",
    room_type: "public",
  },
];

export const publicRoomMessages: MessageList = {
  chatroom_type: "public",
  messages: [
    {
      sender_username: "pinkpanther",
      content: "jbjn",
      type: "user",
      created_at: "2025-09-15T11:35:16.785936Z",
    },
    {
      sender_username: "pinkpanther",
      content: "jbjn",
      type: "user",
      created_at: "2025-09-15T11:37:01.751759Z",
    },
    {
      sender_username: "pinkpanther",
      content: "hey",
      type: "user",
      created_at: "2025-09-15T11:43:23.197011Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hi",
      type: "user",
      created_at: "2025-09-15T11:43:34.552355Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hi",
      type: "user",
      created_at: "2025-09-15T13:42:44.558564Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hi",
      type: "user",
      created_at: "2025-09-15T13:42:52.430391Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hi",
      type: "user",
      created_at: "2025-09-15T13:42:55.506984Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hit",
      type: "user",
      created_at: "2025-09-15T13:43:08.583030Z",
    },
    {
      sender_username: "whitelion",
      content: "hello thor",
      type: "user",
      created_at: "2025-09-17T23:46:56.221910Z",
    },
    {
      sender_username: "pinkpanther",
      content: "fnkf",
      type: "user",
      created_at: "2025-09-17T23:48:57.946235Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hello",
      type: "user",
      created_at: "2025-09-17T23:52:48.846150Z",
    },
    {
      sender_username: "whitelion",
      content: "hello thor",
      type: "user",
      created_at: "2025-09-17T23:53:36.608977Z",
    },
    {
      sender_username: "thor",
      content: "hey",
      type: "user",
      created_at: "2025-09-17T23:54:20.021625Z",
    },
    {
      sender_username: "whitelion",
      content: "this is going well",
      type: "user",
      created_at: "2025-09-17T23:54:29.226459Z",
    },
    {
      sender_username: "thor",
      content: "indeed",
      type: "user",
      created_at: "2025-09-17T23:54:35.226460Z",
    },
    {
      sender_username: "whitelion",
      content: "hr",
      type: "user",
      created_at: "2025-09-17T23:56:53.868806Z",
    },
    {
      sender_username: "whitelion",
      content: "hello",
      type: "user",
      created_at: "2025-09-17T23:59:13.738242Z",
    },
    {
      sender_username: "whitelion",
      content: "this is it",
      type: "user",
      created_at: "2025-09-17T23:59:20.343126Z",
    },
    {
      sender_username: "whitelion",
      content: "jeu",
      type: "user",
      created_at: "2025-09-18T00:00:32.766720Z",
    },
    {
      sender_username: "thor",
      content: "seperate room",
      type: "user",
      created_at: "2025-09-18T00:06:23.942551Z",
    },
    {
      sender_username: "whitelion",
      content: "that message couldn't send because the database was not running",
      type: "user",
      created_at: "2025-09-18T19:20:40.341730Z",
    },
    {
      sender_username: "whitelion",
      content: "now it works",
      type: "user",
      created_at: "2025-09-18T19:20:52.555767Z",
    },
    {
      sender_username: "thor",
      content: "sounds good",
      type: "user",
      created_at: "2025-09-18T19:21:11.243995Z",
    },
    {
      sender_username: "whitelion",
      content: "i'm leaving",
      type: "user",
      created_at: "2025-09-18T19:21:45.914252Z",
    },
  ],
};
export const privateRoomMessages: MessageList = {
  chatroom_type: "private",
  messages: [
    {
      sender_username: "pinkpanther",
      content: "jbjn",
      type: "user",
      created_at: "2025-09-15T11:35:16.785936Z",
    },
    {
      sender_username: "pinkpanther",
      content: "jbjn",
      type: "user",
      created_at: "2025-09-15T11:37:01.751759Z",
    },
    {
      sender_username: "pinkpanther",
      content: "hey",
      type: "user",
      created_at: "2025-09-15T11:43:23.197011Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hi",
      type: "user",
      created_at: "2025-09-15T11:43:34.552355Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hi",
      type: "user",
      created_at: "2025-09-15T13:42:44.558564Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hi",
      type: "user",
      created_at: "2025-09-15T13:42:52.430391Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hi",
      type: "user",
      created_at: "2025-09-15T13:42:55.506984Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hit",
      type: "user",
      created_at: "2025-09-15T13:43:08.583030Z",
    },
    {
      sender_username: "whitelion",
      content: "hello thor",
      type: "user",
      created_at: "2025-09-17T23:46:56.221910Z",
    },
    {
      sender_username: "pinkpanther",
      content: "fnkf",
      type: "user",
      created_at: "2025-09-17T23:48:57.946235Z",
    },
    {
      sender_username: "hiddentiger",
      content: "hello",
      type: "user",
      created_at: "2025-09-17T23:52:48.846150Z",
    },
    {
      sender_username: "whitelion",
      content: "hello thor",
      type: "user",
      created_at: "2025-09-17T23:53:36.608977Z",
    },
    {
      sender_username: "thor",
      content: "hey",
      type: "user",
      created_at: "2025-09-17T23:54:20.021625Z",
    },
    {
      sender_username: "whitelion",
      content: "this is going well",
      type: "user",
      created_at: "2025-09-17T23:54:29.226459Z",
    },
    {
      sender_username: "thor",
      content: "indeed",
      type: "user",
      created_at: "2025-09-17T23:54:35.226460Z",
    },
    {
      sender_username: "whitelion",
      content: "hr",
      type: "user",
      created_at: "2025-09-17T23:56:53.868806Z",
    },
    {
      sender_username: "whitelion",
      content: "hello",
      type: "user",
      created_at: "2025-09-17T23:59:13.738242Z",
    },
    {
      sender_username: "whitelion",
      content: "this is it",
      type: "user",
      created_at: "2025-09-17T23:59:20.343126Z",
    },
    {
      sender_username: "whitelion",
      content: "jeu",
      type: "user",
      created_at: "2025-09-18T00:00:32.766720Z",
    },
    {
      sender_username: "thor",
      content: "seperate room",
      type: "user",
      created_at: "2025-09-18T00:06:23.942551Z",
    },
    {
      sender_username: "whitelion",
      content: "that message couldn't send because the database was not running",
      type: "user",
      created_at: "2025-09-18T19:20:40.341730Z",
    },
    {
      sender_username: "whitelion",
      content: "now it works",
      type: "user",
      created_at: "2025-09-18T19:20:52.555767Z",
    },
    {
      sender_username: "thor",
      content: "sounds good",
      type: "user",
      created_at: "2025-09-18T19:21:11.243995Z",
    },
    {
      sender_username: "whitelion",
      content: "i'm leaving",
      type: "user",
      created_at: "2025-09-18T19:21:45.914252Z",
    },
  ],
};
