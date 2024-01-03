from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Defining the app route
@app.route("/", methods=["get", "post"])

# Defining the main function
def reply():
    response = MessagingResponse()
    response.message("Hello")
    return str(response)

# Run the application
if __name__ == "__main__":
    app.run()
