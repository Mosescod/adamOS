class TelegramAdapter:
    def format(self, response: str, user_id: str) -> str:
        return f"🧱 {response}\n\n_(Your spiritual journey continues...)_"

class DiscordAdapter:
    def format(self, response: str, user_id: str) -> str:
        return f"```prolog\n{response}\n```\n<@{user_id}>"

class WebAdapter:
    def format(self, response: str, user_id: str) -> dict:
        return {
            "text": response,
            "html": f"<div class='adam-response'>{response}</div>"
        }