from fpdf import FPDF
import openai
from flask import Flask, redirect, render_template, request, url_for



app = Flask(__name__)
openai.api_key = "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"

@app.route("/", methods=("GET", "POST"))
def index():
    return render_template("index.html")

@app.route("/question", methods=("GET", "POST"))
def ques():
    return render_template("ques.html")



@app.route("/answer", methods=("GET", "POST"))
def ansques():
    if request.method == "POST":
        ques = request.form["ques"]
        response = responseGen("I have a question (if this is not a valid question return INVALID): "+ques)
        return redirect(url_for("ansques", result=response))

    result = request.args.get("result")
    return render_template("ques.html", result=result)



@app.route("/worksheet", methods=("GET", "POST"))
def ws():
    if request.method == "POST":
        ws = request.form["ws"]
        response = responseGen("Write a Worksheet On This without the answers:"+ws)
        createWs(response)
        return redirect(url_for("ws",result = "Worksheet Made succesfully!"))

    result = request.args.get("result")
    return render_template("ques.html", result=result)

@app.route("/handout", methods=("GET", "POST"))
def hout():
    if request.method == "POST":
        hout = request.form["hout"]
        createHandout(hout)
        return redirect(url_for("hout", result = "Handout Made succesfully!"))

    result = request.args.get("result")
    return render_template("ques.html", result=result)

def responseGen(_prompt):
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=_prompt,
            temperature=0.7,
            max_tokens = 3800,
        )
    return str(response.choices[0].text)

def createWs(response):
    
    worksheet = response
    lines = worksheet.split("\n")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size = 10)

    for i in range (0,len(lines)):
        pdf.cell(200, 10, lines[i], ln=1, align="L")
    
    nameOfWorksheet = responseGen("Generate a two word topic of this worksheet:"+worksheet)
    
    pdf.output(str(nameOfWorksheet+"pdf"), 'F')
    return nameOfWorksheet+"pdf"

def createHandout(response):
    
    subtopics = responseGen("generate 2 subtopics for "+response+".Seperate them with commas")
    subtopics = subtopics.split(",")
    print(subtopics)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size = 10)

    
    for _subtopic in subtopics:
        pdf.cell(200, 15, _subtopic, ln=1, align="L")
        subtopic = responseGen("Elaborate on this subtopic:"+_subtopic)
        lines = subtopic.split("\n")
        print("here")
        
        for i in range (0,len(lines)):
            pdf.cell(200, 10, lines[i], ln=1, align="L")
            print("here2")
    
    nameOfHandout = responseGen("Generate a two word topic of this handout:"+response)
    pdf.output(nameOfHandout+"pdf", 'F')
    return nameOfHandout+"pdf"
