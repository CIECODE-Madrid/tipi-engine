from sparkpost import SparkPost


class emailScrap(object):

    @staticmethod
    def send_mail( message, title):
        sp = SparkPost("f70be647f745f194cc0ccf68ee88ad96b10e3e17")
        doc = message
        response = sp.transmissions.send(
            recipients=["javier.perez@ciecode.es","pablo.martin@enreda.coop","quique@enreda.coop"],  # email is a user's email
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
