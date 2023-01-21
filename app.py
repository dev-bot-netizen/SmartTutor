import os
from fpdf import FPDF

import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = "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"

@app.route("/", methods=("GET", "POST"))
def index():
    return render_template("ques.html")

@app.route("/answer", methods=("GET", "POST"))
def ansques():
    if request.method == "POST":
        ques = request.form["ques"]
        response = responseGen("I have a question: "+ques)
        return redirect(url_for("ansques", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("ques.html", result=result)

@app.route("/worksheet", methods=("GET", "POST"))
def ws():
    if request.method == "POST":
        ws = request.form["ws"]
        response = responseGen("Write a Worksheet On This without the answers:"+ws)
        createWs(response)
        return redirect(url_for("ws"))

    result = request.args.get("result")
    return render_template("ques.html", result=result)

def responseGen(_prompt):
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt=_prompt,
            temperature=0.7,
            max_tokens = 3800,
        )
    return response.choices[0].text

def createWs(response):
    
    worksheet = str(response)
    lines = worksheet.split("\n")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size = 10)

    for i in range (0,len(lines)):
        pdf.cell(200, 10, lines[i], ln=1, align="L")
    
    nameOfWorksheet = responseGen("Generate a two word topic of this worksheet:"+worksheet)
    pdf.output(nameOfWorksheet+"Worksheet.pdf", 'F')

def createHandout(response):
    
    handout = str(response)
    lines = handout.split("\n")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size = 10)

    for i in range (0,len(lines)):
        pdf.cell(200, 10, lines[i], ln=1, align="L")
    
    nameOfHandout = responseGen("Generate a two word topic of this handout:"+handout)
    pdf.output(nameOfHandout+"Handout.pdf", 'F')
