from flask import Blueprint, jsonify, request

from backend.service.analysis_service import AnalysisService
from backend.service.history_service import HistoryService
from backend.service.risk_service import RiskService
from backend.service.predict_service import PredictService

sensor_bp = Blueprint("sensor", __name__)


@sensor_bp.route("/api/environment/status")
def environment_status():
    return jsonify(AnalysisService.get_environment_status())


@sensor_bp.route("/api/environment/risk")
def environment_risk():
    return jsonify(RiskService.assess_environment_risk())

@sensor_bp.route("/api/history", methods=["GET"])
def get_history():
    sensor_type = request.args.get("type", "temperature")
    limit = int(request.args.get("limit", 100))
    group_by = request.args.get("group_by", "raw")  # raw | hour | day

    data = HistoryService.get_history(sensor_type, limit, group_by)
    return jsonify(data)

@sensor_bp.route("/api/predict", methods=["GET"])
def predict():
    window = int(request.args.get("window", 20))
    horizon = int(request.args.get("horizon", 5))

    return jsonify(PredictService.predict_environment(window, horizon))