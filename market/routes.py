
from market import app
from flask import redirect, render_template, url_for, flash, session, request
from market import connection, pool
from market.forms import RegisterForm, LoginForm, PurchaseItem, InfoItem, AddProduct
from datetime import date
from sqlalchemy import text
selectedItems = []

# pool = sqlalchemy.create_engine(
#     "mssql+pytds://localhost",
#     creator=connection,
# )


def executeInsertquery(query: str):
    with pool.connect() as cursor:

        # query = "INSERT INTO [User](name ,CustomerAttribute, dob , email , password) VALUES ('{name}' ,{attr}, {dob}, '{email}', '{password}')".format(
        #     name="Raza haider", attr="1", dob="2002-08-01", email="raza@gmail.com", password="1234567")
        cursor.execute(text(query))
        cursor.commit()
        cursor.close()


def executeAndReturnOneRow(query: str):
    # query = "execute PendingOrders {uid}".format(uid=4)
    with pool.connect() as cursor:
        results = cursor.execute(text(query)).fetchone()
        cursor.close()
    return results


def executeAndReturnManyRows(query: str):
    # query = "execute PendingOrders {uid}".format(uid=4)
    with pool.connect() as cursor:
        results = cursor.execute(text(query)).fetchall()
        cursor.close()
    return results


num1 = executeAndReturnOneRow("select max(id) as maxId from [Order]")


orderID = num1[0]
if orderID == None:
    orderID = 1
totalOrderPrice = 0
totalOrdergPrice = 0


@app.route('/')
@app.route('/home')
def Home_page():
    print("Order Id: ", orderID)
    return render_template('home.html')


