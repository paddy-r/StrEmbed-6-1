import matplotlib.pylab as plt
from matplotlib.widgets import Button


fig,ax = plt.subplots()
ax.plot([1,2,3],[10,20,30],'bo-')
axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
axback = plt.axes([0.51, 0.05, 0.1, 0.075])
bnext = Button(axnext, 'Next')
bback = Button(axback, 'Back')

(xm,ym),(xM,yM)=bnext.label.clipbox.get_points()

def on_press(event):

    if xm<event.x<xM and ym<event.y<yM:
        print("Button clicked, do nothing. This triggered event is useless.")
    else:
        print("canvas clicked and Button not clicked. Do something with the canvas.")
    print(event)
def on_button_clicked(event):
    print("button clicked, do something triggered by the button.")
    print(event)

bnext.on_clicked(on_button_clicked)
bback.on_clicked(on_button_clicked)
fig.canvas.mpl_connect('button_press_event', on_press)
plt.show()