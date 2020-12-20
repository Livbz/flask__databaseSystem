from flask import Flask, render_template, request,url_for
import sqlite3 as sql
import sqlite3
from flask_sqlalchemy import SQLAlchemy # 导入扩展类
import os
import click

from flask import flash,request,  redirect

DEBUG = True
app = Flask(__name__)
####################
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager #登录
from flask_login import login_required, logout_user
from flask_login import current_user,UserMixin
from flask_login import login_user

app = Flask(__name__)
db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///'+os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'
login_manager = LoginManager(app)

@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')

login_manager = LoginManager(app)  # 实例化扩展类


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象



@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    # 全局的两个变量移动到这个函数内
    name = 'Grey Li'

    user = User(name=name)
    db.session.add(user)

    db.session.commit()
    click.echo('Done.')
@app.context_processor
def inject_user():  # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user)

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('home'))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')

######################
@app.route('/')
def home():
   return render_template('index.html')


@app.route('/registerpurchase')
def snew_student():
   return render_template('registerpurchase.html')
login_manager.login_view = 'login'
@app.route('/registerpurchase1') #进货登记
@login_required  # 登录保护
def new_purchase():
   return render_template('registerpurchase1.html')

@app.route('/registersale')#销售登记
@login_required  # 登录保护
def new_sale():
   return render_template('registersale.html')

@app.route('/registeroutsale')#退货登记
@login_required  # 登录保护
def new_outsale():
   return render_template('outsale.html')


@app.route('/querytoday')#今日进货统计
def querytoday():
   return render_template('querytoday.html')

@app.route('/querymonth')#本月进货统计
def querymonth():
   return render_template('querymonth.html')

@app.route('/queryquater')#本季度进货统计
def queryquater():
   return render_template('queryquater.html')

@app.route('/queryyear')#本年度进货统计
def queryyear():
   return render_template('queryyear.html')

###########################################
@app.route('/squerytoday')#今日销售统计
def squerytoday():
   return render_template('squerytoday.html')

@app.route('/squerymonth')#本月销售统计
def squerymonth():
   return render_template('squerymonth.html')

@app.route('/squeryquater')#本季度销售统计
def squeryquater():
   return render_template('squeryquater.html')

@app.route('/squeryyear')#本年度销售统计
def squeryyear():
   return render_template('squeryyear.html')
############################################
@app.route('/squerystaff')#员工业绩情况
def squerystaff():
   return render_template('squerystaff.html')


#########################################
@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
   if request.method == 'POST':
      try:
         # noinspection PyUnusedLocal
         spmc = request.form['spmc']
         sccs = request.form['sccs']
         cpxh = request.form['cpxh']
         dj = request.form['dj']
         sl = request.form['sl']
         zje = request.form['zje']
         ywybh = request.form['ywybh']
         nian = request.form['nian']
         yue = request.form['yue']
         ri = request.form['ri']

         with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO purchasein (spmc,sccs,cpxh,dj,sl,zje,ywybh,nian,yue,ri) VALUES (?,?,?,?,?,?,?,?,?,?)",(pmc,sccs,cpxh,dj,sl,zje,ywybh,nian,yue,ri) )

            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"

      finally:
         return render_template("result.html",msg = msg)
         con.close()

@app.route('/addrecs',methods = ['POST', 'GET']) #进货登记
def addrecs():
   if request.method == 'POST':
      try:
         # noinspection PyUnusedLocal
         spmc = request.form['spmc']
         sccs = request.form['sccs']
         cpxh = request.form['cpxh']
         dj = request.form['dj']
         sl = request.form['sl']
         zje = request.form['zje']
         ywybh = request.form['ywybh']
         nian = request.form['nian']
         yue = request.form['yue']
         ri = request.form['ri']

         with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO purchased (spmc,sccs,cpxh,dj,sl,zje,ywybh,nian,yue,ri) VALUES (?,?,?,?,?,?,?,?,?,?)",(spmc,sccs,cpxh,dj,sl,zje,ywybh,nian,yue,ri) )
