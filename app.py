from flask import Flask, render_template, request
from flask_cors import CORS
from models import create_post, get_posts
from flask_sqlalchemy import SQLAlchemy
import xlrd
import os

app = Flask(__name__)

#loc = ("/Users/suleymanyusupov/PycharmProjects/MedicineIntersection/resources/Supplements interactions-2.xlsx")
loc = ("/Users/suleymanyusupov/Downloads/Supplements interactions-2.xlsx")
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

intersections = dict()

app.config.update(

    SECRET_KEY='topsecret',
    SQLALCHEMY_DATABASE_URI=os.environ['DATABASE_URI'],,
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)


db = SQLAlchemy(app)


class Dawai(db.Model):
    __tablename__ = 'dawai'
    medicine = db.Column(db.String(1000), primary_key=True)
    incomp = db.Column(db.String(5000), nullable=False)

    def __init__(self, medicine, incomp):
        self.medicine = medicine
        self.incomp = incomp
    
    def __repr__(self):
        return self.incomp

# Assumption is that each row has only two values in it
def classifierOtO(med, intersection):

    rowsLen = med.nrows
    colsLen = med.ncols
    for i in range(1, rowsLen):
        if med.cell_value(i, 0) in intersection:
            intersection[med.cell_value(i, 0)].add(med.cell_value(i, 1))
        else:
            intersection[med.cell_value(i, 0)] = {med.cell_value(i, 1)}

        if med.cell_value(i, 1) in intersection:
            intersection[med.cell_value(i, 1)].add(med.cell_value(i, 0))
        else:

            intersection[med.cell_value(i, 1)] = {med.cell_value(i, 0)}
    return intersection

def classifierOtM(med, intersection):

    rowsLen = med.nrows
    colsLen = med.ncols
    for i in range(1, rowsLen):
        if not bool(Dawai.query.filter_by(medicine=med.cell_value(i,0)).first()):
            pub = Dawai(med.cell_value(i,0), med.cell_value(i, 1))
            db.session.add(pub)
            db.session.commit()
        #intersection[med.cell_value(i, 0)] = set()
        #temp = med.cell_value(i, 1).replace(' ', '').split(',')
        #for v in temp:
        #    intersection[med.cell_value(i, 0)].add(v)
    return 0

def intersectOtO(med, intersection):
    # Need to write a function that will take in a list of medicine and will return if two of the names intersect

    dont = set()
    for i in range(0, len(med)):
        if med[i].upper() not in intersection:
            continue
        for j in range(i+1, len(med)):
            if med[j].upper() in intersection[med[i].upper()]:
                dont.add(med[j].upper())
                dont.add(med[i].upper())

    return dont

def intersectOtM(med, intersection):
    # Need to write a function that will take in a list of medicine and will return if two of the names intersect
    
    dont = set()
    if len(med) < 2:
        return dont
    if med[0] in intersection:
        if med[1] in intersection[med[0]]:
            dont.add(med[1])
            dont.add(med[0])
    elif med[1] in intersection:
        if med[0] in intersection[med[1]]:
            dont.add(med[1])
            dont.add(med[0])


    return dont

def searchDB(med):
    dont = set()
    res = Dawai.query.filter_by(medicine=med[0]).first()
    val1 = str(res).replace(' ', '').split(',')
    print(med[1] in val1)
    if med[1] in val1:
        dont.add(med[1])
        dont.add(med[0])
    return dont
#a = classifierOtM(sheet, intersections)


@app.route('/', methods=['GET', "POST"])
def index():
    a = classifierOtM(sheet, intersections)
    out = ''
    name = ['', '']
    if request.method =='GET':
        pass
    if request.method == 'POST':
        name1 = request.form.get('name1')
        name2 = request.form.get('name2')
        
        if name1 != '':
            name[0] = name1
        if name2 != '':
            name[1] = name2
        
        out = searchDB(name)
      
        #create_post(name, post)
    print(out)    
    posts = get_posts() 
    #print(out)
    #print(str(name).replace(" ","").split(','))
    return render_template('index.html', posts=out, len = len(name))
if __name__ == '__main__':
    
    db.create_all()
    app.run(debug=False)
