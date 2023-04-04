import wx, sys, os
# from strembed import gui, embed_images, occ_patch_manual
from strembed import gui


if __name__ == "__main__":

    # MAIN APP BIT
    app = wx.App()
    frame = gui.MainWindow()

    frame.Show()
    # frame.SetTransparent(220)
    frame.Maximize()

    app.MainLoop()