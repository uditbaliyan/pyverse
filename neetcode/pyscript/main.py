import pyjokes
from pyscript.web import page


def get_joke(event):
    page["div#jokes"].innerHTML = f"{pyjokes.get_joke()} 🥁"
