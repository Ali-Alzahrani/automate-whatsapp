from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime
import pytz

cluster = MongoClient("mongodb+srv://Ali:1931@cluster0.f74zbur.mongodb.net/?retryWrites=true&w=majority")
db = cluster["Auto-parts-shop"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)

def get_saudi_time():
    saudi_timezone = pytz.timezone("Asia/Riyadh")
    saudi_time = datetime.now(saudi_timezone)
    return saudi_time

@app.route("/", methods=["GET", "POST"])
def reply():
    text = request.form.get("Body")   # The text sent by the user
    number = request.form.get("From")    # The mobile nubmer of the user who is texting
    
    
    res = MessagingResponse()
    user = users.find_one({"number": number})

    # ------------------- New user ------------------#
    if bool(user) == False:
        # The user is new
        res.message("مرحبا بك في *الابداع الصيني لقطع الغيار* الرجاء ادخال الرقم المناسب" "\n 1️⃣ للطلب والتوصيل \n 2️⃣ لموقعنا على قوقل ماب \n 3️⃣ لساعات العمل \n 4️⃣ للتحدث الى احد الموظفين")
        # Add this new usesr to the db (his number, status, and an empty array to store his coming messages)
        users.insert_one({"number": number, "status": "main", "messages": []})

    # ------------------- (Main) status -------------#
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message("الرجاء تحديد نوع السياره: \n 1️⃣ ام جي \n 2️⃣ تشانجان \n 3️⃣ هافال \n 4️⃣ ماكسوس \n 5️⃣ جيلي \n 6️⃣ جريت وول \n \n 0️⃣ للعوده للقائمه الرئيسيه")
            
        elif option == 2:
            # The coordinates are (21.257466850773422, 40.452543153477315) we replaced the comma with %2C
            map_link = "https://www.google.com/maps?q=21.257466850773422%2C40.452543153477315"
            res.message(f"موقعنا على الخريطة: {map_link}")
            
        elif option == 3:
            #res.message("من السبت الى الخميس من الساعه ٨ صباحا الى ٨ مساءا ⏰")
            saudi_time = get_saudi_time().strftime("%A, %d %B %Y %H:%M:%S %p")
            res.message(f"الوقت الحالي في المملكة العربية السعودية: {saudi_time}")

            
        elif option == 4:
            res.message("الرجاء الانتظار وسيقوم احد موظفينا بالرد عليكم 😎")
            
        else:
            res.message("Please enter a valid response")
            #return str(res)

    # -------------- (Ordering) status ---------------#
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
            
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("مرحبا بك مره اخرى في *الابداع الصيني لقطع الغيار* الرجاء ادخال الرقم المناسب" "\n 1️⃣ للطلب والتوصيل \n 2️⃣ لموقعنا على قوقل ماب \n 3️⃣ لساعات العمل \n 4️⃣ للتحدث الى احد الموظفين")
        elif 1 <= option <= 6:
            car_type = ["ام جي", "تشانجان", "هافال","ماكسوي", "جلي", "قريت وول"]
            selected = car_type[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})

            res.message("الرجاء ارسال رقم الهيكل او الاستماره \n \n *والقطع المطلوبه*")

        else:
            res.message("Please enter a valid nubmer between 1 and 4")

    # ----------------- (Address) status ----------------#
    elif user["status"] == "address":
        selected = user["item"]
        saudi_time = get_saudi_time()

        # Check if it's a non-working time (Friday or 8 PM to 8 AM)
        if saudi_time.strftime("%A") == "Friday" or saudi_time.hour < 8 or saudi_time.hour >= 20:
            res.message(f"تم استلام طلباتكم لقطع غيار السياره من نوع *({selected})* كما نعلمكم بانا خارج اوقات الدوام حيث ان اوقات الدوام لدينا من السبت الى الخميس من الثامنه صباحا وحتى الثامنه مساءا."
            "\n وسيقوم الموظف بالرد عليكم في يوم العمل التالي ان شاء الله")
        else:        
            res.message("شكرا لطلبكم من الابداع الصيني")
            res.message(f"تم استلام طلباتكم لقطع غيار السياره من نوع *({selected})* وسيقوم الموظف بالتواصل معكم في اقرب وقت. \n الرجاء الانتظار ⏳")
        
        orders.insert_one({"number": number, "item": selected, "address": text, "date": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})

    # ----------------- (Ordered) status ----------------#
    elif user["status"] == "ordered":
        res.message("؟؟؟")
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
