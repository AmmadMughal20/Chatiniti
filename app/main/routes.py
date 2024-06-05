from flask import jsonify, redirect, render_template, g, json, session, url_for, request

from app.models.user_model import User
from app.services.chat_services import get_conversations_and_participants, get_latest_conversation_with_participents, get_messages_by_conversation
from app.services.contact_services import add_user_contact, create_contact, delete_contact, get_contacts, remove_user_contact, update_contact
from app.services.conversation_participents_servies import addReceiverInConversationParticipents, createNewConversationPartcipent
from app.services.conversation_services import create_new_conversation
from app.services.friendship_services import get_friends, saveNewFrinedShip, updateFriendShipStatus
# from app.services.user_services import getAllUsers, getUserById
from app.utils import find_element, find_latest_conversations, get_conversation_id
from . import main

@main.route('/')
def index(name='', phone=''):
    name = name
    phone=phone
    return render_template('common/index.html', name=name, phone=phone)

@main.route('/about')
def about():
    return render_template('common/about.html')

@main.route('/contacts', defaults={'contact_id': None}, methods=['GET', 'POST', 'PUT'])
@main.route('/contacts/<int:contact_id>', methods=['PUT', 'DELETE'])
def contacts(contact_id=None):
    userIdToGetChats = session.get('user_id')

    if request.method == 'POST':
        if 'user_id' in session:
            firstName = request.form['first_name']
            middleName = request.form.get('middle_name', '')
            lastName = request.form['last_name']
            phone = request.form['phone']
            email = request.form['email']
            contact = {
                "first_name": firstName,
                "last_name": lastName,
                "middle_name": middleName,
                "phone": phone,
                "email": email
            }
            newContactId = create_contact(contact)
            saveContactInUserTable = add_user_contact(newContactId, userIdToGetChats)
            return redirect(url_for('main.contacts'))

    if request.method == 'PUT':
        if 'user_id' not in session:
            return jsonify({'error': 'User not authenticated'}), 401
        contact_data = {
            "first_name": request.form['first_name'],
            "middle_name": request.form.get('middle_name', ''),
            "last_name": request.form['last_name'],
            "phone": request.form['phone'],
            "email": request.form['email']
        }

        update = update_contact(contact_id, contact_data)
        remove_user_contact(userIdToGetChats, contact_id)
        add_user_contact(contact_id, userIdToGetChats)
        contactsToDisplay = get_contacts(userIdToGetChats)
        return render_template('common/contacts.html', contacts=contactsToDisplay)

    if request.method == 'DELETE':
        if 'user_id' in session:
            removeContactResult = remove_user_contact(userIdToGetChats, contact_id)
            deleteContactResult = delete_contact(contact_id)
            if removeContactResult == 200 and deleteContactResult == 200:
                return jsonify({'message': 'Contact deleted successfully'}), 200
            else:
                return jsonify({'error': 'Failed to delete contact'}), 500
        return jsonify({'error': 'User not authenticated'}), 401

    if request.method == 'GET':
        if 'user_id' in session:
            contactsToDisplay = get_contacts(userIdToGetChats)
        else:
            contactsToDisplay = []
        return render_template('common/contacts.html', contacts=contactsToDisplay)

@main.route('/users', methods=['GET', 'POST'])
def users():
    users = []

    if 'user_id' in session:
        logged_in_user_id = session['user_id']

        if request.method == 'GET':
            usersArray = getAllUsers(logged_in_user_id)
            for row in usersArray:
                if row[0] != logged_in_user_id:
                    user = {
                        "userId": row[0],
                        "name": row[1],
                        "age": row[2],
                        "email": row[3],
                        "phone": row[4],
                        "friendship_status": row[5] if row[5] else 'None',
                        "friendship_direction": row[6]
                    }
                    users.append(user)

    return render_template('common/users.html', users=users)

@main.route('/chat', defaults={'recepent_id': None}, methods=['GET'])
@main.route('/chat/<recepent_id>', methods=['GET','PUT', 'DELETE'])
def chat(recepent_id=None):
    messagesconverted = []
    messages = []
    friends = []
    receiver = None
    contactName = None
    latestConversation = None
    conversation_id = None
    if 'user_id' in session:
        user_id = session['user_id']
        friends = get_friends(user_id)   
        conversations = get_conversations_and_participants(user_id)
        if recepent_id:
            receiver = User.getUserById(recepent_id)
            conversation_of_recepient = find_element(conversations, "user_id2", recepent_id)
            conversation_id = conversation_of_recepient["conversation_id"]
            if conversation_id:
                messages = conversation_of_recepient["messages"]
            else:
                conversation_id = create_new_conversation(user_id, recepent_id)
                createNewConversationPartcipent(user_id, conversation_id)
                addReceiverInConversationParticipents(recepent_id, conversation_id)
        else:
            latestConversation = find_latest_conversations(conversations)
            if latestConversation:
                conversation_id = latestConversation['conversation_id']
                recepent_id = latestConversation['user_id2']
                receiver = User.getUserById(recepent_id)
                messages = latestConversation["messages"]
        for row in messages:
            if(row["sender_id"] == user_id):
                message = {
                    "sender": "You",
                    "message": row["message"],
                    "sendingTime": row["sending_time"],
                    "deliveredTime": row["delivered_time"],
                    "readTime": row["read_time"],
                    "createdAt": row["created_at"]
                }
            else:
                message = {
                    "sender": row["sender_id"],
                    "message": row["message"],
                    "sendingTime": row["sending_time"],
                    "deliveredTime": row["delivered_time"],
                    "readTime": row["read_time"],
                    "createdAt": row["created_at"]
                }
            messagesconverted.append(message)
        if receiver:
            contactName = receiver[1] + '  ' +receiver[0]
                    
    return render_template('common/chat.html', contacts=friends, chat_history=messagesconverted, contactName=contactName, conversation_id=conversation_id)

@main.route('/addFriend', methods=['POST'])
def addFriend():
    data = request.get_json()
    if session:
        user_id1 = session['user_id']  # Assuming the logged-in user's ID is 1; replace with actual logic
        user_id2 = data['user_id2']

    if user_id1 == user_id2:
        return jsonify({'success': False, 'message': "You can't be friends with yourself"}), 400

    result = saveNewFrinedShip(user_id1, user_id2)
    if result:
        return redirect(url_for('main.users'))
    else:
        return jsonify({'success': False, 'message': 'Friend request already exists'}), 400

@main.route('/acceptFriend', methods=['POST'])
def acceptFriend():
    data = request.get_json()
    user_id1 = session['user_id']
    user_id2 = data['user_id']
    updateFriendShipStatus(user_id1, user_id2, 'accepted')
    return jsonify({'success': True, 'message': 'Request accepted'}), 200

@main.route('/rejectFriend', methods=['POST'])
def rejectFriend():
    data = request.get_json()
    user_id1 = session['user_id']
    user_id2 = data['user_id']
    updateFriendShipStatus( user_id1, user_id2, 'rejected')
    return jsonify({'success': True, 'message': 'Request rejected'}), 200

