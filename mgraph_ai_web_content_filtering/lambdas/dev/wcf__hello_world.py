STR_FORMAT__RETURN_MESSAGE = "From WCF lambda code, hello {name}"
def run(event, context=None):
    return STR_FORMAT__RETURN_MESSAGE.format(name=event.get('name'))