@app.route("/market", methods=['GET', 'POST'])
def market_page():

    if 'loggedin' in session:

        if session['attr'] == 1:
            # ---------- variables -----------------
            form = PurchaseItem()
            infoForm = InfoItem()

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
            results = executeAndReturnManyRows("SELECT * FROM Category")
            for row in results:
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

                    if selectedItems:

                        orderID += 1
                        query = "execute assignRider {0},{1},{2},{3}".format(
                            orderID, session['id'], totalOrderPrice, totalOrdergPrice)
                        executeInsertquery(query)
                        for row in selectedItems:
                            query = "execute confirmOrder '{0}',{1}".format(
                                row[0], orderID)
                            executeInsertquery(query=query)
                        selectedItems.clear()
                        totalOrdergPrice = 0
                        totalOrderPrice = 0

                elif searchContent:
                    query = "SELECT * FROM itemDetails where name  LIKE '%{0}%'".format(
                        searchContent)
                    results = executeAndReturnManyRows(query)
                    for row in results:
                        r = list(row)
                        r[4] = "{:.2f}".format(r[4])
                        r[4] = float(r[4])
                        items.append(r)

                elif radiobtn:

                    radiobtn = float(radiobtn)
                    print(infoItem, "---", radiobtn)
                    query = "execute storeRating '{0}',{1}".format(
                        infoItem, radiobtn)
                    executeInsertquery(query)

                elif itemToRemove:
                    print("Item To Remove: ", itemToRemove)
                    itr = 0
                    for row in selectedItems:

                        if itemToRemove == row[0]:

                            totalOrderPrice -= int(row[2])
                            totalOrdergPrice -= int(row[3])
                            print(totalOrderPrice, totalOrdergPrice)
                            selectedItems.pop(itr)

                        itr += 1

                elif purchased_item:
                    print("Selected Items: ", selectedItems)
                    isPresent = False
                    for row in selectedItems:
                        if purchased_item == row[0]:
                            isPresent = True
                            flash("Sorry You Already have selected this item",
                                  category="info")
                            break

                    if not isPresent:

                        query = "select barcodeNum, productName , price , grossPrice from item where barcodeNum = '{0}'".format(
                            purchased_item)
                        num = executeAndReturnOneRow(query)

                        selectedItems.append(num)
                        totalOrderPrice += int(num[2])
                        totalOrdergPrice += int(num[3])

                elif catname and catname != "ALL":

                    query = "SELECT * FROM itemDetails where catName = '{0}'".format(
                        str(catname))
                    results = executeAndReturnManyRows(query)
                    for row in results:
                        r = list(row)
                        r[4] = "{:.2f}".format(r[4])
                        r[4] = float(r[4])
                        items.append(r)

            if (catname == "ALL" or not catname) and not searchContent:

                results = executeAndReturnManyRows("SELECT * FROM itemDetails")

                for row in results:

                    r = list(row)
                    r[4] = "{:.2f}".format(r[4])
                    r[4] = float(r[4])
                    items.append(r)

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

            query = "INSERT INTO [User](name ,CustomerAttribute, dob , email , password) VALUES ('{0}' ,{1}, '{2}', '{3}', '{4}')".format(
                name, value, dateofbirth, email, password)

            executeInsertquery(query)
            query = "SELECT * FROM [User] WHERE email = '{0}' AND password = '{1}'".format(
                email, password)

            account = executeAndReturnOneRow(query)

            if value == 0:
                query = "INSERT INTO Seller(id , joinDate) VALUES ({0}, '{1}')".format(
                    account[0], str(date.today()))
                executeInsertquery(query)

            session['loggedin'] = True
            session['id'] = account[0]
            session['attr'] = account[2]
            session['name'] = account[1]

            flash(
                f"Account created successfully! You are now logged in as {name}", category='success')
            if session['id'] == 1:
                return redirect(url_for('dashboard_page'))
            elif session['attr'] == 1:
                return redirect(url_for('market_page'))
            return redirect(url_for('sell_page'))

        elif form.errors != {}:  # If there are not errors from the validations
            for err_msg in form.errors.values():
                flash(
                    f'There was an error with creating a user: {err_msg}', category='danger')

        return render_template("register.html", form=form)

    return redirect(url_for('Home_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if not 'loggedin' in session:
        form = LoginForm()
        if form.validate_on_submit():
            print(form.email.data, "------", form.password.data)
            query = "SELECT * FROM [User] WHERE email = '{0}' AND password = '{1}'".format(
                form.email.data, form.password.data)
            account = executeAndReturnOneRow(query)

            if account:
                session['loggedin'] = True
                session['id'] = account[0]
                session['name'] = account[1]
                session['attr'] = account[2]

                username = account[1]
                flash(
                    f'Success! You are logged in as: {username}', category='success')
                if session['id'] == 1:
                    return redirect(url_for('dashboard_page'))
                elif session['attr'] == 1:
                    return redirect(url_for('market_page'))

                return redirect(url_for('sell_page'))
            else:
                flash('Username and password are not match! Please try again',
                      category='danger')

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

            num = executeAndReturnOneRow("select * from totalorders")

            orderdetails.append(num[0])

            num = executeAndReturnOneRow("select * from deliveredOrders")

            orderdetails.append(num[0])

            num = executeAndReturnOneRow("select * from departedOrders")

            orderdetails.append(num[0])

            num = orderdetails[0] - orderdetails[1] - orderdetails[2]
            orderdetails.append(num)

            # -------------------------------------------------------------------
            num = executeAndReturnOneRow("select * from busyriders")
            riderDetails.append(num[0])

            num = executeAndReturnOneRow("select * from freeriders")

            riderDetails.append(num[0])

            # ----------------------------------------------------------------
            sellerDetail = executeAndReturnOneRow(
                "select count(*) as totSellers from Seller")

            # ----------------------------------------------------------------
            customerDetail = executeAndReturnOneRow(
                "select count(*) as totalCus from [User] where CustomerAttribute = 1")

            # ----------------------------------------------------------------

            num = executeAndReturnOneRow("select * from CategoryAvailable")
            itemDetails.append(num[0])

            # ---------------------------------------------------------------
            num = executeAndReturnOneRow(
                "select count(*) as totalCat from category")
            itemDetails.append(num[0])

            # --------------------------------------------------------------

            totalProfit = executeAndReturnOneRow(
                "select sum(o.totalPrice-o.totalgPrice) as totProfit from [order] o")

            # --------------------------------------------------------------

            num = executeAndReturnOneRow("select * from findProfit")
            currMonthProfit = num[0]

            if not currMonthProfit:
                currMonthProfit = 0

            return render_template("admin.html", orderdetails=orderdetails, riderDetails=riderDetails, sellerDetail=sellerDetail, customerDetail=customerDetail, itemDetails=itemDetails, totalProfit=totalProfit, currMonthProfit=currMonthProfit)
        else:
            return redirect(url_for('Home_page'))

    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/dashboard/customerDetail")
def customerDetail_page():
    if 'loggedin' in session:
        if session['id'] == 1:

            customerAllDetails = []
            results = executeAndReturnManyRows(
                "select * from customerAllDetails")
            for row in results:
                r = list(row)
                r[3] = str(r[3])
                customerAllDetails.append(r)

            return render_template("customerDetail.html", customerAllDetails=customerAllDetails)
        else:
            return redirect(url_for('Home_page'))

    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/dashboard/sellerDetail")
def sellerDetail_page():
    if 'loggedin' in session:
        if session['id'] == 1:

            sellerAllDetails = []
            results = executeAndReturnManyRows(
                "select * from sellerAllDetails")
            for row in results:
                sellerAllDetails.append(row)

            return render_template("sellerDetail.html", sellerAllDetails=sellerAllDetails)
        else:
            return redirect(url_for('Home_page'))
    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/dashboard/riderDetail", methods=['GET', 'POST'])
def riderDetail_page():
    if 'loggedin' in session:
        if session['id'] == 1:

            if request.method == "POST":
                id = request.form.get("BtnFreed")
                query = "update Rider set countOfOrders = 0 where id = {0}".format(
                    id)
                executeInsertquery(query)

                query = "update [Order] set orderstatus = 'Delivered' where riderID = {0}".format(
                    id)

                executeInsertquery(query)

                executeInsertquery(
                    "update [Order] set riderID = NULL where orderstatus = 'Delivered'")

                results = executeAndReturnManyRows(
                    "select id from [Order] where orderStatus = 'Unassigned'")
                orderIds = []
                for row in results:
                    orderIds.append(row[0])

                orderNums = len(orderIds)
                riderOrders = 0

                while riderOrders < 5 and orderNums > 0:
                    query = "execute assignRider_UA_order {0}, {1}".format(
                        orderIds[riderOrders], id)
                    executeInsertquery(query=query)
                    orderNums -= 1
                    riderOrders += 1

            riders = []

            results = executeAndReturnManyRows(
                "select * from Rider where countOfOrders = 5")

            for row in results:
                riders.append(row)

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

                query = "select id from Category where categoryName = '{0}'".format(
                    category)

                num = executeAndReturnOneRow(query)
                cid = num[0]

                # ========= checking for some conditions while inserting into items =================
                isBalreadyPreset = False
                results = executeAndReturnManyRows("select * from item")

                for row in results:
                    if row[4] == barcode:
                        isBalreadyPreset = True
                        break

                if isBalreadyPreset:
                    query = "Select * from item where barcodeNum = '{0}' and sellerID = {1}".format(
                        barcode, session['id'])

                    checkRow = executeAndReturnOneRow(query)
                    if not checkRow:
                        flash("The product of different seller is already present",
                              category='danger')
                    else:
                        query = "Select * from item where barcodeNum = '{0}' and productName = '{1}' and categoryID = {2}".format(
                            barcode, name, cid)

                        checkRow1 = executeAndReturnOneRow(query)
                        if not checkRow1:
                            flash(
                                "You cannot add the item as product credentials are not matching", category='danger')

                query = "INSERT INTO item(productName ,productDescription, price , grossPrice , barcodeNum ,stockQuantity,SellerID,categoryID,rating,ratingCount) VALUES ('{0}' ,'{1}', {2}, {3}, '{4}',{5},{6}, {7}, {8}, {9})".format(
                    name, desc, int(gPrice + (0.3 * gPrice)), gPrice,
                    barcode, quantity, session['id'], cid, 2, 1)
                executeInsertquery(query)

                query = "update Seller set SellingDate = GETDATE() where id = {0}".format(session[
                    'id'])
                executeInsertquery(query)

            return render_template("sell.html", addProductForm=addProductForm)
        else:
            return redirect(url_for('Home_page'))
    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))


