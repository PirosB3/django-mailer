from oauth2client.client import flow_from_clientsecrets


def main():
    flow = flow_from_clientsecrets(
        './client_secret.json',
        scope=[
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.compose'
        ],
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )
    print "Please go to '%s' and authorize this application" % flow.step1_get_authorize_url()
    print "Insert the code in the 'Success' screen and press ENTER"

    code = raw_input()
    credentials = flow.step2_exchange(code)

    from oauth2client.file import Storage
    storage = Storage('./gmail.storage')
    storage.put(credentials)


if __name__ == '__main__':
    main()
