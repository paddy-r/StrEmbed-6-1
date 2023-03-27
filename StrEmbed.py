import wx, sys, os
# from strembed import gui, embed_images, occ_patch_manual
from strembed import gui
from strembed.utils import do_fixes


if __name__ == "__main__":

    # HR 24/03/23 Executable/script switch to avoid all this UNPLEASANTNESS
    if getattr(sys, 'frozen', False):
        print("\n# Running as executable... #")
    else:
        print("\n# Running as normal Python script... #")
        do_fixes()


    # MAIN APP BIT
    app = wx.App()
    frame = gui.MainWindow()

    frame.Show()
    # frame.SetTransparent(220)
    frame.Maximize()

    app.MainLoop()