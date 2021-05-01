from flask import Flask, render_template, request, redirect, url_for, flash
from app import app, db
from .models import consumer, user
from .forms import LoginForm
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@app.route('/')
@login_required
def index():

    name = current_user.user_id


    return render_template('index.html', name = name)


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':

        user_id = request.form['user_id']
        email = request.form['email']
        password = request.form['password']

        my_data = user(user_id, email, password)
        db.session.add(my_data)
        db.session.commit()

        flash("Successfully Registered")

        return redirect(url_for('Login'))


@app.route('/login', methods=['GET', 'POST'])
def Login():
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            users = user.query.filter_by(user_id = form.userid.data).first()

            if users:
                if (users.password == form.password.data):
                    login_user(users)

                    return redirect(url_for('index'))

                flash("Invalid Credentials")

    return render_template('login.html', title ='Login', form=form)            


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('Login'))


@app.route('/consumer')
def consumer_manage():
    
    userid = current_user.user_id

    all_data = consumer.query.filter_by(userid=userid)

    return render_template("consumer.html", consumers=all_data)


@app.route('/insert', methods=['POST'])
def insert():

    if request.method == 'POST':

        
        userid = current_user.user_id

        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        weight = request.form['weight']
        height = request.form['height']

        if gender == 'Female':
            if int(age) < 3 :
                avg_cal = 1000

            if int(age) <= 8 and int(age) >= 4 :
                avg_cal = 1200
            
            if int(age) <= 13 and int(age) >= 9 :
                avg_cal = 1600
            
            if int(age) <= 18 and int(age) >= 14 :
                avg_cal = 1800

            if int(age) <= 19 and int(age) >= 30 :
                avg_cal = 2000
            
            if int(age) <= 50 and int(age) >= 31 :
                avg_cal = 1800

            if int(age) > 51 :
                avg_cal = 1600
        
        if gender == 'Male':
            if int(age) < 3 :
                avg_cal = 1000

            if int(age) <= 8 and int(age) >= 4 :
                avg_cal = 1400
            
            if int(age) <= 13 and int(age) >= 9 :
                avg_cal = 1800
            
            if int(age) <= 18 and int(age) >= 14 :
                avg_cal = 2200

            if int(age) <= 19 and int(age) >= 30 :
                avg_cal = 2400
            
            if int(age) <= 50 and int(age) >= 31 :
                avg_cal = 2200

            if int(age) > 51 :
                avg_cal = 2000
             

        my_data = consumer(name, age, gender, weight, height, avg_cal, userid)
        db.session.add(my_data)
        db.session.commit()

        flash("Insert Successfully")

        return redirect(url_for('consumer_manage'))


@app.route('/update', methods=['GET', 'POST'])
def update():

    if request.method == 'POST':
        my_data = consumer.query.get(request.form.get('id'))

        my_data.name = request.form['name']
        my_data.age = request.form['age']
        my_data.gender = request.form['gender']
        my_data.weight = request.form['weight']
        my_data.height = request.form['height']

        db.session.commit()
        flash("Consumer Details Updated Successfully")

        return redirect(url_for('consumer_manage'))


@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    my_data = consumer.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Consumer Deleted Successfully")

    return redirect(url_for('consumer_manage'))


@app.route('/cal')
def show_calorie(): 
    userid = current_user.user_id



    nd= pd.read_csv('order_det.csv',index_col = 'Unnamed: 0')

    

    nd=nd.drop(columns=['NDB_No', 'product_name','Fatty acids, total monounsaturated (g)',
       'Fatty acids, total polyunsaturated (g)',
       'Fatty acids, total saturated (g)', 'Fatty acids, total trans (g)','Fiber, total dietary (g)', 'Iron, Fe (mg)',
       'Sodium, Na (mg)', 'Sugars, total (g)','add_to_cart_order', 'reordered', 'aisle_id',
       'department_id','eval_set', 'order_dow',
       'order_hour_of_day', 'days_since_prior_order', 'department', 'aisle','Cholesterol (mg)','Water (g)','order_number',
       'product_id'],axis=1) 

    oid = nd['order_id'][nd.user_id == userid].drop_duplicates().tail(1).values[0]    
    
    nd1 = nd[nd.order_id == oid] 

    total_calcium = nd1['Calcium, Ca (mg)'].sum()
    total_energy = nd1['Energy (kcal)'].sum()
    total_protien = nd1['Protein (g)'].sum() 
    total_fat = nd1['Total lipid (fat) (g)'].sum()

    nd2 = nd1.drop(columns=['order_id','user_id'], axis =1)   

    return render_template('calorie.html', tables = [nd2.to_html(classes='table table-hover table-responsive-lg table-bordered')], titles=nd2.columns.values, 
    calcium=total_calcium, energy=total_energy, protien=total_protien, fat=total_fat)

