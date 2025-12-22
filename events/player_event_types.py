class PlayerEventType:
    START_MESSAGE_SENT = "start_message_sent"
    FINAL_MESSAGE_SENT = "final_message_sent"

    @staticmethod
    def location_opened(point_id: int) -> str:
        return f"location_opened:{point_id}"

    @staticmethod
    def hint_sent(point_id: int) -> str:
        return f"hint_sent:{point_id}"
