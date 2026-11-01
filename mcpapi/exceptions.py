class ToolInputError(Exception):
    """
    Anticipated failure of a tool call caused by its arguments (unknown or ambiguous identifier, record not found);
    the message is passed on to the client
    """
