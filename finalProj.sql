-- create DATABASE market
-- GO
-- use market
-- GO

create table [User]
(
    id int Identity(1,1) primary key,
    name varchar(50),
    CustomerAttribute int ,-- 1 for buyer 0 for seller
    dob varchar(10),
    email varchar(50),
    password NVARCHAR(MAX),
    Unique(CustomerAttribute,email)

)

GO
create table Rider
(

    id int Identity(1,1) primary key,
    name varchar(50),
    countOfOrders int ,
    check (countOfOrders<=5)

)

GO
create table [order]
(
    id int primary key,
    riderID int foreign key references Rider(id),
    orderStatus varchar(20),
    totalPrice float,
    totalgPrice float,
    dateOfOrder Date

)

GO

create table Customer
(
    id int foreign key references [User](id),
    orderNum int foreign key References [Order](id),
    Unique(OrderNum)

)

GO
create table Seller
(
    id int Unique ,
    SellingDate Date,

    joinDate Date,
    foreign key(id) references [User](id)
)

create table Category
(
    id int primary key,
    categoryName varchar(50),
    Unique(categoryName)

)



GO
create table item
(

    productName varchar(50) ,
    productDescription Text,
    price float,
    grossPrice float,
    barcodeNum varchar(20) Primary key,
    stockQuantity int,
    SellerID int foreign key references Seller(id),
    categoryID int foreign key references Category(id),

    rating float ,
    ratingCount float ,
    check (rating >= 1.0 and rating < 6.0)

)

GO
create Table orderedItems
(

    itemCode varchar(20) foreign key references item(barcodeNum),

    itemCount int,

    orderID int foreign key references [order](id),


)



insert into [User]
    (name , CustomerAttribute , dob , email , password)
values
    ('huzaifa' , 0 , '2012-10-20' , 'huzaifageius5@gmail.com' , '$2b$12$O.DvJ15hWyYw89XcedRu0OBVkJhq7UWyTtaoInTYapLr.ZnctkoCS');

insert into Rider
    (name , countOfOrders)
values
    ('Adil' , 0),
    ('Farhan' , 0),
    ('Chaudary' , 0)


INSERT INTO Category
    (id,categoryName)
VALUES
    (5, 'Appliances'),
    (1, 'Computers'),
    (3, 'Furniture'),
    (2, 'Mobile_Phones'),
    (4, 'Stationary');





-- --------------------------------
GO

create view itemDetails
as
    select item.productName as name , item.productDescription as description, item.price as price , item.barcodeNum as barcode , item.rating as rating , [User].name as sellername , category.categoryName as catName
    from item join seller on item.SellerID = seller.id join [User] on [User].id = seller.id join Category on item.categoryID = category.id
    where item.stockQuantity != 0

GO

create view itemDetails2
as
    select item.productName as name , item.price as price , item.grossprice as gprice, item.stockQuantity as quantity , item.ratingCount as countofRating, item.rating as rating , SellerID , [User].email as email , category.categoryName as catName
    from item join seller on item.SellerID = seller.id join [User] on [User].id = seller.id join Category on item.categoryID = category.id
    where item.stockQuantity != 0

GO

create view CategoryAvailable
as
    select count(*) as catAvailable
    from Category c
    where c.id  in (select DISTINCT item.categoryID
    from item)

GO

create view totalorders
as
    select count(*) as totorders
    from [Order]
    where orderStatus = 'Pending' or orderStatus = 'Delivered' or orderStatus = 'Departed'

GO

create view deliveredOrders
as

    select count(*) as delOrders
    from [Order]
    where   orderStatus = 'Delivered'


GO

create view departedOrders
as

    select count(*) as depOrders
    from [Order]
    where   orderStatus = 'Departed'

GO	
create view busyriders
as
    select count(*) as bzyriders
    from Rider
    where Rider.countOfOrders = 5

GO	

create view freeriders
as
    select count(*) as friders
    from Rider
    where Rider.countOfOrders < 5


GO	

create view customerAllDetails
as
    select u.id as id , u.name as name, u.dob as dob, tab.latestOrderMade as latestOrderMade
    from [User] u
        left join ( select c.id as cid, max(o.dateofOrder) as latestOrderMade
        from Customer c join [order] o on c.ordernum = o.id
        group by c.id  ) as tab on u.id = tab.cid where u.customerattribute = 1

GO	
create VIEW sellerAllDetails
as
    select u.id as id , u.name as name , u.email as email, u.dob as dob , s.SellingDate as latestSellDate
    from [User] u join Seller s on u.id = s.id

GO	

create view findProfit
as
    select sum(o.totalPrice-o.totalgPrice) as totPrice
    from [order] o
    where MONTH(o.dateOfOrder) = Month(GETDATE())


GO	

CREATE view orderInfo
as
    select oi.itemCode as bcode , oi.orderID as orderID  , i.productName as name, i.price , c.categoryName as catname
    from orderedItems oi join [order] o on oi.orderID = o.id join item i on oi.itemCode = i.barcodeNum
        join Category c on i.categoryID = c.id
    where o.orderStatus != 'Delivered'




GO	


