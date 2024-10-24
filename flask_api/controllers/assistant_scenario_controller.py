from flask import Blueprint, request, jsonify, current_app
from app import db, logger
from models.user import AssistantScenario,RubricQuestion, Tags
from utils import token_required
import os 
import openai
import requests

openai.api_key = os.getenv("OPENAI_KEY")
openai.model = os.getenv("OPENAI_Model")
assistant_bp = Blueprint('assistant_bp', __name__)
def create_openai_assistant(name, instructions, model):
    try:
        headers = {
            'Authorization': f'Bearer {openai.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }

        assistant_payload = {
            "name": name,
            "instructions": instructions,
            "model": model
            
        }

        response = requests.post(
            'https://api.openai.com/v1/assistants',
            headers=headers,
            json=assistant_payload
        )

        if response.status_code != 200:
            logger.error(f"Failed to create assistant with OpenAI: {response.json()} + {response.status_code}")
            return None, response.json(), response.status_code

        return response.json()['id'], None, 200
    except Exception as e:
        logger.error(f"Failed to create assistant with OpenAI: {e}")
        return None, str(e), 500
    

def delete_openai_assistant(openid):
    try:
        headers = {
            'Authorization': f'Bearer {openai.api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }
        response = requests.delete(f'https://api.openai.com/v1/assistants/{openid}', headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to delete assistant with OpenAI: {response.json()} + {response.status_code}")
            return False
        return True
    except Exception as e:
        logger.error(f"Exception while deleting assistant with OpenAI: {e}")
        return False

def handle_tags_and_rubrics(data, scenario_id):
    try:
        # Delete existing tags and rubric questions
        # First, delete existing tags and rubric questions
        existing_tags = Tags.query.filter_by(scenario_id=scenario_id).all()
        existing_rubrics = RubricQuestion.query.filter_by(scenario_id=scenario_id).all()
        
        for tag in existing_tags:
            db.session.delete(tag)
        for rubric in existing_rubrics:
            db.session.delete(rubric)
        
        # Commit deletions
        db.session.commit()

        # Add new tags
        tags = data['tags']
        for tag_text in tags:
            new_tag = Tags(tag=tag_text, scenario_id=scenario_id)
            db.session.add(new_tag)

        # Add new rubric questions
        rubrics = data['rubrics']
        for question_text in rubrics:
            new_rubric = RubricQuestion(question=question_text, scenario_id=scenario_id)
            db.session.add(new_rubric)

        db.session.commit()  # Commit all changes
        return True, None
    except Exception as e:
        db.session.rollback()  # Rollback the transaction in case of an error
        logger.error(f"Failed to add tags or rubric questions: {e}")
        return False, str(e)

def create_scenario_in_db(data, openid):
    try:
        new_scenario = AssistantScenario(
            scenario_text=data['scenario_text'],
            additional_instructions=data['additional_instructions'],
            enable=data.get('enable', True),
            role=data.get('role'),
            openid=openid
        )
        db.session.add(new_scenario)
        db.session.commit()  # Commit to get the new scenario ID
        return new_scenario, None
    except Exception as e:
        db.session.rollback()  # Rollback the transaction in case of an error
        logger.error(f"Failed to create scenario: {e}")
        return None, str(e)


@assistant_bp.route('/scenarios', methods=['GET'])
@token_required
def get_all_scenarios(curret_user):
    try:
        scenarios = AssistantScenario.query.all()
        result = [scenario.serialize() for scenario in scenarios]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Failed to retrieve scenarios', 'error': str(e)}), 500



@assistant_bp.route('/scenarios', methods=['POST'])
@token_required
def create_scenario(current_user):
    data = request.get_json()
    openid = None
    new_scenario = None

    # Step 1: Create OpenAI Assistant
    
    #scenario_text = f"You have to act as a {data['scenario_text']}. You must always act as a patient persona throughout the entire conversation and be a chatty with doctor add your input in moving the conversation forward like by asking questions. The target is for the medical student to act as a doctor, and you as a patient with the mentioned instructions/profile, so the skills of a doctor can be evaluated. Do not act as anything else, and keep your answers precise. Donot throw all of the information provided further in details at once as we expect doctor to ask specific questions"
    scenario_text = f"You have to act as a {data['scenario_text']}. You must always act as a patient persona throughout the entire conversation and be a chatty with doctor add your input in moving the conversation forward like by asking questions. The target is for the medical student to act as a doctor, and you as a patient with the mentioned instructions/profile, so the skills of a doctor can be evaluated. Do not act as anything else, and keep your answers precise and occasionally add questions. Donot throw all of the information provided further in details at once as we expect doctor to ask specific questions"
    openid, error, status_code = create_openai_assistant( data['scenario_text'], scenario_text+ ' '+ data['additional_instructions'], openai.model)
    if error:
        return jsonify({'message': 'Failed to create assistant with OpenAI', 'details': error}), status_code

    # Step 2: Create Scenario in Database
    new_scenario, error = create_scenario_in_db(data, openid)
    if error:
        delete_openai_assistant(openid)  # Cleanup if scenario creation fails
        return jsonify({'message': f'Failed to create scenario: {error}'}), 500

    # Step 3: Handle Tags and Rubrics
    success, error = handle_tags_and_rubrics(data, new_scenario.id)
    if not success:
        delete_openai_assistant(openid)  # Cleanup OpenAI assistant
        db.session.delete(new_scenario)  # Cleanup scenario in database
        db.session.commit()
        return jsonify({'message': f'Failed to add tags or rubric questions: {error}'}), 500

    return jsonify({'message': 'Scenario and related data created successfully', 'id': new_scenario.id}), 201

@assistant_bp.route('/scenarios/<int:scenario_id>', methods=['PUT'])
@token_required
def update_scenario(current_user, scenario_id):
    data = request.get_json()
    scenario = AssistantScenario.query.get(scenario_id)
    if not scenario:
        return jsonify({'message': 'Scenario not found'}), 404

    # Step 1: Delete the existing OpenAI Assistant
    if scenario.openid:
        if not delete_openai_assistant(scenario.openid):
            return jsonify({'message': 'Failed to delete existing OpenAI assistant'}), 500

    # Step 2: Create a new OpenAI Assistant
    scenario_text = f"You have to act as a {data['scenario_text']}. You must always act as a patient persona throughout the entire conversation. The target is for the medical student to act as a doctor, and you as a patient with the mentioned instructions/profile, so the skills of a doctor can be evaluated. Do not act as anything else, and keep your answers precise. Donot throw all of the information provided further in details at once as we expect doctor to ask specific questions"
    scenario_text = f"You have to act as a {data['scenario_text']}. You must always act as a patient persona throughout the entire conversation and be a chatty with doctor add your input in moving the conversation forward like by asking questions. The target is for the medical student to act as a doctor, and you as a patient with the mentioned instructions/profile, so the skills of a doctor can be evaluated. Do not act as anything else, and keep your answers precise and occasionally add questions. Donot throw all of the information provided further in details at once as we expect doctor to ask specific questions"
    openid, error, status_code = create_openai_assistant( data['scenario_text'], scenario_text+ ' '+ data['additional_instructions'], openai.model)
    if error:
        return jsonify({'message': 'Failed to create new assistant with OpenAI', 'details': error}), status_code

    # Step 3: Update Scenario in Database
    scenario.scenario_text = data['scenario_text']
    scenario.additional_instructions = data['additional_instructions']
    scenario.enable = data.get('enable', True)
    scenario.role = data.get('role')
    scenario.openid = openid
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update scenario: {e}")
        return jsonify({'message': f'Failed to update scenario: {str(e)}'}), 500

    # Step 4: Handle Tags and Rubrics
    success, error = handle_tags_and_rubrics(data, scenario_id)
    if not success:
        logger.error(f"Failed to add new tags or rubric questions: {error}")
        return jsonify({'message': f'Failed to add new tags or rubric questions: {error}'}), 500

    return jsonify({'message': 'Scenario updated successfully'}), 200

@assistant_bp.route('/scenarios/<int:id>', methods=['DELETE'])
@token_required
def delete_scenario(current_user, id):
    scenario = AssistantScenario.query.get(id)
    if not scenario:
        return jsonify({'message': 'Scenario not found'}), 404

    try:
        # Step 1: Delete all associated tags and rubric questions
        Tags.query.filter_by(scenario_id=id).delete()
        RubricQuestion.query.filter_by(scenario_id=id).delete()
        db.session.commit()  # Commit the deletions

        # Step 2: Delete the assistant on OpenAI
        if scenario.openid:
            if not delete_openai_assistant(scenario.openid):
                return jsonify({'message': 'Failed to delete assistant from OpenAI'}), 500

        # Step 3: Delete the scenario in the local database
        db.session.delete(scenario)
        db.session.commit()
        return jsonify({'message': 'Scenario deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete scenario: {str(e)}")
        return jsonify({'message': f'Failed to delete scenario: {str(e)}'}), 500

@assistant_bp.route('/scenarios/<int:id>/enable', methods=['PUT'])
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

@assistant_bp.route('/scenarios/<int:id>/disable', methods=['PUT'])
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

# Function to delete all assistants from OpenAI
def delete_all_openai_assistants():
    headers = {
        'Authorization': f'Bearer {openai.api_key}',
        'Content-Type': 'application/json',
        'OpenAI-Beta': 'assistants=v2'
    }

    # Fetch all assistants
    response = requests.get(
        "https://api.openai.com/v1/assistants?order=desc&limit=100", headers=headers
    )

    if response.status_code == 200:
        assistants = response.json().get('data', [])
        for assistant in assistants:
            assistant_id = assistant['id']
            print(f"Deleting assistant: {assistant_id}")
            delete_response = requests.delete(
                f"https://api.openai.com/v1/assistants/{assistant_id}", headers=headers
            )
            if delete_response.status_code == 204:
                print(f"Successfully deleted assistant: {assistant_id}")
            else:
                logger.error(f"Failed to delete assistant: {assistant_id}")
    else:
        logger.error("Failed to retrieve assistants from OpenAI.")

@assistant_bp.route('/delete_all', methods=['DELETE'])
def delete_all_data():
    try:
        # Delete all tags
        Tags.query.delete()
        
        # Delete all rubric questions
        RubricQuestion.query.delete()
        
        # Delete all scenarios
        AssistantScenario.query.delete()
        
        # Commit the deletions to the database
        db.session.commit()
        
        # Delete all assistants from OpenAI
        delete_all_openai_assistants()

        return jsonify({'message': 'All data and assistants deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        logger.error(f"Failed to delete all data: {str(e)}")
        return jsonify({'message': f'Failed to delete all data: {str(e)}'}), 500