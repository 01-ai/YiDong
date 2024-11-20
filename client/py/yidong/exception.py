from yidong.model import Reply


class YDError(Exception):
    ...


class YDUnknownError(YDError):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


class YDInternalServerError(YDError):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


class YDInvalidReplyError(YDError):
    def __init__(self, reply):
        self.reply = reply


class YDInvalidAPIKeyError(YDError):
    ...


class YDResourceNotUploadedError(YDError):
    ...


def convert_reply_to_error(reply: Reply):
    if reply.code == 0:
        return YDInvalidReplyError(reply)
    if reply.code == 1001:
        raise YDInvalidAPIKeyError()
    elif reply.code == 2002:
        raise YDResourceNotUploadedError()
    else:
        raise YDUnknownError(reply.code, reply.message)
