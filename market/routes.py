
from market import app
from flask import redirect, render_template, url_for, flash, session, request
from market import connection
from market.forms import RegisterForm, LoginForm, PurchaseItem, InfoItem, AddProduct
from datetime import date
selectedItems = []


conn = connection()
cursor = conn.cursor(as_dict=True)
cursor.execute("select max(id) as maxId from [Order]")
num1 = cursor.fetchone()


orderID = num1['maxId']
totalOrderPrice = 0
totalOrdergPrice = 0


@app.route('/')
@app.route('/home')
def Home_page():
    print("Yes")
    return render_template('home.html')


@app.route("/market", methods=['GET', 'POST'])
def market_page():

    if 'loggedin' in session:

        if session['attr'] == 1:
            # ---------- variables -----------------
            form = PurchaseItem()
            infoForm = InfoItem()
            #placeOrderbtn = PlaceOrder()
            conn = connection()
            cursor = conn.cursor(as_dict=True)
            categoryList = []
            items = []
            catname = None
            searchContent = None
            global selectedItems
            global orderID
            global totalOrderPrice
            global totalOrdergPrice
            itemToRemove = None
            purchased_item = None

            # --------- category storing -------------
            cursor.execute('SELECT * FROM Category')
            for row in cursor:
                categoryList.append(row)

            if request.method == "POST":

                # infoItem gives the barcode of the item at which 'More info' is pressed
                # All this code is handled in
                # its code is handled in 'item_modal.html'
                infoItem = request.form.get('infoItem')

                # radio button to get the values of
                # radio button in modals appeared when clicked the button More info in market.html
                # Its code is handled in 'item_modal.html'
                radiobtn = request.form.get('ans')

                # Gives the barcode of item for which selll button is pressed
                # its code is handled in market .html
                purchased_item = request.form.get('purchased_item')

                # Get active when category button is pressed
                catname = request.form.get('dd')

                searchContent = request.form.get('searchContent')

                itemToRemove = request.form.get('toRemove_item')

                confirmOrderValue = request.form.get('confirmOrder')

                if confirmOrderValue:
                    # print("Yes")
                    if selectedItems:
                        # print("Yes")
                        orderID += 1

                        cursor.callproc(
                            'assignRider', (orderID, session['id'], totalOrderPrice, totalOrdergPrice))
                        conn.commit()
                        for row in selectedItems:
                            # print(row)
                            cursor.callproc(
                                'confirmOrder', (row['barcodeNum'], orderID))
                            conn.commit()
                        selectedItems.clear()
                        totalOrdergPrice = 0
                        totalOrderPrice = 0

                elif searchContent:
                    cursor.execute('SELECT * FROM itemDetails where name  LIKE %s', ("%" + searchContent + "%"))
                    for row in cursor:
                        row['rating'] = "{:.2f}".format(row['rating'])
                        row['rating'] = float(row['rating'])
                        items.append(row)

                elif radiobtn:
                    radiobtn = float(radiobtn)
                    cursor.callproc('storeRating', (infoItem, radiobtn))

                    conn.commit()
                elif itemToRemove:
                    # print(itemToRemove)
                    itr = 0
                    for row in selectedItems:

                        if 'barcodeNum' in row and itemToRemove == row['barcodeNum']:

                            totalOrderPrice -= int(row['price'])
                            totalOrdergPrice -= int(row['grossPrice'])
                            print(totalOrderPrice, totalOrdergPrice)
                            selectedItems.pop(itr)

                        itr += 1
                elif purchased_item:
                    # print(purchased_item)
                    isPresent = False
                    for row in selectedItems:
                        if 'barcodeNum' in row and purchased_item == row['barcodeNum']:
                            isPresent = True
                            flash("Sorry You Already have selected this item",category="info")
                            break

                    if not isPresent:
                        cursor.execute("select barcodeNum, productName , price , grossPrice from item where barcodeNum = %s ", purchased_item)
                        num = cursor.fetchone()
                        selectedItems.append(num)
                        totalOrderPrice += int(num['price'])
                        totalOrdergPrice += int(num['grossPrice'])

                elif catname and catname != "ALL":

                    cursor.execute('SELECT * FROM itemDetails where catName = %s ', str(catname))
                    for row in cursor:
                        row['rating'] = "{:.2f}".format(row['rating'])
                        row['rating'] = float(row['rating'])
                        items.append(row)

            if (catname == "ALL" or not catname) and not searchContent:
                #print(catname , "----")
                cursor.execute('SELECT * FROM itemDetails')

                for row in cursor:

                    row['rating'] = "{:.2f}".format(row['rating'])
                    row['rating'] = float(row['rating'])
                    items.append(row)

            cursor.close()
            conn.close()
            return render_template('market.html', items=items, categoryList=categoryList, form=form, infoForm=infoForm, selectedItems=selectedItems, totalOrderPrice=totalOrderPrice)
        else:
            return redirect(url_for('Home_page'))
    else:
        flash("Login First to access this page", category='info')
        return redirect(url_for('login_page'))


