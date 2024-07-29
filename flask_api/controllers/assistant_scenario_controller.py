from flask import Blueprint, request, jsonify, current_app
from app import db, logger
from models.user import AssistantScenario
from utils import token_required

assistant_bp = Blueprint('assistant_bp', __name__)

@assistant_bp.route('/scenarios', methods=['POST'])
@token_required
def create_scenario(current_user):
    data = request.get_json()
    new_scenario = AssistantScenario(
        scenario_text=data['scenario_text'],
        additional_instructions=data['additional_instructions'],
        enable=data.get('enable', True)
    )
    try:
        db.session.add(new_scenario)
        db.session.commit()
        return jsonify({'message': 'Scenario created successfully', 'id': new_scenario.id}), 201
    except Exception as e:
        db.session.rollback()  # Rollback the transaction in case of an error
        logger.error(f"Failed to create scenario: {str(e)}")
        return jsonify({'message': f'Failed to create scenario: {str(e)}'}), 500

@assistant_bp.route('/scenarios/<int:id>', methods=['PUT'])
@token_required
def update_scenario(current_user, id):
    data = request.get_json()
    scenario = AssistantScenario.query.get(id)
    if not scenario:
        return jsonify({'message': 'Scenario not found'}), 404

    try:
        scenario.scenario_text = data['scenario_text']
        scenario.additional_instructions = data['additional_instructions']
        scenario.enable = data.get('enable', scenario.enable)
        db.session.commit()
        return jsonify({'message': 'Scenario updated successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update scenario: {str(e)}")
        return jsonify({'message': f'Failed to update scenario: {str(e)}'}), 500

@assistant_bp.route('/scenarios/<int:id>', methods=['DELETE'])
@token_required
def delete_scenario(current_user, id):
    scenario = AssistantScenario.query.get(id)
    if not scenario:
        return jsonify({'message': 'Scenario not found'}), 404

    try:
        db.session.delete(scenario)
        db.session.commit()
        return jsonify({'message': 'Scenario deleted successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete scenario: {str(e)}")
        return jsonify({'message': f'Failed to delete scenario: {str(e)}'}), 500

@assistant_bp.route('/scenarios/<int:id>/enable', methods=['POST'])
@token_required
def enable_scenario(current_user, id):
    scenario = AssistantScenario.query.get(id)
    if not scenario:
        return jsonify({'message': 'Scenario not found'}), 404

    try:
        scenario.enable_scenario()
        return jsonify({'message': 'Scenario enabled successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to enable scenario: {str(e)}")
        return jsonify({'message': f'Failed to enable scenario: {str(e)}'}), 500

@assistant_bp.route('/scenarios/<int:id>/disable', methods=['POST'])
@token_required
def disable_scenario(current_user, id):
    scenario = AssistantScenario.query.get(id)
    if not scenario:
        return jsonify({'message': 'Scenario not found'}), 404

    try:
        scenario.disable_scenario()
        return jsonify({'message': 'Scenario disabled successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to disable scenario: {str(e)}")
        return jsonify({'message': f'Failed to disable scenario: {str(e)}'}), 500

@assistant_bp.route('/scenarios', methods=['GET'])
@token_required
def get_all_scenarios(current_user):
    scenarios = AssistantScenario.query.all()
    return jsonify([{
        'id': scenario.id,
        'scenario_text': scenario.scenario_text,
        'additional_instructions': scenario.additional_instructions,
        'enable': scenario.enable
    } for scenario in scenarios])
