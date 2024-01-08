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
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = users.find_one({"number": number})

    if bool(user) == False:
        # The user is new
        res.message("Hi in *China*. \n Choose from:" "\n 1️⃣ to contact us \n 2 to order \n 3 hours \n 4 address")
        # Add this new usesr to the db
        users.insert_one({"number": number, "status": "main", "messages": []})
    else:
        res.message("i don't know what to say")

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