@app.route("/register", methods=['GET', 'POST'])
def register_page():
    if not 'loggedin' in session:
        form = RegisterForm()
        if form.validate_on_submit():

            name = form.username.data
            email = form.email_address.data
            password = form.password2.data
            dateofbirth = form.dob.data

            opt = form.options.data

            value = 1
            if opt == "Seller":
                value = 0
            conn = connection()
            cursor = conn.cursor(as_dict=True)

            cursor.executemany(
                "INSERT INTO [User](name ,CustomerAttribute, dob , email , password) VALUES ( %s, %d , %s ,%s , %s)",
                [(name, value, dateofbirth, email, password)]
            )
            conn.commit()

            cursor.execute('SELECT * FROM [User] WHERE email = %s AND password = %s', (email, password))
            account = cursor.fetchone()

            if value == 0:
                cursor.executemany(
                    "INSERT INTO Seller(id , joinDate) VALUES ( %d, %s)",
                    [(account['id'], str(date.today()))]
                )
                conn.commit()
            cursor.close()
            conn.close()

            session['loggedin'] = True
            session['id'] = account['id']
            session['attr'] = account['CustomerAttribute']
            session['name'] = account['name']

            flash(f"Account created successfully! You are now logged in as {name}", category='success')
            if session['id'] == 1:
                return redirect(url_for('dashboard_page'))
            elif session['attr'] == 1:
                return redirect(url_for('market_page'))
            return redirect(url_for('sell_page'))

        elif form.errors != {}:  # If there are not errors from the validations
            for err_msg in form.errors.values():
                flash(f'There was an error with creating a user: {err_msg}', category='danger')

        return render_template("register.html", form=form)

    return redirect(url_for('Home_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if not 'loggedin' in session:
        form = LoginForm()
        if form.validate_on_submit():
            conn = connection()
            cursor = conn.cursor(as_dict=True)

            cursor.execute(f"SELECT * FROM [User] WHERE email = '{form.email.data}' AND password = '{form.password.data}'")
            account = cursor.fetchone()
            cursor.close()
            conn.close()

            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['name'] = account['name']
                session['attr'] = account['CustomerAttribute']

                username = account['name']
                flash(f'Success! You are logged in as: {username}', category='success')
                
                if session['id'] == 1:
                    return redirect(url_for('dashboard_page'))
                elif session['attr'] == 1:
                    return redirect(url_for('market_page'))

                return redirect(url_for('sell_page'))
            else:
                flash('Username and password are not match! Please try again',category='danger')

        return render_template('login.html', form=form)
    else:
        return redirect(url_for('Home_page'))


@app.route("/logout")
def logout_page():
    if 'loggedin' in session:
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('name', None)
        flash("You have been logged out!", category='info')
        return render_template("home.html")

    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard_page():
    if 'loggedin' in session:

        if session['id'] == 1:
            orderdetails = []
            riderDetails = []

            sellerDetail = 0

            customerDetail = 0
            itemDetails = []
            totalProfit = 0
            currMonthProfit = 0

            conn = connection()
            cursor = conn.cursor(as_dict=True)

            cursor.execute("select * from totalorders")
            num = cursor.fetchone()

            orderdetails.append(num["totorders"])

            cursor.execute("select * from deliveredOrders")
            num = cursor.fetchone()

            orderdetails.append(num["delOrders"])

            cursor.execute("select * from departedOrders")
            num = cursor.fetchone()

            orderdetails.append(num["depOrders"])

            num = orderdetails[0] - orderdetails[1] - orderdetails[2]
            orderdetails.append(num)

            # -------------------------------------------------------------------
            cursor.execute("select * from busyriders")
            num = cursor.fetchone()

            riderDetails.append(num["bzyriders"])

            cursor.execute("select * from freeriders")
            num = cursor.fetchone()

            riderDetails.append(num["friders"])

            # ----------------------------------------------------------------
            cursor.execute("select count(*) as totSellers from Seller")
            sellerDetail = cursor.fetchone()

            # ----------------------------------------------------------------
            cursor.execute("select count(*) as totalCus from [User] where CustomerAttribute = 1")
            customerDetail = cursor.fetchone()

            # ----------------------------------------------------------------
            cursor.execute("select * from CategoryAvailable")
            num = cursor.fetchone()
            itemDetails.append(num['catAvailable'])

            # ---------------------------------------------------------------
            cursor.execute("select count(*) as totalCat from category")
            num = cursor.fetchone()
            itemDetails.append(num['totalCat'])

            # --------------------------------------------------------------
            cursor.execute("select sum(o.totalPrice-o.totalgPrice) as totProfit from [order] o")
            totalProfit = cursor.fetchone()

            # --------------------------------------------------------------
            cursor.execute("select * from findProfit")
            num = cursor.fetchone()
            currMonthProfit = num['totPrice']

            # if not currMonthProfit:
            #     currMonthProfit = 0

            cursor.close()
            conn.close()

            return render_template("admin.html", orderdetails=orderdetails, riderDetails=riderDetails, sellerDetail=sellerDetail, customerDetail=customerDetail, itemDetails=itemDetails, totalProfit=totalProfit, currMonthProfit=currMonthProfit)
        else:
            return redirect(url_for('Home_page'))

    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/dashboard/customerDetail")
def customerDetail_page():
    if 'loggedin' in session:
        if session['id'] == 1:
            conn = connection()
            cursor = conn.cursor(as_dict=True)

            customerAllDetails = []
            cursor.execute("select * from customerAllDetails")
            for row in cursor:
                row['latestOrderMade'] = str(row['latestOrderMade'])
                customerAllDetails.append(row)

            cursor.close()
            conn.close()

            return render_template("customerDetail.html", customerAllDetails=customerAllDetails)
        else:
            return redirect(url_for('Home_page'))

    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/dashboard/sellerDetail")
def sellerDetail_page():
    if 'loggedin' in session:
        if session['id'] == 1:
            conn = connection()
            cursor = conn.cursor(as_dict=True)

            sellerAllDetails = []
            cursor.execute("select * from sellerAllDetails")
            for row in cursor:
                sellerAllDetails.append(row)

            cursor.close()
            conn.close()

            return render_template("sellerDetail.html", sellerAllDetails=sellerAllDetails)
        else:
            return redirect(url_for('Home_page'))
    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/dashboard/riderDetail", methods=['GET', 'POST'])
def riderDetail_page():
    if 'loggedin' in session:
        if session['id'] == 1:
            conn = connection()
            cursor = conn.cursor(as_dict=True)
            if request.method == "POST":
                id = request.form.get("BtnFreed")
                cursor.execute("update Rider set countOfOrders = 0 where id = %s ", id)
                cursor.execute("update [Order] set orderstatus = 'Delivered' where riderID = %d", id)
                cursor.execute("update [Order] set riderID = NULL where orderstatus = 'Delivered'")
                conn.commit()

                cursor.execute("select id from [Order] where orderStatus = 'Unassigned'")
                orderIds = []
                for row in cursor:
                    orderIds.append(row['id'])

                orderNums = len(orderIds)
                print(orderNums)
                riderOrders = 0

                while riderOrders < 5 and orderNums > 0:
                    cursor.callproc('assignRider_UA_order',(orderIds[riderOrders], id))
                    conn.commit()
                    orderNums -= 1
                    riderOrders += 1

            riders = []

            cursor.execute("select * from Rider where countOfOrders = 5")

            for row in cursor:
                riders.append(row)

            cursor.close()
            conn.close()

            return render_template("riderDetail.html", riders=riders)
        else:
            return redirect(url_for('Home_page'))
    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/sellForm", methods=['GET', 'POST'])
def sell_page():
    if 'loggedin' in session:
        if session['attr'] == 0:
            addProductForm = AddProduct()
            if addProductForm.validate_on_submit():

                name = addProductForm.name.data
                desc = addProductForm.description.data
                barcode = addProductForm.barcode.data
                gPrice = addProductForm.grossprice.data
                quantity = addProductForm.stockquantity.data
                category = addProductForm.category.data

                conn = connection()
                cursor = conn.cursor(as_dict=True)
                cursor.execute("select id from Category where categoryName = %s", category)
                num = cursor.fetchone()
                cid = num['id']

                # ================== checnking for some conditions while inserting into items =================
                isBalreadyPreset = False
                cursor.execute("Select * from item")
                for row in cursor:
                    if row['barcodeNum'] == barcode:
                        isBalreadyPreset = True
                        break

                if isBalreadyPreset:
                    cursor.execute("Select * from item where barcodeNum = %s and sellerID = %d", (barcode, session['id']))
                    checkRow = cursor.fetchone()
                    if not checkRow:
                        flash("The product of different seller is already present",category='danger')
                    else:
                        cursor.execute("Select * from item where barcodeNum = %s and productName = %s and categoryID = %d", (barcode, name, cid))
                        checkRow1 = cursor.fetchone()
                        if not checkRow1:
                            flash("You cannot add the item as product credentials are not matching", category='danger')

                cursor.executemany(
                    "INSERT INTO item(productName ,productDescription, price , grossPrice , barcodeNum ,stockQuantity,SellerID,categoryID,rating,ratingCount) VALUES ( %s, %s , %d ,%d , %s , %d,%d ,%d,%d,%d)",
                    [(name, desc, int(gPrice + (0.3 * gPrice)), gPrice,
                      barcode, quantity, session['id'], cid, 1, 0)]
                )
                #cursor.execute("update Seller set SellingDate = GETDATE() where id = %d" , session['id'])
                conn.commit()

            return render_template("sell.html", addProductForm=addProductForm)
        else:
            return redirect(url_for('Home_page'))
    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/dashboard/itemDetails", methods=['GET', 'POST'])
def itemDetail_page():
    if 'loggedin' in session:
        if session['id'] == 1:
            conn = connection()
            cursor = conn.cursor(as_dict=True)

            cursor.execute('SELECT * FROM Category')

            categoryList = []
            for row in cursor:
                categoryList.append(row)

            items = []
            catname = None
            searchContent = None
            if request.method == "POST":

                # Get active when category button is pressed
                catname = request.form.get('dd')

                searchContent = request.form.get('searchContent')

                if searchContent:
                    cursor.execute('SELECT * FROM itemDetails2 where name  LIKE %s', ("%" + searchContent + "%"))
                    for row in cursor:
                        row['rating'] = "{:.2f}".format(row['rating'])
                        row['rating'] = float(row['rating'])
                        items.append(row)

                elif catname and catname != "ALL":

                    cursor.execute('SELECT * FROM itemDetails2 where catName = %s', str(catname))
                    for row in cursor:
                        row['rating'] = "{:.2f}".format(row['rating'])
                        row['rating'] = float(row['rating'])
                        items.append(row)

            if (catname == "ALL" or not catname) and not searchContent:
                cursor.execute('SELECT * FROM itemDetails2')

                for row in cursor:

                    row['rating'] = "{:.2f}".format(row['rating'])
                    row['rating'] = float(row['rating'])
                    items.append(row)

            return render_template("itemDetail.html", items=items, categoryList=categoryList)
        else:
            return redirect(url_for('Home_page'))
    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/profile/<userID>")
def profile_page(userID=""):
    if 'loggedin' in session:
        userID = userID[1:-1]
        uID = int(userID)
        conn = connection()

        cursor = conn.cursor(as_dict=True)
        profile = []

        if session['id'] != 1 and session['id'] == uID:

            if session['attr'] == 0:

                cursor.execute("select u.id , name , email , dob , sellingDate ,joinDate from [User] u join Seller s on u.id  = s.id where u.id = %d", uID)
                profile = cursor.fetchone()

                profile['name'] = profile['name'].upper()

                conn.close()
                cursor.close()

                return render_template("seller_profile.html", profile=profile)
            else:
                Porders = []
                Dorders = []
                Unorders = []
                AllOrders = []

                conn = connection()
                cursor.execute("select id , name , email , dob  from [User] u where u.id = %d", uID)
                profile = cursor.fetchone()
                profile['name'] = profile['name'].upper()

                # print(row)
                # ---------------------------------------
                cursor = conn.cursor(as_dict=True)
                cursor.callproc('PendingOrders', (uID,))
                for row in cursor:
                    Porders.append(row)

                # ---------------------------------------
                #cursor.callproc('orderInfo', (num,))
                cursor.callproc('DepartedOrderDetails', (uID,))
                for row in cursor:
                    Dorders.append(row)

                # ---------------------------------------

                cursor.callproc('UnassignedOrders', (uID,))
                for row in cursor:
                    Unorders.append(row)

                # ---------------------------------------
                cursor.execute("select * from orderInfo")
                for row in cursor:
                    AllOrders.append(row)

                return render_template("customer_profile.html", Unorders=Unorders, Dorders=Dorders, Porders=Porders, AllOrders=AllOrders, profile=profile)

        else:
            return redirect(url_for('Home_page'))

    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))
