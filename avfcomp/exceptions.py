class SweepingViewException(Exception):
    pass


class InvalidReplayError(SweepingViewException):
    def __init__(self, replay, message=None):
        super().__init__(
            "The replay file {} is invalid: {}".format(
                replay, message if message else "No details supplied"
            )
        )


class UnknownFormatVersionError(SweepingViewException):
    def __init__(self, replay, version):
        super().__init__(
            "The replay file {} is using a format version this library doesn't understand: {}".format(
                replay,
                version,
            )
        )


class MimeTypeNotImplemented(SweepingViewException):
    def __init__(self, mime_type):
        super().__init__(
            "The mime type {} is not supported by this library. Sorry!".format(
                mime_type,
            )
        )


class UnknownMimeType(SweepingViewException):
    def __init__(self, mime_type):
        from .mime_types import supported

        super().__init__(
            "Unknown mime type {}!\nAvailable mime types:\n".format(
                mime_type,
                "\n".join(supported()),
            )
        )