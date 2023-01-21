from fpdf import FPDF
import openai
from flask import Flask, redirect, render_template, request, url_for, send_file

openai.api_key = "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"


def genPersonality(input):
    response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Make this into main learning type points(seperated by commas):"+ input,
            temperature=0.7,
            max_tokens = 200,
        )
    personality = str(response.choices[0].text)
    
    return personality




app = Flask(__name__)
#content,name
worksheetsGenerated = []
marks = 0

@app.route("/", methods=("GET", "POST"))
def index():
    return render_template("index.html")

@app.route("/question", methods=("GET", "POST"))
def ques():
    return render_template("ques.html")

@app.route("/personality",methods = ("GET", "POST"))
def pers():
    global user;

    if request.method == "POST":
        name = str(request.form["name"])
        sex = str(request.form["sex"])
        grade = str(request.form["grade"])
        like = str(request.form["like"])
        hobby = str(request.form["hobby"])
        unlike = str(request.form["unlike"])
        favsub = str(request.form["favsub"])
        subst = str(request.form["subst"])
        concl = str(request.form["concl"])

        strper = name+sex+grade+like+hobby+unlike+favsub+subst+concl

        user = genPersonality(strper)

    return render_template("index.html")

@app.route("/answer", methods=("GET", "POST"))
def ansques():
    if request.method == "POST":
        ques = request.form["ques"]
        response = responseGen("I have a question (if this is not a valid question return INVALID): "+ques,False)
        return redirect(url_for("ansques", result=response))

    result = request.args.get("result")
    return render_template("ques.html", result=result)



@app.route("/worksheet", methods=("GET", "POST"))
def ws():
    w = 0
    if request.method == "POST":
        ws = request.form["ws"]
        w = createWs(ws)
        

    return send_file(str(w))

@app.route("/handout", methods=("GET", "POST"))
def hout():
    if request.method == "POST":
        hout = request.form["hout"]
        createHandout(hout)
        return redirect(url_for("hout", result = "Handout Made succesfully!"))

    result = request.args.get("result")
    return render_template("ques.html", result=result)






    

def responseGen(_prompt, biased):
    response = None
    if(biased == False):
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt=_prompt,
                temperature=0.7,
                max_tokens = 3800,
                )
    else:
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt=_prompt + "(Keep in mind the user has these qualities:"+user+")",
                temperature=0.7,
                max_tokens = 3800,
            )
    return str(response.choices[0].text)

def createWs(_input):
    
    worksheet = responseGen("generate a worksheet on this(dont answer the questions, give marks per question in square brakets the total should be 25):"+_input,False)

    lines = worksheet.split("\n")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size = 10)
    
    pdf.multi_cell(200, 10, worksheet, 0, len(lines))
    name = _input[0:3]+".pdf"
    print(name)

    pdf.output(name, 'F')
    
    worksheetsGenerated.append([worksheet,name])

    return name

def createHandout(_input):
    
    subtopics = responseGen("generate 5 subtopics for "+_input+".Seperate them with commas",False)
    subtopics = subtopics.split(",")
    pdf = FPDF()
    pdf.add_page()

    
    for _subtopic in subtopics:
        pdf.set_font("Times",'B', size = 15)
        pdf.cell(200, 15, _subtopic, ln=1, align="L")
        subtopic = responseGen("Elaborate on this subtopic give rich amounts of information:"+_subtopic +" of this topic:"+_input+"Dont use any quotation marks",True)
        lines = subtopic.split("\n")
        
        pdf.set_font("Times", size = 10)

        pdf.multi_cell(200, 10, subtopic, 0, len(lines))
        
    name = _input[0:3]+".pdf"

    print(name)
    pdf.output(name, 'F')
    
def marksObtained(answerScheme, answeredWorksheet):
    response =  responseGen("Grade this worksheet using the answer scheme, return the integer value of the percentage:"+answeredWorksheet + "Answer Scheme:"+answerScheme, False)
    
    return int(response)

    
def generateAnswerScheme(ws):
    
    lines = ws[0].split("\n")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size = 10)
    
    pdf.multi_cell(200, 10, ws[0], 0, len(lines))
    name = ws[1]+"AnswerScheme.pdf"

    pdf.output(name, 'F')
    return name
def generateFeedback(worksheet,answeredWorksheet,answerScheme):
    response = responseGen("Generate constructive feedback for the answers the user gave for this worksheet:"+worksheet,"This is the answer scheme:"+answerScheme+"This is the answers the user gave"+answeredWorksheet, True)
    
    return response
def checkWorksheet(worksheet, answeredWorksheet,user):
    
    answerScheme = responseGen("Generate an answer Scheme for this worksheet (key points to be present for each answer, marks per question):"+worksheet,False)
    marks += marksObtained(answerScheme,answeredWorksheet)
    generateAnswerScheme(answerScheme)
    
    print(marks)
    print("Grade"+response)
    
    
    