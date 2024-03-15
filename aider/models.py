import re

KNOWN_TOKENS = {
    "gpt-3.5-turbo": 4,
    "gpt-4": 8,
}

def calculate_token_count(name: str) -> int:
    match = re.search(r"-([0-9]+)k", name)
    if match:
        return int(match.group(1))
    else:
        for model, tokens in KNOWN_TOKENS.items():
            if name.startswith(model):
                return tokens
    raise ValueError(f"Unknown context window size for model: {name}")

def set_prices(max_context_tokens: int) -> None:
    if max_context_tokens == 8:
        PROMPT_PRICE = 0.03
        COMPLETION_PRICE = 0.06
    elif max_context_tokens == 32:
        PROMPT_PRICE = 0.06
        COMPLETION_PRICE = 0.12
    else:
        PROMPT_PRICE = None
        COMPLETION_PRICE = None

class Model:
    """
    A class representing a language model.
    """
    always_available: bool = False
    use_repo_map: bool = False
    send_undo_reply: bool = False

    prompt_price: float = None
    completion_price: float = None

    def __init__(self, name: str):
        """
        Initialize the model object.
        """
        self.name = name
        max_context_tokens = calculate_token_count(name)
        self.max_context_tokens = max_context_tokens * 1024
        set_prices(max_context_tokens)

        if self.is_gpt4():
            self.edit_format = "diff"
            self.use_repo_map = True
            self.send_undo_reply = True

        if self.is_gpt35():
            self.edit_format = "whole"
            self.always_available = True

    def is_gpt4(self) -> bool:
        """
        Check if the model is GPT-4.
        """
        return self.name.startswith("gpt-4")

    def is_gpt35(self) -> bool:
        """
        Check if the model is GPT-3.5-turbo.
        """
        return self.name.startswith("gpt-3.5-turbo")

