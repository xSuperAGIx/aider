class CoderPrompts:
    EDIT_MESSAGES: dict[str, str] = {
        "git_commit": "I committed the changes with git hash {hash} & commit msg: {message}",
        "no_edits": "I didn't see any properly formatted edits in your reply?!",
        "local_edits": "I edited the files myself.",
        "no_repo": "I updated the files.",
    }

    def get_edit_message(self, edit_type: str, **context: str) -> str:
        """Return the message for the given edit type and context.

        The context should contain the variables to be interpolated into the message.
        """
        message = self.EDIT_MESSAGES.get(edit_type)
        if message is None:
            raise ValueError(f"Unknown edit type: {edit_type}")
        return message.format(**context)



coder = CoderPrompts()
print(coder.get_edit_message("git_commit", hash="abc123", message="Add docstring"))
print(coder.get_edit_message("local_edits"))
print(coder.get_edit_message("no_repo"))


I