#spmc TEXT,sccs TEXT,cpxh TEXT,dj INT,sl INT,zje INT,ywybh TEXT,nian INT,yue INT,ri INT
            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"

      finally:
         return render_template("result.html",msg = msg)
         con.close()

@app.route('/addrecsale',methods = ['POST', 'GET']) #销售登记
def addrecsale():
   if request.method == 'POST':
      try:
         # noinspection PyUnusedLocal
         spmc = request.form['spmc']
         sccs = request.form['sccs']
         cpxh = request.form['cpxh']
         dj = request.form['dj']
         sl = request.form['sl']
         zje = request.form['zje']
         ywybh = request.form['ywybh']
         nian = request.form['nian']
         yue = request.form['yue']
         ri = request.form['ri']

         with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO purchasesale (spmc,sccs,cpxh,dj,sl,zje,ywybh,nian,yue,ri) VALUES (?,?,?,?,?,?,?,?,?,?)",(spmc,sccs,cpxh,dj,sl,zje,ywybh,nian,yue,ri) )

            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"

      finally:
         return render_template("result.html",msg = msg)
         con.close()

@app.route('/addrecoutsale',methods = ['POST', 'GET']) #退货登记
def addrecoutsale():
   if request.method == 'POST':
      try:
         # noinspection PyUnusedLocal
         spmc = request.form['spmc']
         sccs = request.form['sccs']
         cpxh = request.form['cpxh']
         dj = request.form['dj']
         sl = request.form['sl']
         zje = request.form['zje']
         ywybh = request.form['ywybh']
         nian = request.form['nian']
         yue = request.form['yue']
         ri = request.form['ri']

         with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO outsale (spmc,sccs,cpxh,dj,sl,zje,ywybh,nian,yue,ri) VALUES (?,?,?,?,?,?,?,?,?,?)",(spmc,sccs,cpxh,dj,sl,zje,ywybh,nian,yue,ri) )

            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"

      finally:
         return render_template("result.html",msg = msg)
         con.close()

@app.route('/purchaselist') #进货表
def list():
   con = sql.connect("database.db")
   con.row_factory = sql.Row

   cur = con.cursor()
   cur.execute("select * from purchased")

   rows = cur.fetchall();
   return render_template("purchaselist.html",rows = rows)

@app.route('/querytoday',methods = ['POST', 'GET']) #今日进货统计
def querytodays():

         # noinspection PyUnusedLocal

         snian = request.form['snian']
         syue = request.form['syue']
         sri = request.form['sri']
         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()

         cur.execute("select * from purchased where nian like '"+snian+"' and yue like '"+syue+"' and ri like '"+sri+"' ")
         rows = cur.fetchall();
         return render_template("statictoday.html",rows = rows)




@app.route('/salelist') #销售表
def salelist():
   con = sql.connect("database.db")
   con.row_factory = sql.Row

   cur = con.cursor()
   cur.execute("select * from purchasesale")

   rows = cur.fetchall();
   return render_template("salelist.html",rows = rows)

@app.route('/outsalelist') #退货表
def outsalelist():
   con = sql.connect("database.db")
   con.row_factory = sql.Row

   cur = con.cursor()
   cur.execute("select * from outsale")

   rows = cur.fetchall();
   return render_template("outsalelist.html",rows = rows)

@app.route('/staff') #员工表
def staff():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("select ywybh,sum(sl),sum(zje) from purchasesale group by ywybh ")
   rows = cur.fetchall();
   return render_template("staff.html",rows = rows)

@app.route('/merchant') #厂商表
def merchant():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("select * from merchant")
   rows = cur.fetchall();
   return render_template("merchant.html",rows = rows)


@app.route('/staticmonth',methods = ['POST', 'GET']) #本月进货统计
def staticmonth():

         # noinspection PyUnusedLocal

         snian = request.form['snian']
         syue = request.form['syue']
         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()

         cur.execute("select * from purchased where nian like '"+snian+"' and yue like '"+syue+"'")
         rows = cur.fetchall();
         return render_template("staticmonth.html",rows = rows)