create procedure PendingOrders
    @cusID int
as
begin
    select o.id as id, o.totalPrice as price
    from Customer join [order] o on o.id = customer.orderNum
    where o.orderStatus = 'Pending' and customer.id =  @cusID
end

GO	

create procedure DepartedOrderDetails
    @cusID int
as
begin
    select o.id as id, o.totalPrice as price
    from Customer join [order] o on o.id = customer.orderNum
    where o.orderStatus = 'Departed' and customer.id =  @cusID
end

GO

create procedure UnassignedOrders
    @cusID int
as
begin
    select o.id as id, o.totalPrice as price
    from Customer join [order] o on o.id = customer.orderNum
    where o.orderStatus = 'Unassigned' and customer.id =  @cusID
end


-- execute PendingOrders 3
GO	

create procedure storeRating
    @barcode varchar(20),
    @RATING float
as 
begin


    update item 
	set rating = (rating*ratingCount+@RATING)/(ratingCount+1) where barcodeNum = @barcode


    UPDATE item
	SET ratingCount = ratingCount+1 WHERE barcodeNum = @barcode

end

GO	

create procedure confirmOrder
    @itemCode varchar(20) ,
    @orderID INT
as
BEGIN
    INSERT INTO ordereditems
    VALUES
        ( @itemCode , 1 , @orderID )

    update item 
    set stockQuantity = stockQuantity  - 1
    where item.barcodeNum  = @itemCode


END

GO	

create procedure assignRider
    @orderID int ,
    @customerID int ,
    @totalprice int ,
    @totalgprice int
as
begin

    declare @riderID int
    set @riderID = 0
    declare @currentDate Date

    select @currentDate = GETDATE()

    select top 1
        @riderID = id
    from Rider r
    where countOfOrders < 5
    order by countOfOrders DESC , id ASC

    if (@riderID = 0)
    BEGIN
        insert into [order]
        values
            (@orderID , NULL , 'Unassigned' , @totalprice , @totalgprice , @currentDate)
    END
    
    else
    
    begin
        insert into [order]
        values
            (@orderID , @riderID , 'Pending' , @totalprice , @totalgprice , @currentDate)

        update Rider 
        set countOfOrders = countOfOrders +1 where id = @riderID

        DECLARE @count int
        set @count = 0

        select @count = countOfOrders
        from Rider
        where id = @riderID

        if(@count = 5)
        BEGIN
            update [Order] 
            set orderStatus = 'Departed' where riderID = @riderID
        END
    end

    insert into Customer
    values
    (@customerID , @orderID)


end

GO	

create procedure assignRider_UA_order @orderID int , @riderId int
as begin
    
    update  [order] 
    set riderID = @riderId , orderStatus = 'Pending'
    where id = @orderID
    
    
    update Rider 
    set countOfOrders = countOfOrders +1 where id = @riderID
    
    DECLARE @count int
    set @count = 0
    
    select @count = countOfOrders from Rider where id = @riderID
    
    if(@count = 5)
    BEGIN 
        update [Order] 
        set orderStatus = 'Departed' where riderID = @riderID
    END
    

end


-- -- -----------------------------------------------------------------------------

GO	
	        
create trigger alert_item_Insert
on Item
instead of insert
as begin
    Declare @prodName varchar(50)
    Declare @bcode varchar(20)
    Declare @desc varchar(100)
    Declare @price int
    Declare @gPrice float
    Declare @quantity int
    Declare @sid int
    Declare @cid int
    
    select @prodName = productName ,@desc = productDescription ,@price = price , @gprice = grossPrice , @bcode = barcodeNum , @quantity = stockQuantity ,@sid = SellerID ,@cid = categoryID from inserted

    Declare @opt int
    set @opt = 0

    select @opt = 1
    from item where barcodeNum = @bcode

    if @opt = 1
    BEGIN 
        Declare @opt1 int
        set @opt1 = 0
        
        select @opt1 = 1 from Item where barcodeNum = @bcode and SellerID = @sid
        
        if @opt1 = 1
        BEGIN 
            
            Declare @opt2 int
            set @opt2 = 0 
            
            select @opt2 = 1
            from item where barcodeNum = @bcode and productName = @prodName and categoryID = @cid
            
            if @opt2 = 1
            BEGIN 
                
                update item 
                set productDescription = @desc ,price =  @price , grossPrice = @gprice , stockQuantity = stockQuantity + @quantity , SellerID = @sid 
                where barcodeNum = @bcode
                
                update Seller set SellingDate = GETDATE() where id = @sid
            END
        END
        
            
        
    END

    ELSE 

    BEGIN 

        insert into item (productName ,productDescription, price , grossPrice , barcodeNum ,stockQuantity,SellerID,categoryID,rating,ratingCount)
        select * from inserted
        
        update Seller set SellingDate = GETDATE() where id = @sid
        
    END


end
 
GO 

SELECT * FROM [User]
GO
SELECT * FROM Customer
GO
SELECT * FROM Seller
GO
SELECT * FROM Rider
GO
SELECT * FROM item
GO
SELECT * FROM Category
GO
SELECT * FROM [order]
GO
SELECT * FROM ordereditems