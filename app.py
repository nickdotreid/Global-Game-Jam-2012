from flask import Flask, redirect, request, flash, render_template, session, jsonify, Blueprint
import twilio

app = Flask(__name__)

@app.route("/")
def home_page():
	return render_template("pages/home_page.html")