@app.route('/recommendation')
def recommendation():
    
    userid = current_user.user_id
    #get last order items of current user

    nd= pd.read_csv('order_det.csv',index_col = 'Unnamed: 0')    

    nd=nd.drop(columns=['NDB_No', 'product_name','Fatty acids, total monounsaturated (g)',
       'Fatty acids, total polyunsaturated (g)',
       'Fatty acids, total saturated (g)', 'Fatty acids, total trans (g)','Fiber, total dietary (g)', 'Iron, Fe (mg)',
       'Sodium, Na (mg)', 'Sugars, total (g)','add_to_cart_order', 'reordered', 'aisle_id',
       'department_id','eval_set', 'order_dow',
       'order_hour_of_day', 'days_since_prior_order', 'department', 'aisle','Cholesterol (mg)','Water (g)','order_number',
       'product_id','Calcium, Ca (mg)','Energy (kcal)','Protein (g)','Total lipid (fat) (g)'],axis=1) 

    oid = nd['order_id'][nd.user_id == userid].drop_duplicates().tail(1).values[0]    
    
    nd1 = nd[nd.order_id == oid] 
    
    nd2 = nd1['Long_Desc']

    item_list = nd2.to_numpy()

    
    

    ###### helper functions. Use them when needed #######
    def get_item_from_index(index):
        return df2[df2.index == index]["item"].values[0]

    def get_index_from_item(item):
        return df2[df2.item == item]["index"].values[0]
    ##################################################

    ##Step 1: Read CSV File

    df = pd.read_csv("food_descr.csv")
    cols = ['Unnamed: 0','NDB_No','Long_Desc','Shrt_Desc','FdGrp_Desc']
    df1=df[cols]
    df2=df1.rename({'Unnamed: 0':'index','Long_Desc':'item'}, axis=1)

    ##Step 2: Select Features

    features = ['FdGrp_Desc','Shrt_Desc']

    ##Step 3: Create a column in DF which combines all selected features
    for feature in features:
        df2[feature] = df2[feature].fillna('')

    def combine_features(row):
        try:
            return row['FdGrp_Desc']+" "+row['Shrt_Desc']
        except:
            print("Error:", row)

    df2["combine_features"] = df2.apply(combine_features,axis=1)

    
    ##Step 4: Create count matrix from this new combined column
    cv = CountVectorizer()

    count_matrix = cv.fit_transform(df2["combine_features"])

    ##Step 5: Compute the Cosine Similarity based on the count_matrix

    cosine_sim = cosine_similarity(count_matrix) 
    
    items = []

    j = 0
    while j < len(item_list):

        food_item_likes = item_list[j]

    ## Step 6: Get index of this food item from its title

        item_id = get_index_from_item(food_item_likes)

        similar_items = list(enumerate(cosine_sim[item_id]))

    ## Step 7: Get a list of similar food items in descending order of similarity score

        sorted_similar_items = sorted(similar_items,key=lambda x:x[1],reverse=True)

    ## Step 8: Print titles of first 5 food items
        i=0
        for item in sorted_similar_items:
            items = get_item_from_index(item[0])
            print(items)
            
            i=i+1
            if i>5:
                break
        
        j= j+1

        


    return render_template('recommendation.html', len = len(items) ,items = items )


#custom error pages

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')