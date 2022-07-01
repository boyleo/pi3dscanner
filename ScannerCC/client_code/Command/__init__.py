from ._anvil_designer import CommandTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Command(CommandTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def bt_send_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("send_command", self.command_box.text)

  def bt_shoot_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("send_command", "shoot")

  def bt_get_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("send_command", "get")

  def bt_update_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("send_command", "update")

  def bt_Exit_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("send_command", "exit")

  def bt_Shutdown_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("send_command", "shutdown")

  def bt_Cleanup_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("send_command", "cleanup")

  def bt_GetAll_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("send_command", "getall")

  def bt_Stop_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("send_command", "stop")

  def primary_color_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("send_command", "shoot")

  def form_show(self, **event_args):
    """This method is called when the HTML panel is shown on the screen"""
    pass















