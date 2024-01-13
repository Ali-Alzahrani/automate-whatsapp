from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://Ali:1931@cluster0.f74zbur.mongodb.net/?retryWrites=true&w=majority")
db = cluster["Auto-parts-shop"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def reply():
    text = request.form.get("Body")   # The text sent by the user
    number = request.form.get("From")    # The mobile nubmer of the user who is texting
    
    
    res = MessagingResponse()
    user = users.find_one({"number": number})

    if bool(user) == False:
        # The user is new
        res.message("مرحبا بك في *الابداع الصيني لقطع الغيار* الرجاء ادخال الرقم المناسب" "\n 1️⃣ للطلب والتوصيل \n 2️⃣ لموقعنا على قوقل ماب \n 3️⃣ لساعات العمل \n 4️⃣ للتحدث الى احد الموظفين")
        # Add this new usesr to the db (his number, status, and an empty array to store his coming messages)
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message("الرجاء تحديد نوع السياره: \n 1️⃣ ام جي \n 2️⃣ تشانجان \n 3️⃣ هافال \n 4️⃣ ماكسوس \n \n 0️⃣ للعوده للقائمه الرئيسيه")
            
        elif option == 2:
            res.location(21.257466850773422, 40.452543153477315)
            
        elif option == 3:
            res.message("Here is nubmer 3")
        elif option == 4:
            res.message("Here is number 4")
        else:
            res.message("Please enter a valid response")
            #return str(res)

    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
            
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("Choose from:" "\n 1️⃣ to contact us \n 2 to order \n 3 hours \n 4 address")
        elif 1 <= option <= 4:
            car_type = ["Mg", "Changan", "Haval", "Great wall"]
            selected = car_type[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})

            res.message("Your order has been placed, please enter your address 📍")

        else:
            res.message("Please enter a valid nubmer between 1 and 4")
            
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for shopping with us")
        res.message(f"Your order for {selected} has been received")
        orders.insert_one({"number": number, "item": selected, "address": text, "date": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})

    elif user["status"] == "ordered":
        res.message("Hi AGAIN in *China*. \n Choose from:" "\n 1️⃣ to contact us \n 2️⃣ to order \n 3️⃣ hours \n 4️⃣ address")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
        
        
            
        

    # Always update the user's data by adding his new message to the array
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    
    return str(res)
    
    #print("Received a message!")  # Check if this message appears in the Heroku logs
    #response = MessagingResponse()
    #response.message("حصه احبك")
    #print(str(response))  # Check the response being generated
    #return str(response)
    


# Run the application
if __name__ == "__main__":
    app.run()
