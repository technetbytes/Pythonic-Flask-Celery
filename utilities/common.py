
def get_url(url, port, method):
    return f"{url}:{port}/{method}"

def get_complete_url(protocol, url, port, method):
    return f"{protocol}://{url}:{port}/{method}"#protocol + "://" + url +":"+ port +"/"+ method