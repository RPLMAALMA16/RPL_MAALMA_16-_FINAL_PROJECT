from . import create_app, db
from .models import Student, Book, Loan
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
import pickle
import pandas
from datetime import datetime
import numpy as np

pbr_df = pickle.load(open('PopularBookRecommendation.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
book = pickle.load(open('book.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))


main = Blueprint('main', __name__)
csrf = CSRFProtect()

@main.route('/')
def index():
    return render_template('home.html')


@main.route('/rekomendasi')
def rekomendasi_buku():
    list_popular_book = pbr_df['Book-Title'].tolist()
    books = Book.query.filter(Book.title.in_(list_popular_book)).limit(10).all()
    
    return render_template('rekomendasi_buku.html', books=books)

@main.route('/peminjaman')
def menu_peminjaman():
    return render_template('menu_peminjaman.html')

@main.route('/pengembalian')
def menu_pengembalian():
    loans = db.session.query(
        Loan.id, Student.name, Student.class_name, Book.ISBN, Book.title, Book.author, Loan.loan_date, Loan.return_date, Loan.is_return
    ).join(Student).join(Book).all()
    print(loans)
    return render_template('menu_pengembalian.html', loans=loans)

@main.route('/pengembalian/<int:id>', methods=['POST'])
def pengembalian(id):
    loan = Loan.query.get(id)
    loan.is_return = True
    db.session.commit()
    return redirect(url_for('main.menu_pengembalian'))

@main.route('/registrasi', methods=['GET', 'POST'])
def registrasi():
    if request.method == 'POST':
        name = request.form.get('name')
        class_name = request.form.get('class_name')
        address = request.form.get('address')
        fingerprint = request.form.get('fingerprint')

        if not (name and class_name and address and fingerprint):
            flash('Please fill out all fields', 'error')
        else:
            new_student = Student(name=name, class_name=class_name, address=address, fingerprint=fingerprint)
            db.session.add(new_student)
            db.session.commit()
            flash('Registrasi berhasil!', 'success')
            return redirect(url_for('main.index'))

    return render_template('registrasi.html')


@main.route('/get_students/<string:fingerprint>', methods=['GET'])
def get_students(fingerprint):
    student = Student.query.filter_by(fingerprint=fingerprint).first()
    if student:
        return {
            'message': 'success',
            'id': student.id,
            'name': student.name,
            'class_name': student.class_name,
            'address': student.address,
            'fingerprint': student.fingerprint
        }
    else:
        return {
            'message': 'failed'
        }


@main.route('/get_books/<string:ISBN>', methods=['GET'])
def get_books(ISBN):
    book = Book.query.filter_by(ISBN=ISBN).first()
    if book:
        return {
            'message': 'success',
            'id': book.id,
            'title': book.title,
            'ISBN': book.ISBN,
            'author': book.author,
            'year': book.year,
            'publisher': book.publisher,
            'image_url': book.image_url
        }
    else:
        return {
            'message': 'failed'
        }

@main.route('/loan', methods=['POST'])
def loan():
    data = request.get_json()

    fingerprint_id = data.get('fingerprint_id')
    # print(fingerprint_id)
    student = Student.query.filter_by(fingerprint=fingerprint_id).first()
    # print(student)
    student_id = student.id
    book_id = data.get('book_id')
    loan_date = data.get('loan_date')
    loan_data = datetime.strptime(loan_date, '%d-%m-%Y')
    return_date = data.get('return_date')
    return_data = datetime.strptime(return_date, '%d-%m-%Y')

    new_loan = Loan(student_id=student_id, book_id=book_id, loan_date=loan_data, return_date=return_data)
    db.session.add(new_loan)
    db.session.commit()

    return {
        'message': 'success'
    }

@main.route('/get_recommendation/<string:fingerprint_id>',methods=["GET"])
def get_recommendation(fingerprint_id):
    # print(fingerprint_id)
    try:
        student = Student.query.filter_by(fingerprint=fingerprint_id).first()
        student_id = student.id
        Loans = db.session.query(Loan.id, Student.name, Student.class_name, Book.ISBN, Book.title, Book.author, Loan.loan_date, Loan.return_date, Loan.is_return).join(Student).join(Book).filter(Loan.student_id == student_id).all()

        book_name = []
        for i in Loans:
            book_name.append(i[4])

        data_recommendation = recommendation(book_name[-1])

        book_name_recommendation = []
        for i in data_recommendation:
            book_name_recommendation.append(i[0])

        # print(book_name_recommendation)
        book_recommendation = Book.query.filter(Book.title.in_(book_name_recommendation)).limit(10).all()
    except:
        list_popular_book = pbr_df['Book-Title'].tolist()
        book_recommendation = Book.query.filter(Book.title.in_(list_popular_book)).limit(10).all()


    return render_template('rekomendasi_buku_cf.html', books=book_recommendation)


def recommendation(book_name):
    # fetching Index
    index = np.where(np.array(list(pt.index))==book_name)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[0])),reverse=True,key=lambda x:x[1])[1:9]
    
    data =[]
    for i in similar_items:
        item = []
        temp_df = book[book['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
        data.append(item)
    return data