@app.route('/staticquater',methods = ['POST', 'GET']) #本季度进货统计
def staticquater():

         # noinspection PyUnusedLocal

         snian = request.form['snian']
         jidu = request.form['jidu']

         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()
         if jidu=='1':
             cur.execute("select * from purchased where nian like '" + snian + "' and yue >=1 and yue <=3 ")
             rows = cur.fetchall();
             return render_template("staticquater.html", rows=rows)
         elif jidu=='2':
          cur.execute("select * from purchased where nian like '" + snian + "'") #and yue >='4' and yue <=6"
          rows = cur.fetchall();
          return render_template("staticquater.html", rows=rows)
         elif jidu=='3':
          cur.execute("select * from purchased where nian like '" + snian + "' and yue >=7 and yue <=9")
          rows = cur.fetchall();
          return render_template("staticquater.html", rows=rows)
         else:
             cur.execute("select * from purchased where nian like '" + snian + "' and yue >=10")
             rows = cur.fetchall();
             return render_template("staticquater.html", rows=rows)

@app.route('/staticyear',methods = ['POST', 'GET']) #本年度进货统计
def staticyear():

         # noinspection PyUnusedLocal

         snian = request.form['snian']

         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()

         cur.execute("select * from purchased where nian like '" + snian + "'")
         rows = cur.fetchall();
         return render_template("staticyear.html",rows = rows)

#######################################################################
@app.route('/sstatictoday',methods = ['POST', 'GET']) #今日销售统计
def sstatictoday():

         # noinspection PyUnusedLocal

         snian = request.form['snian']
         syue = request.form['syue']
         sri = request.form['sri']
         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()

         cur.execute("select * from purchasesale where nian like '"+snian+"' and yue like '"+syue+"' and ri like '"+sri+"' ")
         rows = cur.fetchall();
         return render_template("sstatictoday.html",rows = rows)

@app.route('/sstaticmonth',methods = ['POST', 'GET']) #本月销售统计
def sstaticmonth():

         # noinspection PyUnusedLocal

         snian = request.form['snian']
         syue = request.form['syue']
         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()

         cur.execute("select * from purchasesale where nian like '"+snian+"' and yue like '"+syue+"'")
         rows = cur.fetchall();
         return render_template("sstaticmonth.html",rows = rows)

@app.route('/sstaticquater',methods = ['POST', 'GET']) #本季度销售统计
def sstaticquater():

         # noinspection PyUnusedLocal

         snian = request.form['snian']
         jidu = request.form['jidu']

         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()
         if jidu=='1':
             cur.execute("select * from purchasesale where nian like '" + snian + "' and yue >=1 and yue <=3 ")
             rows = cur.fetchall();
             return render_template("staticquater.html", rows=rows)
         elif jidu=='2':
          cur.execute("select * from purchasesale where nian like '" + snian + "' and yue >=4 and yue <=6")
          rows = cur.fetchall();
          return render_template("staticquater.html", rows=rows)
         elif jidu=='3':
          cur.execute("select * from purchasesale where nian like '" + snian + "' and yue >=7 and yue <=9")
          rows = cur.fetchall();
          return render_template("staticquater.html", rows=rows)
         else:
             cur.execute("select * from purchasesale where nian like '" + snian + "' and yue >=10")
             rows = cur.fetchall();
             return render_template("sstaticquater.html", rows=rows)

@app.route('/sstaticyear',methods = ['POST', 'GET']) #本年度销售统计
def sstaticyear():

         # noinspection PyUnusedLocal

         snian = request.form['snian']

         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()

         cur.execute("select * from purchasesale where nian like '" + snian + "'")
         rows = cur.fetchall();
         return render_template("sstaticyear.html",rows = rows)

##########################



@app.route('/staticstaff',methods = ['POST', 'GET']) #本年度进货统计
def staticstaff():

         # noinspection PyUnusedLocal
         ssywybh= request.form['sywybh']
         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()
#SELECT NAME, SUM(SALARY) FROM COMPANY GROUP BY NAME
         cur.execute("select ywybh,sum(sl),sum(zje) from purchasesale where ywybh like '" + ssywybh + "'group by ywybh ")
         rows = cur.fetchall();
         return render_template("staticstaff.html",rows = rows)