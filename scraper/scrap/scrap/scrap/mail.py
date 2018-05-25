from sparkpost import SparkPost


class emailScrap(object):

    def __init__(self, apikey=''):
        self.apikey = apikey

    def send_mail( message, title):
        sp = SparkPost(self.apikey)
        doc = message
        response = sp.transmissions.send(
            recipients=["javier.perez@ciecode.es","pablo.martin@ciecode.es"],  # email is a user's email
            html=doc,
            from_email="scrap@tipiciudadano.es",
            subject=title,
            attachments=[
                            {
                                "name": "failed.log",
                                "type": "text/plain",
                                "filename": "failed.log"
                            }
                        ],
        )

        print "reporting..."
