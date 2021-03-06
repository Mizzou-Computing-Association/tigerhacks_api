# -*- coding: utf-8 -*-

import json
import logging
import sqlalchemy as s

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from tigerhacks_api.utils import flash_errors
from tigerhacks_api import app

logger = logging.getLogger(__name__)

blueprint = Blueprint("api", __name__)

@blueprint.route("/healthcheck", methods=["GET"])
@blueprint.route("/status", methods=["GET"])
@blueprint.route("/ping", methods=["GET"])
@blueprint.route("/", methods=["GET"])
def home():
    return Response(
        response=json.dumps({"status": "OK"}), status=200, mimetype="application/json"
    )

@blueprint.route("/register", methods=["POST", "OPTIONS"])
def register():

    if request.method == "OPTIONS":
        response = Response(
            response=json.dumps({"status": "OK"}), status=200, mimetype="application/json"
        )
        response.headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
            "Access-Control-Allow-Headers": "Content-Type, X-TigerHacks-API-Key"
        }
        return response

    try:
        if request.headers['X-TigerHacks-API-Key'] != current_app.api_key:
            logger.error("Unauthorized request")
            return Response(
                response=json.dumps({"status": "error", "msg": "Invalid API key given"}), status=401, mimetype="application/json"
            )
    except KeyError as e:
        logger.error("No API key given")
        return Response(
            response=json.dumps({"status": "error", "msg": "No API key given"}), status=400, mimetype="application/json"
        )

    given_email = request.json["email"]
    duplicate_email_query = s.sql.text("""
        SELECT COUNT(*) FROM registrations WHERE email LIKE :email
    """)
    email_already_exists = current_app.dbconn.execute(duplicate_email_query, email=given_email).fetchone()[0]
    if email_already_exists == 1:
        return Response(
            response=json.dumps({"status": "error", "msg": "A record with that email already exists"}), status=500, mimetype="application/json"
        )

    register_query = s.sql.text("""
        INSERT INTO
        `registrations`
            (`first_name`, `last_name`, `phone_number`, `school`, `email`, `grade_level`, `major`, `shirt_size`, `mailing_address`, `birthdate`, `gender`, `graduation_year`)
        VALUES
            (:first_name, :last_name, :phone_number, :school, :email, :grade_level, :major, :shirt_size, :mailing_address, :birthdate, :gender, :graduation_year);
    """)

    try:
        values = {
            "first_name": request.json["first_name"],
            "last_name": request.json["last_name"],
            "phone_number": request.json["phone_number"],
            "school": request.json["school"],
            "email": request.json["email"],
            "grade_level": request.json["grade_level"],
            "major": request.json["major"],
            "shirt_size": request.json["shirt_size"],
            "mailing_address":request.json["mailing_address"],
            "birthdate": request.json["birthdate"],
            "gender": request.json["gender"],
            "graduation_year": request.json["graduation_year"]
        }
    except KeyError as e:
        logger.error(e)
        return Response(
            response=json.dumps({"status": "error", "msg": f"Required key of {str(e)} not found. Please check the format of your request body."}), status=400, mimetype="application/json"
        )

    try:
        current_app.dbconn.execute(register_query, **values)
        return Response(
            response=json.dumps({"status": "successful"}), status=200, mimetype="application/json"
        )
    except Exception as e:
        logger.error(e)
        return Response(
            response=json.dumps({"status": "error", "msg": str(e)}), status=500, mimetype="application/json"
        )
