from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def reply():
    
    
    #print("Received a message!")  # Check if this message appears in the Heroku logs
    response = MessagingResponse()
    response.message("Hello4")
    #print(str(response))  # Check the response being generated
    return str(response)
    


# Run the application
if __name__ == "__main__":
    app.run()
