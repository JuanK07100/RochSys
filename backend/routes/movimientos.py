from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from backend.utils import movimientos_data

movimientos_bp = Blueprint('movimientos', __name__, url_prefix='/api/movimientos')

@movimientos_bp.route('', methods=['GET'])
@jwt_required()
def get_movimientos():
    return jsonify(movimientos_data(50))