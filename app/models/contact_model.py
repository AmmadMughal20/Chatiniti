from app.db import Database


class Contact:
    def __init__(self, id, first_name, middle_name, last_name, phone, email):
        self.id = id
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.phone = phone
        self.email = email

    @staticmethod
    def create_contact(userid, first_name, middle_name, last_name, phone, email):
        db = Database()
        db.execute("""
            INSERT INTO contacts (first_name, middle_name, last_name, phone, email, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id;
        """, (first_name, middle_name, last_name, phone, email))
        new_contact_id = db.fetchone()[0]
        db.commit()

        db.execute("""INSERT INTO user_contact (user_id, contact_id, first_name, last_name, created_at, updated_at)
            SELECT %s, id, first_name, last_name, NOW(), NOW()
            FROM contacts
            WHERE id = %s;
                   """, (userid, new_contact_id))
        db.commit()
        db.close()
        return new_contact_id

    @staticmethod
    def get_contact(id):
        db = Database()
        db.execute("SELECT id, first_name, middle_name, last_name, phone, email FROM contacts WHERE id = %s;", (id,))
        contact = db.fetchone()
        db.close()
        db.close()
        if contact:
            return Contact(*contact)
        else:
            return None

    @staticmethod
    def get_contacts(user_id):
        db = Database()
        db.execute("SELECT con.id, con.first_name, con.middle_name, con.last_name, con.phone, con.email, con.created_at, con.updated_at FROM contacts con left join user_contact uc on con.id = uc.contact_id WHERE user_id = %s;", (user_id,))
        contactsArray = db.fetchall()
        db.close()
        if contactsArray:
            return contactsArray
        else:
            return []

    def update_contact(self, first_name, middle_name, last_name, phone, email):
        db = Database()
        db.execute("""
            UPDATE contacts
            SET first_name = %s, middle_name = %s, last_name = %s, phone = %s, email = %s, updated_at = NOW()
            WHERE id = %s;
        """, (first_name, middle_name, last_name, phone, email, self.id))
        db.commit()
        db.close()
    
    @staticmethod
    def delete_contact(id):
        db = Database()
        db.execute("DELETE FROM contacts WHERE id = %s;", (id,))
        db.commit()
        db.close()
    
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
    
    @staticmethod
    def remove_user_contact(user_id, contact_id):
        db = Database()
        db.execute("DELETE FROM user_contact WHERE user_id = %s AND contact_id = %s;", (user_id, contact_id))
        db.commit()
        db.close()