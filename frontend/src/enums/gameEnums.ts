export enum eGameCardNames {
    ROCKET = "ROCKET",
    IGNORE = "IGNORE",
    EVACUATION = "EVACUATION",
    BUNKER = "BUNKER"
}

export enum eGameRoomChangedTypes {
    USER_ADDED = "USER_ADDED",
    USER_REMOVED = "USER_REMOVED"
}

export enum eSocketEvent {
    //SETTINGS
    CONNECT = "connect",
    ERROR = "error",
    CONNECT_ERROR = "connect_error",
    DISCONNECTED = "disconnected",

    //USER
    REMOVE_USER = "remove_user",

    //ROOM
    JOIN_ROOM = "join_room",
    JOIN_EXISTING_ROOM = "join_existing_room",
    ROOM_JOINED = "room_joined",
    ROOM_CHANGED = "room_changed",
    ROOM_CLOSED = "room_closed",
    ROOM_CREATED = "room_created",

    //GAME
    START_GAME = "start_game",
    GAME_REDIRECT = "game_redirect",
}

export const eGameSocketEvent = {
    ON: {
        GAME_READY: "game_ready",
        GAME_WAIT_ROOM: "game_wait_room",
        GAME_JOINED_WAITING: "game_joined_waiting",
        ROUND_RESULT: "round_result",
        GAME_ENDED: "game_ended",
    },
    EMIT: {
        JOIN_GAME: "join_game",
        CARD_CHOSEN: "card_chosen",
    }
}

export enum eModes {
    SELECT = 'select',
    COOP = 'coop',
    CREATE = 'create',
    ROOM = 'room'
}