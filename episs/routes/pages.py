"""Páginas servidas por Flask."""

from flask import Blueprint, render_template

pages = Blueprint("pages", __name__)


@pages.get("/")
@pages.get("/index.html")
def home():
    return render_template("index.html")


@pages.get("/interpolacion.html")
def interpolation():
    return render_template("interpolacion.html")
