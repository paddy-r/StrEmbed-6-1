import wx
from strembed import StrEmbed
app = wx.App()
frame = StrEmbed.MainWindow()

frame.Show()
# frame.SetTransparent(220)
frame.Maximize()

app.MainLoop()