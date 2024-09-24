from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func


app = Flask(__name__)
app.secret_key = 'todo-list-app'

# Configurando a URI de conexão com o MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://user:password@db:3306/todolistapp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    cars = db.relationship('Car', backref='owner', lazy=True)
    
    def __repr__(self):
        return f'<User {self.nickname}>'

    def set_password(self, password):
        """Armazena a senha como um hash"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash armazenado"""
        return check_password_hash(self.password_hash, password)

    def car_count(self):
        """Retorna a quantidade de carros que o usuário possui"""
        return len(self.cars)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.Enum('yellow', 'blue', 'gray', name='color_enum'), nullable=False)
    model = db.Column(db.Enum('hatch', 'sedan', 'convertible', name='model_enum'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @classmethod
    def get_colors(cls):
        return [('yellow', 'Yellow'), ('blue', 'Blue'), ('gray', 'Gray')]

    @classmethod
    def get_models(cls):
        return [('hatch', 'Hatch'), ('sedan', 'Sedan'), ('convertible', 'Convertible')]


@app.route('/', methods=['GET'])
def index():
    """Exibe a lista de usuários ordenada pelo número de carros que possuem"""
    # Subquery para contar o número de carros de cada usuário
    car_count_subquery = (
        db.session.query(
            Car.owner_id,
            func.count(Car.id).label('car_count')
        )
        .group_by(Car.owner_id)
        .subquery()
    )

    # Consulta principal que une a contagem de carros com os usuários
    users = (
        User.query
        .outerjoin(car_count_subquery, User.id == car_count_subquery.c.owner_id)
        .order_by(car_count_subquery.c.car_count.asc())  # Ordena pela contagem de carros em ordem decrescente
        .all()
    )
    return render_template('index.html', title='To-do List', users=users)


@app.route('/new_car')
def new_car():
    """Exibe o formulário para cadastro de um novo carro"""
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('index')))
    
    colors = Car.get_colors()
    models = Car.get_models()
    return render_template('new_car.html', title='New Car', colors=colors, models=models)


@app.route('/create_car', methods=['POST'])
def create_car():
    """Cria um novo carro no banco de dados"""
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('index')))
    
    # Obtém o ID do proprietário baseado no nickname do usuário logado
    owner = User.query.filter_by(nickname=session['usuario_logado']).first()
    
    if owner is None:
        flash('Usuário não encontrado.')
        return redirect(url_for('index'))

    # Contar quantos carros o usuário já tem
    car_count = owner.car_count()
    if car_count >= 3:
        flash('Você já tem 3 carros cadastrados. Limite atingido.')
        return redirect(url_for('index'))

    model = request.form['model']
    color = request.form['color']
    
    # Criação do novo carro com o owner_id correto
    new_car = Car(owner_id=owner.id, model=model, color=color)  # Ajuste aqui
    db.session.add(new_car)
    db.session.commit()
    
    flash('Carro cadastrado com sucesso!')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Exibe o formulário de cadastro de um novo usuário"""
    if request.method == 'POST':
        nickname = request.form['user']
        password = request.form['senha']

        # Verifica se o usuário já existe
        existing_user = User.query.filter_by(nickname=nickname).first()
        if existing_user:
            flash('Usuário já existe. Escolha outro nickname.')
            return redirect(url_for('register'))

        # Cria um novo usuário
        new_user = User(nickname=nickname)
        new_user.set_password(password)  # Armazena a senha de forma segura
        
        # Adiciona o novo usuário ao banco de dados
        db.session.add(new_user)
        db.session.commit()

        flash(f'Usuário {nickname} cadastrado com sucesso!')
        return redirect(url_for('login'))
    
    # Exibe o formulário de cadastro
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Exibe o formulário de login e autentica o usuário"""
    if request.method == 'POST':
        nickname = request.form['user']
        password = request.form['senha']
        user = User.query.filter_by(nickname=nickname).first()

        if user and user.verify_password(password):
            session['usuario_logado'] = user.nickname
            flash(f'{user.nickname} logado com sucesso!')
            next_page = request.form.get('next', url_for('index'))
            return redirect(next_page)
        else:
            flash('Usuário ou senha incorretos.')
            return redirect(url_for('login'))

    # Para requisições GET, apenas renderiza o template de login
    next_page = request.args.get('next')
    return render_template('login.html', next=next_page)


@app.route('/dashboard')
def dashboard():
    """Exibe a página de dashboard do usuário logado"""
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('dashboard')))
    
    user = User.query.filter_by(nickname=session['usuario_logado']).first()
    cars = Car.query.filter_by(owner_id=user.id).all()
    return render_template('dashboard.html', title='Dashboard', user=user, cars=cars)


@app.route('/delete_car/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    """Deleta um carro do banco de dados"""
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('index')))
    
    # Obtém o ID do proprietário baseado no nickname do usuário logado
    owner = User.query.filter_by(nickname=session['usuario_logado']).first()
    
    if owner is None:
        flash('Usuário não encontrado.')
        return redirect(url_for('index'))

    # Busca o carro pelo ID e verifica se pertence ao proprietário
    car_to_delete = Car.query.filter_by(id=car_id, owner_id=owner.id).first()

    if car_to_delete is None:
        flash('Carro não encontrado ou você não tem permissão para deletá-lo.')
        return redirect(url_for('index'))

    # Deleta o carro
    db.session.delete(car_to_delete)
    db.session.commit()
    
    flash('Carro vendido com sucesso!')
    return redirect(url_for('index'))



@app.route('/logout')
def logout():
    """Realiza o logout do usuário"""
    session.pop('usuario_logado', None)
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
