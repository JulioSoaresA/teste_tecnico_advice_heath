from flask import Flask, render_template, request, redirect

app = Flask(__name__)

class Owner:
    def __init__(self, name):
        self.name = name

class Car:
    def __init__(self, owner, model, color):
        self.owner = owner
        self.model = model
        self.color = color


owner1 = Owner('João')
owner2 = Owner('Maria')
car1 = Car(owner1, 'Red', 'Fusca')
car2 = Car(owner2, 'Blue', 'Civic')
car3 = Car(owner1, 'Black', 'Gol')
list = [car1, car2, car3]


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', title='To-do List', cars=list)


@app.route('/new')
def new():
    return render_template('new.html', title='New')


@app.route('/create_car', methods=['POST'])
def create_car():
    owner = request.form['owner']
    model = request.form['model']
    color = request.form['color']
    if Owner(owner) not in list:
        owner = Owner(owner)
    car = Car(owner, model, color)
    list.append(car)
    return redirect('/')

app.run(port=8000, debug=True)