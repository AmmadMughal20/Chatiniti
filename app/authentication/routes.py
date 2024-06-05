from flask import redirect, render_template, request, session, url_for, flash
from app.authentication.authentication_validations import validate_age, validate_email, validate_password, validate_phone, validate_role, validate_userId, validate_userName
from app.services.account_services import authenticate_User_With_User_Id, update_password_by_token
from app.utils import generate_random_token, send_recovery_email_to_user
from . import authentication

@authentication.route('/signin', methods=['GET','POST'])
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
        if signing_in_user == None:
            flash('Wrong userId or password!', 'error')
            return render_template('login.html')
            
        elif signing_in_user.is_verified == False:
            flash('Email not verified yet!', 'error')
            return render_template('login.html')

        elif signing_in_user:
            session['user_id'] = signing_in_user.userId
            session['name'] = signing_in_user.name
            session['age'] = signing_in_user.age
            session['email'] = signing_in_user.email
            session['phone'] = signing_in_user.phoneNo
            session['roleId'] = signing_in_user.roleId
            flash('Signed in successfully!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Signed in successfully!', 'success')
            return render_template('login.html')

@authentication.route('/signup', methods=['GET', 'POST'])
def signup():
    from app.models.user_model import User
    
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

        if not new_user_id:
            flash('UserId is empty!', 'error')
            return render_template('signup.html')

        elif not new_user_name:
            flash('Username is empty!', 'error')
            return render_template('signup.html')

        elif not new_user_age:
            flash('Age is empty!', 'error')
            return render_template('signup.html')

        elif not new_user_email:
            flash('Email is empty!', 'error')
            return render_template('signup.html')

        elif not new_user_phone:
            flash('Phone is empty!', 'error')
            return render_template('signup.html')

        elif not new_user_password:
            flash('Password is empty!', 'error')
            return render_template('signup.html')

        elif not new_user_role:
            flash('Role is empty!', 'error')
            return render_template('signup.html')

        userIdValidation = validate_userId(new_user_id)

        if userIdValidation == 1:
            flash("UserId already exists!")
            return render_template('signup.html')

        userNameValidation = validate_userName(new_user_name)

        if userNameValidation == 1:
            flash("Username can not be empty!")
            return render_template('signup.html')

        elif userNameValidation == 2:
            flash("Username can not contain special characters!")
            return render_template('signup.html')

        userAgeValidation = validate_age(new_user_age)

        if userAgeValidation == 1:
            flash("Age can contain numbers only!")
            return render_template('signup.html')
            
        elif userAgeValidation == 2:
            flash("Age can not be 0 or empty!")
            return render_template('signup.html')

        userEmailValidation = validate_email(new_user_email)

        if userEmailValidation == 1:
            flash("Invalid email format!")
            return render_template('signup.html')
            
        elif userEmailValidation == 2:
            flash("Email already exists!")
            return render_template('signup.html')

        userPhoneValidation = validate_phone(new_user_phone)

        if userPhoneValidation == 1:
            flash("Phone already exists!")
            return render_template('signup.html')
            
        elif userPhoneValidation == 2:
            flash("Phone can not be empty!")
            return render_template('signup.html')
            
        elif userPhoneValidation == 3:
            flash("Invalid phone number!")
            return render_template('signup.html')

        userPasswordValidation = validate_password(new_user_password)
            
        if userPasswordValidation == 1:
            flash("Password must contain atleast 8 characters including capital, small alphabets and numeric digits!")
            return render_template('signup.html')

        userRoleValidation = validate_role(new_user_role)

        if userRoleValidation == 1:
            flash("Role doesn't exists. Enter correct role id!")
            return render_template('signup.html')

        if userIdValidation == 0 and userNameValidation == 0 and userAgeValidation == 0 and userEmailValidation == 0 and userPhoneValidation == 0 and userPasswordValidation == 0 and userRoleValidation == 0:
            User.createUser(new_user_id, new_user_name, new_user_age, new_user_email, new_user_phone, new_user_password, new_user_role)
            flash('Account created! Check your email!')
            return render_template('login.html')

@authentication.route('/verify_email/<token>')
def verify_email(token):
    from app.models.user_model import User
    
    user_data = User.getUserByToken(token)
    if user_data:
        user = User(
            userId=user_data[0],
            name=user_data[1],
            age=user_data[2],
            email=user_data[3],
            phoneNo=user_data[4],
            password=user_data[5],
            roleId=user_data[6],
            token=user_data[7],
            is_verified=False
            )
        user.updateUserToTokenVerified()
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

    from app.models.user_model import User
    
    if request.method == 'GET':
        return render_template('forgotpassword.html')
    elif request.method == 'POST':
        user_id = request.form.get('userId')
        userFound = User.getUserById(user_id)
        if userFound:
            recovery_token = generate_random_token()
            userFound.updateToken(recovery_token)
            send_recovery_email_to_user(userFound.email, recovery_token)
            flash('Recovery email sent. Please check your email.')
        else:
            flash('User ID not found.')

    return redirect(url_for('authentication.forgot_password'))

@authentication.route('/resetpassword', methods=['GET', 'POST'])
def reset_password():
    from app.models.user_model import User
    
    if request.method == 'GET':
        # Get the reset token from the URL query parameters
        token = request.args.get('token')
        if token:
            userFound = User.getUserByToken(token)
            if userFound:
                return render_template('resetpassword.html', token=token)
            else:
                flash('Invalid reset token.')
                return redirect(url_for('authentication.forgot_password'))
        else:
            flash('Reset token not provided.')
            return redirect(url_for('authentication.forgot_password'))

    elif request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        token = request.form['token']
        
        if not new_password:
            flash('New Password is required!')
            return render_template('resetpassword.html', token=token)

        if not confirm_password:
            flash('Confirm Password is required!')
            return render_template('resetpassword.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match.')
            return render_template('resetpassword.html', token=token)
        else:
            is_valid_password = validate_password(new_password)
            if is_valid_password == 1:
                flash("Password must contain atleast 8 characters including capital, small alphabets and numeric digits!")
                return render_template('resetpassword.html', token=token)
            else:
                User.update_password_by_token(token, new_password)
                flash('Password updated successfully!')
                return redirect(url_for('authentication.signIn'))