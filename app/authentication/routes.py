from flask import redirect, render_template, request, session, url_for, flash
from app.authentication.authentication_validations import validate_age, validate_email, validate_password, validate_phone, validate_role, validate_userId, validate_userName
from app.utils import generate_random_token, send_recovery_email_to_user
from . import authentication

@authentication.route('/signin', methods=['GET', 'POST'])
def signIn():
    from app.models.user_model import User
    
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        userId = request.form.get('userId')
        password = request.form.get('password')

        if not userId:
            flash('UserId is empty!', 'error')
            return render_template('login.html')

        if not password:
            flash('Password is empty!', 'error')
            return render_template('login.html')

        signing_in_user = User.signIn(userId, password)
        if signing_in_user is None:
            flash('Wrong userId or password!', 'error')
            return render_template('login.html')
            
        if not signing_in_user.is_verified:
            flash('Email not verified yet!', 'error')
            return render_template('login.html')

        session['user_id'] = signing_in_user.userId
        session['name'] = signing_in_user.name
        session['age'] = signing_in_user.age
        session['email'] = signing_in_user.email
        session['phone'] = signing_in_user.phoneNo
        session['roleId'] = signing_in_user.roleId
        flash('Signed in successfully!', 'success')
        return redirect(url_for('main.index'))

@authentication.route('/signup', methods=['GET', 'POST'])
def signup():
    from app.models.user_model import User
    
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        new_user_id = request.form['userId']
        new_user_name = request.form['name']
        new_user_age = request.form['age']
        new_user_email = request.form['email']
        new_user_phone = request.form['phone']
        new_user_password = request.form['password']
        new_user_role = request.form['roleId']

        if not new_user_id:
            flash('UserId is empty!', 'error')
            return render_template('signup.html')

        if not new_user_name:
            flash('Username is empty!', 'error')
            return render_template('signup.html')

        if not new_user_age:
            flash('Age is empty!', 'error')
            return render_template('signup.html')

        if not new_user_email:
            flash('Email is empty!', 'error')
            return render_template('signup.html')

        if not new_user_phone:
            flash('Phone is empty!', 'error')
            return render_template('signup.html')

        if not new_user_password:
            flash('Password is empty!', 'error')
            return render_template('signup.html')

        if not new_user_role:
            flash('Role is empty!', 'error')
            return render_template('signup.html')

        userIdValidation = validate_userId(new_user_id)
        if userIdValidation == 1:
            flash("UserId already exists!", 'error')
            return render_template('signup.html')

        userNameValidation = validate_userName(new_user_name)
        if userNameValidation == 1:
            flash("Username cannot be empty!", 'error')
            return render_template('signup.html')

        if userNameValidation == 2:
            flash("Username cannot contain special characters!", 'error')
            return render_template('signup.html')

        userAgeValidation = validate_age(new_user_age)
        if userAgeValidation == 1:
            flash("Age can contain numbers only!", 'error')
            return render_template('signup.html')
            
        if userAgeValidation == 2:
            flash("Age cannot be 0 or empty!", 'error')
            return render_template('signup.html')

        userEmailValidation = validate_email(new_user_email)
        if userEmailValidation == 1:
            flash("Invalid email format!", 'error')
            return render_template('signup.html')
            
        if userEmailValidation == 2:
            flash("Email already exists!", 'error')
            return render_template('signup.html')

        userPhoneValidation = validate_phone(new_user_phone)
        if userPhoneValidation == 1:
            flash("Phone already exists!", 'error')
            return render_template('signup.html')
            
        if userPhoneValidation == 2:
            flash("Phone cannot be empty!", 'error')
            return render_template('signup.html')
            
        if userPhoneValidation == 3:
            flash("Invalid phone number!", 'error')
            return render_template('signup.html')

        userPasswordValidation = validate_password(new_user_password)
        if userPasswordValidation == 1:
            flash("Password must contain at least 8 characters including capital, small alphabets, and numeric digits!", 'error')
            return render_template('signup.html')

        userRoleValidation = validate_role(new_user_role)
        if userRoleValidation == 1:
            flash("Role doesn't exist. Enter correct role id!", 'error')
            return render_template('signup.html')

        if all(v == 0 for v in [userIdValidation, userNameValidation, userAgeValidation, userEmailValidation, userPhoneValidation, userPasswordValidation, userRoleValidation]):
            User.createUser(new_user_id, new_user_name, new_user_age, new_user_email, new_user_phone, new_user_password, new_user_role)
            flash('Account created! Check your email!', 'success')
            return render_template('login.html')

@authentication.route('/verify_email/<token>')
def verify_email(token):
    from app.models.user_model import User
    
    user_data = User.getUserByToken(token)
    if user_data:
        user_data.updateUserToTokenVerified()
        flash('Your email has been verified successfully.', 'success')
        return redirect(url_for('authentication.signIn'))
    else:
        flash('Invalid verification token.', 'error')
        return redirect(url_for('authentication.signIn'))

@authentication.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('authentication.signIn'))

@authentication.route('/forgotpassword', methods=['GET', 'POST'])
def forgot_password():
    from app.models.user_model import User
    
    if request.method == 'GET':
        return render_template('forgotpassword.html')
    elif request.method == 'POST':
        user_id = request.form.get('userId')
        userFound = User.getUserById(user_id)
        if userFound:
            recovery_token = generate_random_token()
            User.updateToken(userFound.userId, recovery_token)
            send_recovery_email_to_user(userFound.email, recovery_token)
            flash('Recovery email sent. Please check your email.', 'success')
        else:
            flash('User ID not found.', 'error')

    return redirect(url_for('authentication.forgot_password'))

@authentication.route('/resetpassword', methods=['GET', 'POST'])
def reset_password():
    from app.models.user_model import User
    
    if request.method == 'GET':
        token = request.args.get('token')
        if token:
            userFound = User.getUserByToken(token)
            if userFound:
                return render_template('resetpassword.html', token=token)
            else:
                flash('Invalid reset token.', 'error')
                return redirect(url_for('authentication.forgot_password'))
        else:
            flash('Reset token not provided.', 'error')
            return redirect(url_for('authentication.forgot_password'))

    elif request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        token = request.form['token']
        
        if not new_password:
            flash('New Password is required!', 'error')
            return render_template('resetpassword.html', token=token)

        if not confirm_password:
            flash('Confirm Password is required!', 'error')
            return render_template('resetpassword.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('resetpassword.html', token=token)
        else:
            is_valid_password = validate_password(new_password)
            if is_valid_password == 1:
                flash("Password must contain at least 8 characters including capital, small alphabets, and numeric digits!", 'error')
                return render_template('resetpassword.html', token=token)
            else:
                User.update_password_by_token(token, new_password)
                flash('Password updated successfully!', 'success')
                return redirect(url_for('authentication.signIn'))
