from flask import Flask, request, render_template, redirect, Markup, send_from_directory, send_file
from PIL import Image
import urllib.request
import random
app = Flask(__name__)

# Układ zdjęć przy danej ilości zdjęć: (ilość w pierwszym rzędzi, drugim,trzecim)
uklad = [(1,0,0),(2,0,0),(2,1,0),(2,2,0),(3,2,0),(3,3,0),(2,3,2),(3,2,3)]

'''
Główny formularz wyboru
'''
@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        try:
            los = request.form["los"]
            los = 1
        except KeyError:
            los = 0
        resX = request.form["resX"]
        resY = request.form["resY"]
        zdjecia = []
        flaga = False
        for i in range(1,9):
            if request.form["url"+str(i)]:
                if flaga:
                    zdjecia.append(",")
                zdjecia.append(request.form["url"+str(i)])
                flaga = True
        if not resY:   
            resY="2048"
        if not resX:
            resX="2048"
        return redirect("mozaika?losowo="+str(los)+"&rozdzielczosc="+resX+"x"+resY+"&zdjecia="+"".join(zdjecia))
    return render_template("index.html")

'''
Funkcja mieszająca kolejność zdjęć
'''
def shuffle(zdjecia):
    for i in range(len(zdjecia)):
        rand = random.randrange(len(zdjecia))
        zdjecia[i], zdjecia[rand] = zdjecia[rand], zdjecia[i]


'''
funkcja tworząca mozikę
'''
def create_image(losowo, x, y, zdjecia):
    n = int((len(zdjecia) + 1) / 2)

    if losowo:
        shuffle(zdjecia)

    new_img = Image.new("RGB", (x, y), color=(255,255,255))
    x_off = 0
    y_off = 0
    max_y_off = 0
    j = 0   #kolumna
    k = 0   #rząd
    n_y = 3 - uklad[len(zdjecia)-1].count(0)
    for i in zdjecia:
        if j == uklad[len(zdjecia)-1][k]:
            if k == 0:
                y_off = 0
            j = 0
            k += 1
            y_off += int(y / n_y)
            x_off = 0
            if k == 2:
                y_off = max_y_off
        scale(x,y,i,uklad[len(zdjecia)-1][k],n_y)
        if k == 0:
            y_off = int(axis(y,n_y,i.size[1]))
        if k == 1:
            if max_y_off < y_off + i.size[1]:
                max_y_off = y_off + i.size[1]
        new_img.paste(i, (x_off, y_off))
        x_off += i.size[0]
        j += 1
    new_img.save("img/s.jpg")


'''
Funkcja zwracająca odległość zdjęcia do osi
'''
def axis(height, n_y, h):
    return ((height / n_y) - h)


'''
Skalowanie zdjęć
'''
def scale(width, height, img, n_x, n_y):
    if n_x > 0 and n_y > 0:
        img.thumbnail((width/n_x,height/n_y))
    elif n_x > 0:
        img.thumbnail((width/n_x,height))
    elif n_y > 0:
        img.thumbnail((width,height/n_y))
    else:
        img.thumbnail((width,height))



'''
Wyświetlanie mozaiki
'''
@app.route("/mozaika", methods=["GET"])
def mozaika():
    losowo = request.args.get("losowo", 0)
    rozdzielczosc = request.args.get("rozdzielczosc","2048x2048")
    zdjecia = request.args.get("zdjecia")
    (rozdzielczoscX, rozdzielczoscY) = rozdzielczosc.split("x")
    rozdzielczoscX = int(rozdzielczoscX)
    rozdzielczoscY = int(rozdzielczoscY)
    zdjecia = zdjecia.split(",")
    losowo = int(losowo)

    urls = list(map(urllib.request.urlopen,zdjecia))
    images = list(map(Image.open,urls))
    
    create_image(losowo, rozdzielczoscX, rozdzielczoscY, images)

    return send_file("img/s.jpg")


if __name__ == "__main__":
    app.run(debug=True)
