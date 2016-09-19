import pdb
from sparkpost import SparkPost
from setting import API_SPARKPOST, FROM_EMAIL
from jinja2 import Environment, FileSystemLoader
import os

class emailSparkPost(object):

    @staticmethod
    def send_mail(email,listforuser):
        sp = SparkPost(API_SPARKPOST)
        doc = render_html_doc(listforuser)
        response = sp.transmissions.send(
            recipients=['quique@enreda.coop'],#email is a user's email
            html=doc,
            from_email=FROM_EMAIL,
            subject='Summary of new Tipis'
        )

def render_html_doc(items):
    DIR = os.path.dirname(os.path.abspath(__file__))+"/templates"
    j2_env = Environment(loader=FileSystemLoader(DIR),
                         trim_blocks=True)
    return j2_env.get_template('email.html').render(items=items)
