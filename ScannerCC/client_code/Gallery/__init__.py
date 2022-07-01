from ._anvil_designer import GalleryTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Gallery(GalleryTemplate):
  def refresh_photo(self):
    # Load existing articles from the Data Table, and display them in the RepeatingPanel
    self.photo_panel.items = anvil.server.call('get_photo')
    
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.refresh_photo()

  