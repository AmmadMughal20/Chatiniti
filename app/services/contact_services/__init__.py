from app.db import Database

# Create a new contact
def create_contact(contact):
    db = Database()
    db.execute("""
        INSERT INTO contacts (first_name, middle_name, last_name, phone, email, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id;
    """, (contact['first_name'], contact['middle_name'], contact['last_name'], contact['phone'], contact['email']))
    new_id = db.fetchone()[0]
    db.commit()
    db.close()
    return new_id

def get_contact(id):
    db = Database()
    db.execute("SELECT id, first_name, middle_name, last_name, phone, email, created_at, updated_at FROM contacts WHERE id = %s;", (id,))
    contact = db.fetchone()
    db.close()
    db.close()
    if contact:
        return contact
    else:
        return 404
    
def get_contacts(user_id):
    db = Database()
    db.execute("SELECT con.id, con.first_name, con.middle_name, con.last_name, con.phone, con.email, con.created_at, con.updated_at FROM contacts con left join user_contact uc on con.id = uc.contact_id WHERE user_id = %s;", (user_id,))
    contact = db.fetchall()
    db.close()
    if contact:
        return contact
    else:
        return []

def update_contact(id, contact):
    db = Database()
    db.execute("""
        UPDATE contacts
        SET first_name = %s, middle_name = %s, last_name = %s, phone = %s, email = %s, updated_at = NOW()
        WHERE id = %s;
    """, (contact['first_name'], contact['middle_name'], contact['last_name'], contact['phone'], contact['email'], id))
    db.commit()
    db.close()
    return 200

# Delete a contact
def delete_contact(id):
    db = Database()
    db.execute("DELETE FROM contacts WHERE id = %s;", (id,))
    db.commit()
    db.close()
    return 200

# Add a contact to a user
def add_user_contact(contactId, user_id):
    db = Database()
    db.execute("""
        INSERT INTO user_contact (user_id, contact_id, first_name, last_name, created_at, updated_at)
        SELECT %s, id, first_name, last_name, NOW(), NOW()
        FROM contacts
        WHERE id = %s;
    """, (user_id, contactId))
    db.commit()
    db.close()
    return 200

# Get all contacts for a specific user
def get_user_contacts(user_id):
    db = Database()
    db.execute("""
        SELECT uc.contact_id, c.first_name, c.middle_name, c.last_name, c.phone, c.email
        FROM user_contact uc
        JOIN contacts c ON uc.contact_id = c.id
        WHERE uc.user_id = %s;
    """, (user_id,))
    user_contacts = db.fetchall()
    db.close()
    return user_contacts

# Remove a contact from a user
def remove_user_contact(user_id, contact_id):
    db = Database()
    db.execute("DELETE FROM user_contact WHERE user_id = %s AND contact_id = %s;", (user_id, contact_id))
    db.commit()
    db.close()
    return 200
