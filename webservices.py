from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/create")
def create():
	bashCommand = "create.bat"
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='c:/github/azure-the_creator/')
	output = process.communicate()[0]
	return output

@app.route("/delete")
def delete():
	bashCommand = "delete.bat"
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, cwd='c:/github/azure-the_creator/')
	output = process.communicate()[0]
	return output

if __name__ == "__main__":
    app.run()