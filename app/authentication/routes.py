from flask import redirect, render_template, request, session, url_for, flash

from app.authentication.authentication_validations import validate_age, validate_phone, validate_role, validate_userId, validate_userName
from app.services.account_services import authenticate_User_With_User_Id, update_password_by_token
from app.services.account_services.uservalidations import validate_email, validate_password
from app.services.user_services import createUser, getUserById, getUserByToken, updateToken, updateUserToTokenVerified
from app.utils import generate_random_token, send_recovery_email_to_user
from . import authentication

@authentication.route('/signin', methods=['GET','POST'])
def signIn():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':

        userId = request.form['userId']
        password = request.form['password']

        responseObject = {}

        if userId != '':
            userAuthentication = authenticate_User_With_User_Id(userId, password)

            if userAuthentication == 1:
                responseObject["status"] = 401
                responseObject["message"] = f"UserId is required!"

            elif userAuthentication == 2:
                responseObject["status"] = 402
                responseObject["message"] = f"Password is required!"

            elif userAuthentication == 3:
                responseObject["status"] = 403
                responseObject["message"] = f"Wrong userId or password!"
            elif userAuthentication == 4:
                responseObject["status"] = 404
                responseObject["message"] = f"Email not verified yet!"
            else:
                session['user_id'] = userAuthentication[0]
                session['name'] = userAuthentication[1]
                session['age'] = userAuthentication[2]
                session['email'] = userAuthentication[3]
                session['phone'] = userAuthentication[4]
                session['roleId'] = userAuthentication[5]
                responseObject["status"] = 200
                responseObject["message"] = f"Data received successfully!"
                responseObject["data"] = userAuthentication
        else:
            responseObject["status"] = 404
            responseObject["message"] = f"UserId is required!"

        if responseObject["status"] == 200:
            return redirect(url_for('main.index'))
        else:
            return render_template('login.html', error=responseObject)

@authentication.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        new_user_id = request.form['userId']
        new_user_name = request.form['name']
        new_user_age = request.form['age']
        new_user_email = request.form['email']
        new_user_phone = request.form['phone']
        new_user_password = request.form['password']
        new_user_role = request.form['roleId']
        responseObject = {}

        userIdValidation = validate_userId(new_user_id)

        if userIdValidation == 1:
            responseObject["status"] = 401
            responseObject["message"] = f"UserId already exists!"

        userNameValidation = validate_userName(new_user_name)

        if userNameValidation == 1:
            responseObject["status"] = 402
            responseObject["message"] = f"Username can not be empty!"
        elif userNameValidation == 2:
            responseObject["status"] = 403
            responseObject["message"] = f"Username can not contain special characters!"

        userAgeValidation = validate_age(new_user_age)

        if userAgeValidation == 1:
            responseObject["status"] = 404
            responseObject["message"] = f"Age can contain numbers only!"
        elif userAgeValidation == 2:
            responseObject["status"] = 405
            responseObject["message"] = f"Age can not be 0 or empty!"

        userEmailValidation = validate_email(new_user_email)

        if userEmailValidation == 1:
            responseObject["status"] = 406
            responseObject["message"] = f"Email already exists!"
        elif userEmailValidation == 2:
            responseObject["status"] = 407
            responseObject["message"] = f"Email can not be empty!"
        elif userEmailValidation == 3:
            responseObject["status"] = 408
            responseObject["message"] = f"Invalid email format!"

        userPhoneValidation = validate_phone(new_user_phone)

        if userPhoneValidation == 1:
            responseObject["status"] = 409
            responseObject["message"] = f"Phone already exists!"
        elif userPhoneValidation == 2:
            responseObject["status"] = 410
            responseObject["message"] = f"Phone can not be empty!"
        elif userPhoneValidation == 3:
            responseObject["status"] = 411
            responseObject["message"] = f"Invalid phone number!"

        userPasswordValidation = validate_password(new_user_password)

        if userPasswordValidation == 1:
            responseObject["status"] = 412
            responseObject["message"] = f"Phone can not be empty!"
        elif userPasswordValidation == 2:
            responseObject["status"] = 413
            responseObject["message"] = f"Password must contain atleast 8 characters including capital, small alphabets and numeric digits!"

        userRoleValidation = validate_role(new_user_role)

        if userRoleValidation == 1:
            responseObject["status"] = 414
            responseObject["message"] = f"Role doesn't exists. Enter correct role id!"

        if userIdValidation == 0 and userNameValidation == 0 and userAgeValidation == 0 and userEmailValidation == 0 and userPhoneValidation == 0 and userPasswordValidation == 0 and userRoleValidation == 0:
            return createUser(new_user_id, new_user_name, new_user_age, new_user_email, new_user_phone, new_user_password, new_user_role)

        if responseObject["status"] != 200:
            return render_template('signup.html', error=responseObject["message"])

@authentication.route('/verify_email/<token>')
def verify_email(token):

    # Fetch the user associated with the token
    user = getUserByToken(token)

    if user:
        updateUserToTokenVerified(user[0])
        flash('Your email has been verified successfully.')
        return redirect(url_for('authentication.signIn'))
    else:
        flash('Invalid verification token.')
        return redirect(url_for('authentication.signIn'))

@authentication.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('authentication.signIn'))

@authentication.route('/forgotpassword', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgotpassword.html')
    elif request.method == 'POST':
        user_id = request.form.get('userId')
        userFound = getUserById(user_id)
        if userFound:
            recovery_token = generate_random_token()
            updateToken(user_id, recovery_token)
            send_recovery_email_to_user(userFound[3], recovery_token)
            flash('Recovery email sent. Please check your email.')
        else:
            flash('User ID not found.')

    return redirect(url_for('authentication.forgot_password'))

@authentication.route('/resetpassword', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        # Get the reset token from the URL query parameters
        token = request.args.get('token')
        if token:
            userFound = getUserByToken(token)
            if userFound:
                return render_template('resetpassword.html', token=token)
            else:
                flash('Invalid reset token.')
                return redirect(url_for('forgot_password'))
        else:
            print('Reset token not provided.')
            flash('Reset token not provided.')
            return redirect(url_for('forgot_password'))

    elif request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        token = request.form['token']
        if new_password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('reset_password', token=token))
        updatingPassword = update_password_by_token(token, new_password)
        if updatingPassword == 1:
            print('Password reset successfully.')
            flash('Password reset successfully.')
            return redirect(url_for('authentication.signIn'))
        elif updatingPassword == 2:
            flash('Invalid reset token.')
            return redirect(url_for('authentication.forgot_password'))
        elif updatingPassword == 3:
            print('Invalid Password!')
            flash('Invalid Password!')
            return redirect(url_for('authentication.forgot_password'))