@app.route("/dashboard/itemDetails", methods=['GET', 'POST'])
def itemDetail_page():
    if 'loggedin' in session:
        if session['id'] == 1:

            results = executeAndReturnManyRows("SELECT * FROM Category")

            categoryList = []
            for row in results:
                categoryList.append(row)

            items = []
            catname = None
            searchContent = None
            if request.method == "POST":

                # Get active when category button is pressed
                catname = request.form.get('dd')

                searchContent = request.form.get('searchContent')

                if searchContent:
                    query = "SELECT * FROM itemDetails2 where name  LIKE '%{0}%'".format(
                        searchContent)
                    results = executeAndReturnManyRows(query=query)
                    for row in results:
                        r = list(row)
                        r[4] = "{:.2f}".format(r[4])
                        r[4] = float(r[4])
                        items.append(r)

                elif catname and catname != "ALL":

                    query = "SELECT * FROM itemDetails2 where catName = {0}".format(
                        str(catname))

                    results = executeAndReturnManyRows(query)
                    for row in results:
                        r = list(row)
                        r[5] = "{:.2f}".format(r[5])
                        r[5] = float(r[5])
                        items.append(r)

            if (catname == "ALL" or not catname) and not searchContent:
                results = executeAndReturnManyRows(
                    "SELECT * FROM itemDetails2")

                for row in results:

                    r = list(row)
                    r[5] = "{:.2f}".format(r[5])
                    r[5] = float(r[5])
                    items.append(r)

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

        profile = []

        if session['id'] != 1 and session['id'] == uID:

            if session['attr'] == 0:

                query = "select u.id , name , email , dob , sellingDate ,joinDate from [User] u join Seller s on u.id  = s.id where u.id = {0}".format(
                    uID)
                profile = list(executeAndReturnOneRow(query))

                profile[1] = profile[1].upper()

                return render_template("seller_profile.html", profile=profile)
            else:
                Porders = []
                Dorders = []
                Unorders = []
                AllOrders = []

                query = "select id , name , email , dob  from [User] u where u.id = {0}".format(
                    uID)
                profile = list(executeAndReturnOneRow(query))

                profile[1] = profile[1].upper()

                # print(row)
                # ---------------------------------------

                query = "execute PendingOrders {0}".format(uID)
                results = executeAndReturnManyRows(query)
                for row in results:
                    Porders.append(row)

                # ---------------------------------------
                query = "execute DepartedOrderDetails {0}".format(uID)
                results = executeAndReturnManyRows(query)
                for row in results:
                    Dorders.append(row)

                # ---------------------------------------

                query = "execute UnassignedOrders {0}".format(uID)
                results = executeAndReturnManyRows(query)
                for row in results:
                    Unorders.append(row)

                # ---------------------------------------
                query = "select * from orderInfo"
                results = executeAndReturnManyRows(query)
                for row in results:
                    AllOrders.append(row)

                return render_template("customer_profile.html", Unorders=Unorders, Dorders=Dorders, Porders=Porders, AllOrders=AllOrders, profile=profile)

        else:
            return redirect(url_for('Home_page'))

    flash("Login First to access this page", category='info')
    return redirect(url_for('login_page'))
